# Group Research: subset-b-004310

This grouped report covers the CAN driver sources assigned to `subset-b-004310`. Each section is delimited so it can be split into the required source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd_core.c

## Purpose
`kvaser_pciefd_core.c` is the main PCI driver for Kvaser PCIe CAN FD adapters. It binds supported Kvaser PCI device IDs, maps the board register BAR, discovers firmware/channel properties, allocates DMA receive buffers, creates one SocketCAN netdev per CAN channel, handles transmit/receive/error/status packets, and tears everything down at remove time.

## Important APIs, Types, And Functions
- Registers and packet fields are described with `KVASER_PCIEFD_*` macros for the system ID block, shared receive buffer, KCAN channel blocks, DMA mapping registers, interrupt masks, and packet encodings.
- Board-family data is modeled by static `kvaser_pciefd_address_offset`, `kvaser_pciefd_irq_mask`, `kvaser_pciefd_dev_ops`, and `kvaser_pciefd_driver_data` instances for Altera, SmartFusion2, and Xilinx variants.
- `kvaser_pciefd_rx_packet` and `kvaser_pciefd_tx_packet` are the wire-format packet helpers used for DMA receive parsing and TX FIFO writes.
- `kvaser_pciefd_id_table` maps many Kvaser vendor/device IDs to the correct address, IRQ, and DMA-map operations.
- Netdev entry points are `kvaser_pciefd_open()`, `kvaser_pciefd_stop()`, and `kvaser_pciefd_start_xmit()`.
- CAN core hooks include `kvaser_pciefd_set_nominal_bittiming()`, `kvaser_pciefd_set_data_bittiming()`, `kvaser_pciefd_set_mode()`, and `kvaser_pciefd_get_berr_counter()`.
- PCI lifecycle is handled by `kvaser_pciefd_probe()` and `kvaser_pciefd_remove()`, registered through `module_pci_driver()`.

## Control Flow
Probe allocates a devlink instance, enables PCI, requests regions, maps BAR0, reads system ID information, verifies DMA capability, configures DMA buffers, creates CAN controllers, allocates an IRQ vector, requests the shared IRQ, enables SRB and PCI-level interrupts, rearms both DMA buffers, registers all candevs, and finally registers devlink.

Each CAN netdev open resets TX/ACK indices, calls `open_candev()`, and performs `kvaser_pciefd_bus_on()`. Bus-on waits for flush completion, clears/arms KCAN interrupts, exits reset mode, waits for start completion, configures mode bits, sets state to `CAN_STATE_ERROR_ACTIVE`, wakes the queue, and clears cached error counters. Stop performs a flush, disables channel interrupts, deletes the BEC poll timer, sets the state to stopped, resets queue accounting, and calls `close_candev()`.

TX builds a KCAN packet from a CAN or CAN FD skb, assigns a sequence slot from `tx_idx`, saves an echo skb, updates BQL, writes the packet header/data to the channel FIFO, and uses the `FIFO_LAST` register to complete the hardware packet. ACK packets later validate the echo sequence, timestamp the skb, call `can_get_echo_skb()`, advance `ack_idx` with release semantics, update counters, and wake BQL in bulk after the receive DMA buffer is processed.

Receive interrupts come through the shared PCI interrupt. The handler masks the board interrupt source, dispatches SRB packet-done interrupts to `kvaser_pciefd_receive_irq()`, processes TX-side channel IRQs, then reenables the board mask. `kvaser_pciefd_receive_irq()` reads either DMA buffer, parses a packet list until the zero-size terminator, dispatches by KCAN packet type, reports DMA overflow/underflow errors, and rearms the consumed DMA buffer.

Status/error control flow is tied to completions. Status packets complete `flush_comp` or `start_comp` when reset/flush/bus-on state transitions are observed. Error packets and status responses update CAN state, deliver CAN error skbs when requested, track bus-off, and use a timer to limit high-rate error generation after `KVASER_PCIEFD_MAX_ERR_REP` reports.

## State And Persistence
Runtime state is in `struct kvaser_pciefd` and one `struct kvaser_pciefd_can` per channel. Persistent hardware state includes mapped register values, DMA buffer addresses programmed into variant-specific SerDes registers, KCAN mode/bittiming registers, and devlink firmware version information. Driver-owned volatile state includes `tx_idx`, `ack_idx`, `cmd_seq`, `ioc`, `bec`, completions, BEC poll timer, and per-buffer DMA memory. No on-disk state is stored.

## Dependencies And Integration Points
The file depends on the Linux PCI, DMA, netdevice, SocketCAN, ethtool, timer, completion, and devlink facilities. It integrates with `kvaser_pciefd.h` for private structures and with `kvaser_pciefd_devlink.c` through `kvaser_pciefd_devlink_ops`, `kvaser_pciefd_devlink_port_register()`, and `kvaser_pciefd_devlink_port_unregister()`. It exports no symbols; the PCI module is the integration boundary.

## Risks And Edge Cases
- Several probe error paths call `kvaser_pciefd_teardown_can_ctrls()` after partial setup; correctness depends on `pcie->can[i]` being NULL for uncreated channels and on devlink port registration being paired only for initialized channels.
- `dma_set_mask_and_coherent()` return value is ignored in `kvaser_pciefd_setup_dma()`, so systems unable to satisfy a 64-bit mask may proceed unexpectedly.
- RX packet parsing trusts packet sizes enough to index the 4 KiB DMA buffer; the final size check catches mismatch but happens after field reads.
- TX queue accounting relies on correct ACK sequencing; out-of-order or missing ACKs can leave echo slots occupied and queue progress dependent on later hardware behavior.
- Error-rate throttling disables EPEN after too many error reports and relies on the timer/status request path to reenable it.
- Hardware timestamp conversion multiplies `timestamp * 1000` before division; very large timestamp counters should be reviewed for overflow expectations.

## Test Signals
Useful signals include PCI probe/remove on each supported board family, one channel and multi-channel registration, CAN 2.0 and CAN FD TX/RX, loopback/self reception where available, bus-off and restart behavior, BERR reporting on/off, one-shot NACK handling, DMA overflow/underflow fault logging, IRQ sharing/MSI behavior, ethtool physical ID LED toggling, hardware timestamp reporting, and devlink firmware version visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd_devlink.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd_devlink.c

## Purpose
This file provides the devlink integration for the Kvaser PCIe FD driver. It reports firmware version information and binds each SocketCAN netdev to a physical devlink port.

## Important APIs, Types, And Functions
- `kvaser_pciefd_devlink_info_get()` reads `struct kvaser_pciefd::fw_version` and reports `DEVLINK_INFO_VERSION_GENERIC_FW` when a nonzero major version exists.
- `kvaser_pciefd_devlink_ops` exposes `.info_get`.
- `kvaser_pciefd_devlink_port_register()` initializes `devlink_port_attrs` with `DEVLINK_PORT_FLAVOUR_PHYSICAL`, registers the port at the CAN device `dev_port`, and attaches it to the netdev with `SET_NETDEV_DEVLINK_PORT()`.
- `kvaser_pciefd_devlink_port_unregister()` unregisters the previously registered port.

## Control Flow
Core probe allocates the devlink object before hardware setup. Once each channel netdev is allocated and populated, `kvaser_pciefd_devlink_port_register()` is called before candev registration. After all netdevs are registered, the core registers devlink. Removal unregisters each per-channel devlink port before freeing its candev, then unregisters and frees the devlink object.

## State And Persistence
The only state owned here is the `devlink_port` embedded in `struct kvaser_pciefd_can`. Firmware version fields are populated in the core file from system ID registers and are only reported through devlink. There is no persistent storage.

## Dependencies And Integration Points
The file depends on `<net/devlink.h>`, netdevice helpers, and Kvaser private structures from `kvaser_pciefd.h`. It is tightly coupled to the core file: core owns the devlink allocation and channel lifetime, while this file owns port registration and version reporting policy.

## Risks And Edge Cases
- Firmware version reporting is suppressed when major version is zero, which may hide valid `0.x.y` firmware if such versions exist.
- The version buffer is sized for `xxx.xxx.xxxxx`; larger field widths would truncate via `snprintf()`, though source fields are small integer types.
- Port registration failure aborts channel setup; the core path must free any candevs already allocated and unregister any ports already registered.

## Test Signals
Check `devlink dev info` for firmware version after probe, `devlink port show` for one physical port per CAN channel, netdev-to-devlink port association, and remove/reprobe without stale devlink ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/kvaser_pciefd/kvaser_pciefd_devlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/Kconfig

## Purpose
This Kconfig file defines build-time selection for the Bosch M_CAN common framework and its PCI, platform MMIO, and TCAN4x5x SPI integrations.

## Important APIs, Types, And Functions
- `menuconfig CAN_M_CAN` is the parent tristate and selects `CAN_RX_OFFLOAD`.
- `CAN_M_CAN_PCI` depends on `PCI` and enables the generic PCI bus wrapper.
- `CAN_M_CAN_PLATFORM` depends on `HAS_IOMEM` and enables the IO-mapped platform wrapper.
- `CAN_M_CAN_TCAN4X5X` depends on `SPI`, selects `REGMAP_SPI`, and enables the Texas Instruments TCAN4x5x peripheral wrapper.

## Control Flow
When the parent option is disabled, all child drivers are hidden. When enabled, child options determine which bus glue modules are compiled alongside or on top of `m_can.o`.

## State And Persistence
Kconfig state is build configuration only. It controls which modules or built-in objects exist; it has no runtime state.

## Dependencies And Integration Points
The parent option integrates with SocketCAN and specifically selects RX offload because peripheral variants use `can_rx_offload`. The TCAN option pulls in regmap SPI support needed by `tcan4x5x-regmap.c`.

## Risks And Edge Cases
- Selecting only `CAN_M_CAN` builds the common core without a concrete bus device unless another wrapper is enabled.
- `CAN_M_CAN_PLATFORM` relies on device-tree or firmware properties at runtime despite only declaring `HAS_IOMEM` at build time.
- `CAN_M_CAN_TCAN4X5X` requires SPI IRQ, clock, GPIO, regulator, and MRAM properties at runtime beyond the Kconfig dependency.

## Test Signals
Check that each selected symbol produces the expected object/module, that `CAN_RX_OFFLOAD` and `REGMAP_SPI` are selected where needed, and that allyesconfig/allmodconfig builds cover all combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/Makefile

## Purpose
This Makefile maps the M_CAN Kconfig symbols to build artifacts.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CAN_M_CAN) += m_can.o` builds the common class driver.
- `obj-$(CONFIG_CAN_M_CAN_PCI) += m_can_pci.o` builds the PCI wrapper.
- `obj-$(CONFIG_CAN_M_CAN_PLATFORM) += m_can_platform.o` builds the platform/MMIO wrapper.
- `obj-$(CONFIG_CAN_M_CAN_TCAN4X5X) += tcan4x5x.o` builds a composite TCAN module from `tcan4x5x-core.o` and `tcan4x5x-regmap.o`.

## Control Flow
Kbuild includes the listed objects according to resolved Kconfig values. The TCAN target is a multi-object module, so both core probe logic and SPI regmap transport are linked together.

## State And Persistence
There is no runtime state. The file defines build composition.

## Dependencies And Integration Points
The common `m_can.o` exports class APIs consumed by all wrappers. The TCAN module depends on both `tcan4x5x-core.c` and `tcan4x5x-regmap.c` and on the Kconfig-selected regmap SPI support.

## Risks And Edge Cases
- Building a wrapper without compatible exported symbols from `m_can.o` would fail at link/modpost time, so symbol visibility in `m_can.c` is part of the build contract.
- The empty initial `tcan4x5x-objs :=` is harmless but means later object additions define the full composite module.

## Test Signals
Verify `make M=drivers/net/can/m_can` for built-in and module configs, and check that `tcan4x5x.ko` contains both TCAN object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can.c

## Purpose
`m_can.c` is the shared SocketCAN class driver for Bosch M_CAN controller IP. It provides the common netdev lifecycle, register programming, Message RAM layout handling, RX/TX processing, CAN state/error reporting, ethtool coalescing, power-management helpers, and exported class registration functions used by platform, PCI, and SPI peripheral wrappers.

## Important APIs, Types, And Functions
- Register definitions and bit masks cover the M_CAN core release, CCCR, bit timing, interrupt, FIFO, Message RAM, timestamp, error counter, and protocol status registers.
- `m_can_read()`, `m_can_write()`, `m_can_fifo_read()`, `m_can_fifo_write()`, and `m_can_txe_fifo_read()` dispatch through `struct m_can_ops`, allowing the common driver to work with MMIO or SPI/regmap transports.
- RX path functions include `m_can_read_fifo()`, `m_can_do_rx_poll()`, `m_can_rx_handler()`, and `m_can_poll()`.
- Error handling is split across `m_can_handle_lost_msg()`, `m_can_handle_lec_err()`, `m_can_handle_state_change()`, `m_can_handle_state_errors()`, `m_can_handle_protocol_error()`, and `m_can_handle_bus_errors()`.
- TX path functions include `m_can_start_tx()`, `m_can_tx_handler()`, `m_can_start_xmit()`, `m_can_echo_tx_event()`, `m_can_finish_tx()`, and peripheral workqueue helpers.
- Configuration functions include `m_can_cccr_update_bits()`, `m_can_config_enable()`, `m_can_init_ram()`, `m_can_set_bittiming()`, `m_can_chip_config()`, `m_can_start()`, and `m_can_stop()`.
- Exported APIs are `m_can_check_mram_cfg()`, `m_can_class_get_clocks()`, `m_can_class_allocate_dev()`, `m_can_class_free_dev()`, `m_can_class_register()`, `m_can_class_unregister()`, `m_can_class_suspend()`, and `m_can_class_resume()`.

## Control Flow
Wrappers allocate an `m_can_classdev` with `m_can_class_allocate_dev()`, fill clock/IRQ/transport fields, then call `m_can_class_register()`. Registration computes a safe TX FIFO size, gets reset control, powers/clocks the controller, optionally adds RX offload for peripherals, sets up an hrtimer for polling or interrupt coalescing, probes the core release, initializes CAN capabilities, registers the candev, reads transceiver configuration, and powers the controller back down until open.

Open powers the PHY, resumes clocks, deasserts reset, opens the candev, enables NAPI or peripheral RX offload, requests the interrupt, runs `m_can_start()`, and starts the queue. Start programs Message RAM, filters, TX/RX FIFOs, CCCR modes, bit timing, timestamps, and interrupts, then clears `CCCR_INIT` to enter normal mode.

RX processing is interrupt or hrtimer driven. The interrupt handler reads and acknowledges `M_CAN_IR`, handles edge-triggered wrappers by looping until IR is observed clear, updates coalescing, dispatches RX/error work to NAPI for non-peripherals or directly to the offload path for peripherals, and handles TX completion. NAPI combines latched `irqstatus` with current IR and calls `m_can_rx_handler()`.

TX first reserves a logical in-flight slot under `tx_handling_spinlock`. Version 3.0 uses a single TX buffer and `IR_TC`; newer versions use TX FIFO/queue plus TX event FIFO message markers. Peripheral chips queue TX work to an ordered workqueue and may batch `TXBAR` submission until `netdev_xmit_more()` or the configured coalescing threshold.

Suspend stops or partially leaves the chip running for wake-capable devices, updates pinctrl state, clocks down the device, and marks state sleeping. Resume restores pinctrl, clocks, interrupts, optional wrapper init, controller state, and queue attachment.

## State And Persistence
Runtime state lives in `struct m_can_classdev`: CAN core state, NAPI/offload state, active interrupt mask cache, coalescing values, TX FIFO indices and in-flight count, workqueue operations, MRAM layout, reset/clock handles, transceiver, hrtimer, and wake pinctrl. Message RAM contents are initialized at start and then used as hardware queues. There is no on-disk persistence.

## Dependencies And Integration Points
This file depends on the SocketCAN core, CAN FD helpers, RX offload, NAPI, hrtimers, ethtool, runtime PM, reset, clocks, PHY, pinctrl, fwnode/device-tree properties, and wrapper-provided `m_can_ops`. The integration contract is that wrappers must provide valid register/FIFO operations, `bosch,mram-cfg`, clock frequency, IRQ/polling mode, and peripheral flags before registration.

## Risks And Edge Cases
- `m_can_cccr_update_bits()` refuses many configuration writes when not in init mode; wrappers that call class APIs with bad power/reset sequencing can fail with `-EBUSY`.
- Message RAM configuration is firmware-supplied; bad offsets/counts can corrupt hardware queues unless wrapper-specific size checks such as `m_can_check_mram_cfg()` are used.
- TX accounting depends on TX event FIFO message markers matching echo skb slots.
- Peripheral chips perform bus access from a workqueue, so stop/close paths must destroy the workqueue after TX operations are quiesced.
- Coalescing settings are only accepted while stopped and must stay within RX FIFO/TX FIFO/TX event FIFO capacities.
- `m_can_start()` ignores the return value of `m_can_start()` in `m_can_set_mode()` before waking the queue, so restart error propagation is limited there.
- Edge-triggered IRQ wrappers require the IR drain loop to avoid missing a later edge.

## Test Signals
Use loopback, listen-only, one-shot, CAN FD, CAN FD non-ISO, BERR reporting, bus-off/restart, interrupt coalescing, polling mode, RX overflow, protocol error injection, suspend/resume with and without wakeup, runtime PM, and TX FIFO saturation tests. Also validate that MRAM layout errors are rejected and that ethtool coalescing rejects invalid active or out-of-range settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can.h

## Purpose
`m_can.h` defines the common data structures and exported interfaces for the Bosch M_CAN class driver and its bus-specific wrappers.

## Important APIs, Types, And Functions
- `enum m_can_lec_type` names M_CAN last-error-code values used by common error reporting.
- `enum m_can_mram_cfg` indexes Message RAM regions: standard filters, extended filters, RX FIFO 0/1, RX buffers, TX event FIFO, and TX buffers.
- `struct mram_cfg` stores offset and element count for each Message RAM region.
- `struct m_can_ops` is the wrapper transport interface for register access, FIFO access, optional wrapper init/deinit, and interrupt clearing.
- `struct m_can_tx_op` carries queued peripheral TX work.
- `struct m_can_classdev` embeds `can_priv`, offload/NAPI, netdev/device pointers, clocks, reset, transceiver, operations, PM flags, interrupt/coalescing state, TX state, MRAM layout, hrtimer, and wake pinctrl.
- Function prototypes expose allocation, free, registration, unregister, clock discovery, MRAM checking, and suspend/resume helpers.

## Control Flow
Wrappers include this header, allocate a private object whose first member is `struct m_can_classdev` or whose netdev private area begins with compatible storage, fill fields such as `ops`, `dev`, `net->irq`, clock frequency, `is_peripheral`, and PM flags, then call `m_can_class_register()`. The common core later calls back into `m_can_ops` for all hardware access.

## State And Persistence
The header lays out all common runtime state. Important cached state includes `active_interrupts`, coalescing parameters, `tx_fifo_putidx`, `tx_fifo_in_flight`, queued `tx_ops`, `tx_peripheral_submit`, and parsed MRAM layout. There is no persistence outside kernel memory and hardware registers.

## Dependencies And Integration Points
The header includes many Linux kernel dependencies used by both common and wrapper code, including CAN core/dev/rx-offload, clk, reset, freezable workqueues, hrtimers, IO, netdevice, PHY, pinctrl, PM runtime, slab, and uaccess. It is the key ABI between `m_can.c`, `m_can_platform.c`, `m_can_pci.c`, and `tcan4x5x-core.c`.

## Risks And Edge Cases
- Because wrappers depend on `container_of()` around `struct m_can_classdev`, private structs must keep layout assumptions consistent.
- `m_can_ops` read/write callbacks return mixed conventions: register read returns `u32`, writes and FIFO access return `int`; common code assumes FIFO errors are propagated.
- `active_interrupts`, TX counters, and workqueue fields are shared across IRQ, NAPI, TX, and close paths, so locking rules in the C file are part of this header contract.

## Test Signals
Compile all wrappers against the header, run sparse/build checks for function pointer signatures, and test both `is_peripheral` and non-peripheral paths because the same structure fields are interpreted differently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can_pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can_pci.c

## Purpose
`m_can_pci.c` is the PCI glue for Intel PCI-attached Bosch M_CAN controllers. It maps PCI BAR MMIO into the common M_CAN transport interface and registers an `m_can_classdev`.

## Important APIs, Types, And Functions
- `struct m_can_pci_priv` embeds `struct m_can_classdev` and stores the mapped BAR base.
- `iomap_read_reg()`, `iomap_write_reg()`, `iomap_read_fifo()`, and `iomap_write_fifo()` implement `m_can_ops` with `readl()`/`writel()` and 32-bit FIFO loops.
- `m_can_pci_probe()` performs managed PCI enable/iomap, allocates the class device, allocates one IRQ vector, fills M_CAN class fields, registers the class device, enables wrapper interrupt control, and enables runtime PM autosuspend.
- `m_can_pci_remove()` disables runtime PM and wrapper interrupt control, unregisters and frees the class device, and frees IRQ vectors.
- PM callbacks forward to `m_can_class_suspend()` and `m_can_class_resume()`.

## Control Flow
Probe enables the PCI device, sets bus master, maps BAR0, allocates the common netdev/class private area, configures the class for runtime PM clock support and edge-triggered IRQ behavior, then calls the common registration path. After successful registration, it writes `CTL_CSR_INT_CTL_OFFSET` to enable the CAN wrapper interrupt output.

## State And Persistence
State is limited to the mapped MMIO base and the embedded common class state. Runtime PM state is managed through the PCI device. No persistent storage is used.

## Dependencies And Integration Points
The file depends on PCI core, runtime PM, netdevice, and the exported M_CAN class APIs. It supports Intel PCI IDs `0x4bc1` and `0x4bc2` with a 200 MHz CAN clock from `driver_data`.

## Risks And Edge Cases
- The driver marks interrupts as edge-triggered, so correctness depends on common IR drain behavior.
- FIFO access increments `void *` pointers as a GNU C extension and assumes aligned 32-bit transfers.
- Wrapper interrupt enable happens after class registration; failures after that point must disable it during remove.

## Test Signals
Validate probe/remove on supported Intel devices, MSI and legacy IRQ behavior, runtime PM autosuspend/resume, interrupt delivery after IR drain, and TX/RX over MMIO FIFO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can_platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can_platform.c

## Purpose
`m_can_platform.c` is the platform-device glue for IO-mapped Bosch M_CAN controllers. It maps controller registers and shared Message RAM, obtains clocks and optional transceiver, then registers the common M_CAN class device.

## Important APIs, Types, And Functions
- `struct m_can_plat_priv` embeds `struct m_can_classdev` and stores separate register and Message RAM bases.
- `iomap_read_reg()` and `iomap_write_reg()` access controller registers.
- `iomap_read_fifo()` and `iomap_write_fifo()` access Message RAM using the parsed offsets supplied by the common core.
- `m_can_plat_probe()` allocates the class device, gets clocks, maps named resources `m_can` and `message_ram`, obtains optional IRQ `int0`, optional PHY, fills class fields, enables runtime PM, and registers the class.
- Runtime PM callbacks enable/disable `hclk` and `cclk`; system sleep callbacks forward to the common class suspend/resume helpers.

## Control Flow
Probe begins with `m_can_class_allocate_dev()`, which already parses `bosch,mram-cfg`. The platform wrapper then supplies hardware access resources and clock rate before calling `m_can_class_register()`. If no interrupt properties are present, `net->irq` stays zero and the common driver uses hrtimer polling.

## State And Persistence
The wrapper stores only `base` and `mram_base`; the common class owns netdev, CAN state, NAPI, and PM behavior. Runtime clock state is held by PM runtime. No disk state exists.

## Dependencies And Integration Points
The file depends on platform devices, device properties, named memory resources, clocks from `m_can_class_get_clocks()`, optional PHY, runtime PM, and Open Firmware match string `bosch,m_can`.

## Risks And Edge Cases
- Missing `message_ram` resource is fatal, and bad `bosch,mram-cfg` values can still cause invalid accesses unless the integration ensures the memory range is large enough.
- The IRQ is optional; polling mode should be tested because it is selected by absence of interrupt properties.
- Runtime PM must be enabled before class registration because the common class starts clocks during setup.

## Test Signals
Validate device-tree probing with and without `interrupts`, named resource mapping, clock prepare/unprepare through runtime PM, PHY bitrate max propagation, open/close, suspend/resume, and polling-mode RX/TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/m_can_platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x-core.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x-core.c

## Purpose
`tcan4x5x-core.c` is the SPI peripheral wrapper for Texas Instruments TCAN4x5x M_CAN controllers. It handles TCAN-specific registers, reset/wake GPIOs, regulators, device identification, interrupt clearing, mode changes, and supplies regmap-backed M_CAN operations to the common class driver.

## Important APIs, Types, And Functions
- TCAN device, configuration, interrupt, MCAN, MRAM, mode, wake, and watchdog registers are defined as `TCAN4X5X_*`.
- `struct tcan4x5x_version_info` describes detected device variants and pin capabilities.
- `tcan4x5x_read_reg()`, `tcan4x5x_write_reg()`, `tcan4x5x_read_fifo()`, and `tcan4x5x_write_fifo()` implement M_CAN transport over regmap.
- `tcan4x5x_init()` clears TCAN interrupts, enables TCAN interrupt sources, unmasks error status, selects normal mode, and applies optional NWKRQ voltage behavior.
- `tcan4x5x_deinit()` puts the transceiver into standby mode.
- `tcan4x5x_get_gpios()`, `tcan4x5x_check_gpios()`, and `tcan4x5x_find_version()` handle reset/wake/state pins and device identity.
- `tcan4x5x_can_probe()` is the SPI probe path; `tcan4x5x_can_remove()` unregisters and powers down the device.

## Control Flow
Probe allocates an M_CAN class device, checks that the parsed MRAM layout fits within the TCAN MRAM window, gets the optional `vsup` regulator, obtains or defaults the CAN clock, validates the 20 to 40 MHz frequency range, configures SPI, initializes regmap, powers the chip, resets it through GPIO or software reset, detects the TCAN variant, disables absent wake/state pins in hardware, reads DT options, clears and disables interrupts, enables wakeup if requested, and calls `m_can_class_register()`.

During common M_CAN open/start, the `.init` callback wakes the device if needed, clears TCAN interrupt/status registers, enables TCAN-level interrupt bits that include the MCAN interrupt, clears error mask status, selects normal mode, and optionally sets `TCAN4X5X_NWKRQ_VOLTAGE_VIO`. On stop/deinit, the device returns to standby.

Suspend and resume wrap the common M_CAN PM helpers and enable or disable IRQ wake when the device is a wake source.

## State And Persistence
TCAN-specific state is in `struct tcan4x5x_priv`: regmap, SPI device, reset/wake/state GPIOs, regulator, aligned regmap TX/RX buffers, and the `nwkrq_voltage_vio` flag. Common CAN state lives in the embedded `m_can_classdev`. Hardware mode, interrupt masks, wake pin behavior, and MRAM are volatile device state.

## Dependencies And Integration Points
The file depends on SPI, regmap, GPIO descriptors, regulators, clocks, device-tree properties, and exported M_CAN class APIs. It also depends on `tcan4x5x_regmap_init()` from `tcan4x5x-regmap.c` and `struct tcan4x5x_priv` from `tcan4x5x.h`.

## Risks And Edge Cases
- If no clock is provided, the driver logs an error but defaults to 40 MHz; board descriptions must match actual hardware timing.
- Wake/state GPIO absence is handled differently depending on detected variant capabilities; generic fallback assumes both pins exist.
- The SPI IRQ must be valid for interrupt-driven operation; common peripheral code relies on threaded IRQ and RX offload.
- Regulator power is disabled on probe failure and remove, but runtime open/close power cycling is not used.
- `tcan4x5x_read_reg()` ignores the regmap read return code and returns whatever `val` holds if the read fails.

## Test Signals
Test TCAN4552, TCAN4553, and generic-compatible devices; reset GPIO and software reset paths; missing wake/state GPIO handling; optional regulator; clock absent, low, high, and valid cases; wakeup-source suspend/resume; SPI half/full duplex controllers; CAN FD TX/RX; and TCAN bus fault interrupt clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x-regmap.c

## Purpose
`tcan4x5x-regmap.c` implements the SPI regmap bus used by the TCAN4x5x wrapper. It translates regmap reads and writes into TCAN SPI command frames with big-endian register/value formatting.

## Important APIs, Types, And Functions
- `TCAN4X5X_SPI_INSTRUCTION_WRITE` and `TCAN4X5X_SPI_INSTRUCTION_READ` encode the TCAN SPI opcodes.
- `tcan4x5x_regmap_gather_write()` builds one write transfer containing command header plus payload.
- `tcan4x5x_regmap_write()` adapts flat regmap writes to gather writes.
- `tcan4x5x_regmap_read()` builds command and receive transfers, supporting both half-duplex and full-duplex SPI controllers.
- Read/write access tables restrict allowed TCAN, M_CAN, and MRAM register ranges.
- `tcan4x5x_regmap` and `tcan4x5x_bus` define regmap geometry, endianness, raw transfer limits, flags, and access policy.
- `tcan4x5x_regmap_init()` creates the devm regmap.

## Control Flow
The TCAN probe calls `tcan4x5x_regmap_init()` after SPI setup. All later TCAN core register access and common M_CAN register/FIFO access go through this regmap. Reads copy the command into the aligned TX buffer, set word length, then either issue command and RX payload as separate transfers for half-duplex controllers or one full-duplex transfer with a sanitized data area.

## State And Persistence
The regmap uses no cache (`REGCACHE_NONE`). Transfer state is transient in `map_buf_tx` and `map_buf_rx` embedded in `struct tcan4x5x_priv`. There is no persistent state.

## Dependencies And Integration Points
The file depends on SPI controller capabilities, regmap bus APIs, and TCAN private buffers from `tcan4x5x.h`. It is linked into the composite `tcan4x5x` module with `tcan4x5x-core.o`.

## Risks And Edge Cases
- `tcan4x5x_spi_cmd_set_len()` stores byte length divided by four; callers must provide 32-bit aligned transfer lengths.
- Raw reads/writes are capped at 256 bytes, matching the static buffer data length.
- Access tables must include every M_CAN register used by the common core; missing ranges would fail regmap operations.
- Full-duplex reads rely on copying from `buf_rx->data` after the combined transfer; sanitizing TX data avoids leaking stale buffer contents.

## Test Signals
Exercise regmap single register reads/writes, bulk MRAM reads/writes, half-duplex and full-duplex SPI controllers, access-table rejection of invalid registers, and max-size raw transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x.h

## Purpose
`tcan4x5x.h` defines private TCAN4x5x SPI/regmap data structures and the regmap initialization prototype shared by the TCAN core and regmap files.

## Important APIs, Types, And Functions
- `TCAN4X5X_SANITIZE_SPI` enables clearing unused TX bytes for full-duplex reads.
- `struct tcan4x5x_buf_cmd` is the packed SPI command header: opcode, 16-bit address, and word count.
- `struct tcan4x5x_map_buf` combines a command header and a 256-word data buffer, cacheline aligned for transfer use.
- `struct tcan4x5x_priv` embeds `m_can_classdev` and stores regmap, SPI device, GPIOs, regulator, TX/RX buffers, and DT option state.
- `tcan4x5x_spi_cmd_set_len()` converts byte length to the TCAN command word count.
- `tcan4x5x_regmap_init()` is implemented by `tcan4x5x-regmap.c`.

## Control Flow
The TCAN SPI probe allocates an M_CAN class device with enough private space for `struct tcan4x5x_priv`; the core and regmap files recover this structure from `m_can_classdev` or SPI driver data and share the same transfer buffers.

## State And Persistence
The header defines volatile runtime state only. GPIO descriptors, regulator handles, regmap, SPI device, and aligned buffers are owned for the lifetime of the SPI device.

## Dependencies And Integration Points
It includes GPIO consumer, regmap, regulator, SPI, and `m_can.h`. It is the bridge between the bus transport implementation and the M_CAN class wrapper.

## Risks And Edge Cases
- Buffer length and SPI command length assume transfers are multiples of four bytes.
- Because the class device is embedded first, container conversions depend on stable struct layout.
- The static transfer buffer size must stay consistent with regmap `.max_raw_read` and `.max_raw_write`.

## Test Signals
Build TCAN core/regmap together, validate struct layout through normal probe, and test SPI transfers at the maximum configured raw size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/m_can/tcan4x5x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/mscan/Kconfig

## Purpose
This Kconfig file controls support for Freescale/Motorola MSCAN based controllers and the MPC5xxx onboard CAN driver.

## Important APIs, Types, And Functions
- `CAN_MSCAN` is a PPC-only tristate for the generic MSCAN support.
- `CAN_MPC5XXX` is available under `CAN_MSCAN`, depends on `PPC_MPC52xx || PPC_MPC512x`, and builds support for MPC5200/MPC5200B/MPC5121 controllers.

## Control Flow
The child option is only visible when `CAN_MSCAN` is enabled. Selecting `CAN_MPC5XXX` builds the combined generic MSCAN core and MPC5xxx platform glue as a module or built-in object.

## State And Persistence
The file controls build-time availability only.

## Dependencies And Integration Points
The PPC dependency reflects register layout, clock, and SoC support assumptions in `mscan.h` and `mpc5xxx_can.c`.

## Risks And Edge Cases
- The generic MSCAN core is not built standalone by this Makefile; it is linked into the MPC5xxx module.
- The help text lists support only for MPC5121 revision 2 and later, but runtime revision checking is limited to compatible matching and clock/register behavior.

## Test Signals
Check PPC randconfig/allmodconfig builds, dependency visibility for MPC52xx/MPC512x, and module naming as `mscan-mpc5xxx.ko`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/mscan/Makefile

## Purpose
This Makefile builds the MSCAN MPC5xxx driver from the generic MSCAN core and platform glue.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CAN_MPC5XXX) += mscan-mpc5xxx.o` creates the final driver object/module.
- `mscan-mpc5xxx-objs := mscan.o mpc5xxx_can.o` links generic MSCAN logic with MPC5xxx platform support.

## Control Flow
Kbuild includes both object files in one module when `CAN_MPC5XXX` is enabled.

## State And Persistence
No runtime state is defined here.

## Dependencies And Integration Points
The composition means exported symbols between `mscan.c` and `mpc5xxx_can.c` remain internal to the final module unless exported elsewhere.

## Risks And Edge Cases
Build failures in either generic core or platform glue prevent the single module from linking. There is no separate module for generic MSCAN.

## Test Signals
Run module and built-in builds for `CONFIG_CAN_MPC5XXX`, and confirm `mscan.o` plus `mpc5xxx_can.o` are linked into `mscan-mpc5xxx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/mpc5xxx_can.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/mscan/mpc5xxx_can.c

## Purpose
`mpc5xxx_can.c` is the platform/OF glue for Freescale MPC5xxx MSCAN controllers. It maps registers, obtains IRQ and SoC-specific clocks, allocates the generic MSCAN netdev, registers it, and handles remove plus basic suspend/resume register save/restore.

## Important APIs, Types, And Functions
- `struct mpc5xxx_can_data` selects controller type and clock get/put callbacks per compatible.
- `mpc52xx_can_get_clock()` handles MPC5200 clock source selection between bus and oscillator, including the old revision A erratum.
- `mpc512x_can_get_clock()` interprets `fsl,mscan-clock-source` and `fsl,mscan-clock-divider`, configures clock parents/rates, enables the IPG register clock, and stores clock handles in `mscan_priv`.
- `mpc512x_can_put_clock()` disables the IPG clock.
- `mpc5xxx_can_probe()` maps OF resources, parses IRQ, allocates `alloc_mscandev()`, fills private fields, derives the CAN clock, and calls `register_mscandev()`.
- `mpc5xxx_can_remove()` unregisters the generic device, releases clocks, unmaps IO, disposes IRQ mapping, and frees the candev.
- PM callbacks save the MSCAN register block into static `saved_regs` and restore it around INIT mode.

## Control Flow
OF matching selects either MPC5200 or MPC5121 data. Probe maps the first register resource and IRQ, allocates a generic MSCAN netdev, records the base and IRQ, reads the optional clock-source property, asks the SoC callback for a usable CAN clock and `MSCAN_CLKSRC` setting, and registers the device. Registration is delegated to `mscan.c`, which programs acceptance filters and registers with SocketCAN.

MPC512x clock setup can auto-select a system clock divisible to 16 MHz, fall back to reference clock, or obey explicit `ip`, `sys`, or `ref` choices. It also enables the separate IPG clock needed for register access.

Suspend copies the register layout to a static buffer. Resume requests INIT mode, restores control, bit timing, acceptance, buffer, interrupt, and TX selection registers, then returns to the previous control state.

## State And Persistence
State lives in the platform device driver data as the netdev and in `mscan_priv` fields populated here. Clock handles are devm-managed but enabled/disabled explicitly for MPC512x IPG. The PM save area is a single static `struct mscan_regs`, which persists only in kernel memory and is shared across instances.

## Dependencies And Integration Points
The file depends on OF address/IRQ APIs, platform devices, PPC SoC helpers, MPC52xx register definitions, the common clock framework for MPC512x, and generic MSCAN APIs from `mscan.h`/`mscan.c`.

## Risks And Edge Cases
- The static `saved_regs` suspend buffer is not per-device, so multiple MSCAN instances suspended concurrently could overwrite each other.
- Clock derivation returns zero on many failures, which collapses distinct clock errors into a generic probe failure.
- `of_iomap()`/`irq_of_parse_and_map()` are manually paired with `iounmap()`/`irq_dispose_mapping()`, so error paths must remain balanced.
- MPC5200 oscillator selection depends on SoC-specific CDM mapping and PVR erratum handling.

## Test Signals
Test MPC5200 and MPC5121 compatible probing, explicit and automatic clock-source properties, invalid clock-source failure, register clock enable/disable, remove error-path cleanup, suspend/resume with active configuration, and multiple-channel suspend behavior if hardware exposes more than one node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/mpc5xxx_can.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/mscan.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/mscan/mscan.c

## Purpose
`mscan.c` is the generic SocketCAN driver logic for Freescale/Motorola MSCAN controllers. It handles mode changes, bit timing, TX buffer management, RX/error NAPI polling, interrupts, open/close, and generic device allocation/registration.

## Important APIs, Types, And Functions
- `mscan_bittiming_const` defines classic CAN timing limits.
- `mscan_set_mode()` transitions between normal, sleep, init, and poweroff-style modes using `CANCTL0/CANCTL1` handshakes.
- `mscan_start()` initializes software TX/RX state, clears MPC5121 bus-off hold, enters normal mode, caches status flags, and enables receive interrupts.
- `mscan_restart()` supports CAN restart, with special MPC5121 bus-off hold behavior.
- `mscan_start_xmit()` selects one of three hardware TX buffers, encodes standard/extended CAN IDs and RTR, writes payload and priority, starts transmission, and saves echo skb.
- `mscan_rx_poll()` drains receive and error events through NAPI.
- `mscan_isr()` handles TX completions and schedules RX/error NAPI.
- `register_mscandev()`, `unregister_mscandev()`, and `alloc_mscandev()` are the API used by platform glue.

## Control Flow
Open enables clocks, calls `open_candev()`, enables NAPI, requests IRQ, sets listen-only mode bit, starts the controller, and starts the netdev queue. Close stops the queue, disables NAPI, masks interrupts, enters init mode, closes the candev, frees IRQ, and disables clocks.

TX disables TX interrupts, chooses a free hardware buffer from `~tx_active & MSCAN_TXE`, manages queue stop/priority ordering when hardware buffer priority could reorder frames, writes ID/data/DLC/priority into the selected buffer, starts transmission with `CANTFLG`, queues echo state in a linked list, marks the buffer active, and reenables TX interrupts for active buffers.

The ISR first handles TX complete flags by walking `tx_head`, reclaiming echo skbs, updating stats, clearing active bits, and waking the queue when allowed. It then examines receive/error flags and, if no RX poll is already running, shadows interrupt enables, disables receive interrupts, and schedules NAPI.

NAPI loops while RX or error flags are present. RX events allocate a classic CAN skb, decode ID/data from the receive buffer, acknowledge `MSCAN_RXF`, and update stats. Error events build CAN error frames, report overflow and state changes, handle bus-off, and acknowledge error flags.

## State And Persistence
`struct mscan_priv` stores controller type, flags, mapped register base, clocks, cached status/interrupt masks, TX priority and active-buffer state, a linked list of TX queue entries, and NAPI. Hardware acceptance filters are initialized to accept all frames. No persistent storage is used.

## Dependencies And Integration Points
The file depends on SocketCAN, NAPI, netdevice, classic CAN skb helpers, Linux IO accessors, clocks, and register definitions from `mscan.h`. It is linked with `mpc5xxx_can.c`, which supplies mapped resources and clock source selection.

## Risks And Edge Cases
- There is a stray `#` character at the end of the "Abort transfers before going to sleep" comment line; if present in the actual compilation unit, it would be a syntax/preprocessor issue worth verifying in the full tree context.
- TX ordering is constrained by hardware buffer priorities; the `cur_pri`/`F_TX_WAIT_ALL` logic is subtle and can stop the queue until all buffers drain.
- Sleep-mode entry may fail under bus activity; the driver proceeds to avoid leaving `SLPRQ` stuck.
- Bus-off recovery differs by MPC5121 versus older controllers, including automatic recovery prevention for non-MPC5121.
- Only classic CAN is supported; no CAN FD paths exist.

## Test Signals
Exercise standard and extended IDs, RTR, all three TX buffers, queue stop/wake under sustained TX, RX overflow, state transitions, bus-off and restart, listen-only, 3-sample bit timing, open/close clock balancing, and NAPI scheduling under mixed TX/RX interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/mscan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/mscan.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/mscan/mscan.h

## Purpose
`mscan.h` defines register bits, register layout, timing macros, private state, and public helper prototypes for the MSCAN driver.

## Important APIs, Types, And Functions
- `MSCAN_*` macros define control, status, interrupt, TX, acceptance filter, misc, ID, mode, retry, and state bits.
- `struct mscan_regs` describes the packed hardware register map, including PPC MPC5xxx reserved spacing through `_MSCAN_RESERVED_`.
- `BTR0_*` and `BTR1_*` macros encode classic CAN bit timing values.
- `struct tx_queue_entry` tracks hardware TX buffer echo/list metadata.
- `struct mscan_priv` embeds `can_priv` first and stores type, flags, register base, clocks, cached interrupt/status state, TX state, TX queue entries, and NAPI.
- Prototypes expose `alloc_mscandev()`, `register_mscandev()`, and `unregister_mscandev()`.

## Control Flow
The platform driver allocates a netdev with `alloc_mscandev()`, fills `reg_base`, `type`, clocks, and IRQ, then calls `register_mscandev()`. The generic driver uses the register layout and bit macros throughout open, TX, RX, IRQ, and mode transitions.

## State And Persistence
The header defines in-memory per-device state and the hardware register map. It also defines compile-time layout differences under `CONFIG_PPC`, including reserved register gaps and clock-source bit semantics.

## Dependencies And Integration Points
It includes clock and type headers and relies on `CONFIG_PPC` to select MPC5xxx-specific layout definitions. It is shared by `mscan.c` and `mpc5xxx_can.c`.

## Risks And Edge Cases
- Register layout changes under `CONFIG_PPC`; using this header for a non-PPC MSCAN integration would need careful validation.
- `MSCAN_REGION` is defined as `sizeof(struct mscan)`, but the defined register type is `struct mscan_regs`; this macro is not used in the inspected files but looks stale.
- `struct mscan_priv` requires `can_priv` to be first for casts and netdev private assumptions.

## Test Signals
Compile PPC and non-PPC configurations where possible, validate register offsets against hardware documentation, and run sparse/build checks for the stale `MSCAN_REGION` macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/mscan/mscan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/Kconfig

## Purpose
This Kconfig file enables the PEAK-System PCAN-PCIe FD family driver.

## Important APIs, Types, And Functions
- `CAN_PEAK_PCIEFD` is a PCI-dependent tristate.
- The help text documents PEAK PCIe FD cards with one or two CAN FD channels, CAN 2.0 A/B, CAN FD data bitrates up to 12 Mbit/s, galvanic isolation, and industrial temperature range.

## Control Flow
When selected, Kbuild links the PEAK CAN FD common uCAN logic with the PCIe FD board driver.

## State And Persistence
Only build configuration state is represented.

## Dependencies And Integration Points
The only explicit dependency is `PCI`; runtime integration also depends on SocketCAN and the common PEAK uCAN header in `include/linux/can/dev/peak_canfd.h`.

## Risks And Edge Cases
- The help text mentions one or two channels, while the PCIe main driver derives one to four channels from subsystem IDs.
- No explicit dependency on CAN FD core support is listed here, so it relies on surrounding CAN driver menu dependencies.

## Test Signals
Check Kconfig visibility under PCI and build the module for allmodconfig and PCI-disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/Makefile

## Purpose
This Makefile builds the PEAK PCIe CAN FD driver as a composite module/object.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CAN_PEAK_PCIEFD) += peak_pciefd.o` defines the final target.
- `peak_pciefd-y := peak_pciefd_main.o peak_canfd.o` links PCIe board support with common PEAK uCAN CAN FD logic.

## Control Flow
Kbuild composes both object files into `peak_pciefd` when the Kconfig symbol is enabled.

## State And Persistence
No runtime state is defined here.

## Dependencies And Integration Points
The composition allows `peak_pciefd_main.c` to call common functions from `peak_canfd.c` without exporting a separate module.

## Risks And Edge Cases
If another PEAK bus wrapper is added, common `peak_canfd.o` may need to move to a separate library object or be linked into multiple modules carefully.

## Test Signals
Build `CONFIG_CAN_PEAK_PCIEFD=y` and `m`, and inspect that the final module contains both common and PCIe symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_canfd.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_canfd.c

## Purpose
`peak_canfd.c` is the common PEAK-System uCAN CAN FD netdev layer. It provides command construction, bit timing commands, mode changes, RX message parsing, status/error handling, TX skb formatting, echo management, hardware timestamp reporting, and allocation of PEAK CAN FD netdevs. Bus-specific drivers supply command and TX transport callbacks.

## Important APIs, Types, And Functions
- `peak_canfd_nominal_const` and `peak_canfd_data_const` define bit timing ranges from uCAN field widths.
- `pucan_init_cmd()`, `pucan_add_cmd()`, and `pucan_write_cmd()` build and submit uCAN commands through bus callbacks.
- Command helpers include reset/normal/listen-only modes, slow/fast timing, standard filters, TX abort, error counter clear, option set/clear, and RX barrier.
- RX handlers include `pucan_handle_can_rx()`, `pucan_handle_error()`, `pucan_handle_status()`, and `pucan_handle_cache_critical()`.
- Public message APIs are `peak_canfd_handle_msg()` and `peak_canfd_handle_msgs_list()`.
- Netdev operations are `peak_canfd_open()`, `peak_canfd_close()`, and `peak_canfd_start_xmit()`.
- `alloc_peak_canfd_dev()` allocates and initializes a SocketCAN netdev with PEAK-specific callbacks and capabilities.

## Control Flow
Open calls `open_candev()`, commands reset mode, configures CAN FD ISO/non-ISO option when FD is enabled, enables error counter reporting, programs all standard filter rows to accept all standard IDs, starts the controller in normal or listen-only mode, then sends an RX barrier. The bus-specific driver treats the barrier status as the point where the TX path can be safely enabled and the netdev queue woken.

TX asks the bus-specific `alloc_tx_msg()` for room, formats a `pucan_tx_msg` with CAN ID, DLC, CAN FD flags, RTR, loopback, and optional self-receive, stores an echo skb under `echo_lock`, advances `echo_idx`, stops the queue when echo slots or transport room are exhausted, and calls `write_tx_msg()`.

RX message lists are parsed by size/type. CAN RX messages may first reclaim echo skbs when marked looped back, then optionally deliver self-received frames to RX. Status messages update CAN state, emit CAN error frames, call `can_bus_off()` on bus-off, and process RX barrier confirmation. Error messages update cached BEC counters. Cache-critical messages report RX overflow.

## State And Persistence
State lives in `struct peak_canfd_priv`: CAN core state, netdev pointer, channel index, cached error counters, echo ring index/lock, command buffer state, and bus callback pointers. Hardware timestamps are converted from uCAN microsecond counters to skb hardware timestamps. No persistent storage exists.

## Dependencies And Integration Points
The file depends on SocketCAN, PEAK uCAN protocol structures from `<linux/can/dev/peak_canfd.h>`, and bus-specific callbacks supplied through `peak_canfd_user.h`. The PCIe FD implementation is one such bus-specific backend.

## Risks And Edge Cases
- `pucan_add_cmd()` returns NULL on command-buffer overflow, but several command helpers dereference the returned pointer without checking because current command buffers are sized for one command.
- Queue wake relies on loopback echo messages; lost loopback notifications can leave echo slots occupied.
- RX barrier sequencing is required before TX path enablement; a missing barrier status would keep the queue stopped.
- The common code accepts all standard filters but does not show extended filter programming in this file.
- `pucan_handle_status()` calls `dev_kfree_skb(skb)` even if `alloc_can_err_skb()` returned NULL in the no-state-change path; `dev_kfree_skb(NULL)` is safe but worth noting.

## Test Signals
Test open configuration, CAN FD ISO/non-ISO option switching, listen-only, loopback and self-receive, echo reclaim, queue stop/wake on echo ring exhaustion, RX barrier handling, bus-off and restart, error counter reporting, RX overflow error frames, and hardware timestamp visibility through ethtool/SO_TIMESTAMPING.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_canfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_canfd_user.h -->
# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_canfd_user.h

## Purpose
`peak_canfd_user.h` defines the private interface between PEAK's common uCAN CAN FD logic and bus-specific drivers.

## Important APIs, Types, And Functions
- `PCANFD_ECHO_SKB_DEF` tells the allocator to use the common default echo skb count.
- `struct peak_canfd_priv` embeds `can_priv`, netdev pointer, channel index, BEC cache, echo ring state, command buffer state, and callback hooks.
- Callback hooks cover command pre-processing, command write, command post-processing, TX path enablement, TX message allocation, and TX message submission.
- Public prototypes expose `alloc_peak_canfd_dev()`, `peak_canfd_handle_msg()`, and `peak_canfd_handle_msgs_list()`.

## Control Flow
Bus drivers allocate a netdev with `alloc_peak_canfd_dev()`, then fill callbacks and command buffer fields. The common code calls those callbacks during open, mode changes, and TX. Bus drivers call `peak_canfd_handle_msgs_list()` when transport-specific RX/IRQ code obtains uCAN messages.

## State And Persistence
The struct defines per-channel runtime state. It has no persistent storage and no global state.

## Dependencies And Integration Points
It includes `<linux/can/dev/peak_canfd.h>` for uCAN message and command protocol definitions. It is shared by `peak_canfd.c` and `peak_pciefd_main.c`.

## Risks And Edge Cases
- `struct can_priv` must remain first for SocketCAN private-data assumptions.
- The callback contract is not type-specialized by transport, so bus drivers must ensure command buffer size, DMA/message allocation, and callback sequencing match common expectations.
- Echo locking is shared between common TX and backend IRQ wake paths.

## Test Signals
Compile common plus PCIe backend, validate callback initialization before registration, and run TX/RX paths that exercise every callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_canfd_user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_pciefd_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_pciefd_main.c

## Purpose
`peak_pciefd_main.c` is the PCIe backend for PEAK PCAN-PCIe FD, cPCIe FD, PCIe-104 FD, mini-PCIe FD, OEM, and M.2 CAN FD cards. It discovers board/channel count, maps PCI registers, allocates per-channel DMA buffers, wires transport callbacks into the common uCAN layer, handles IRQs, and manages TX/RX DMA rings.

## Important APIs, Types, And Functions
- PCI IDs are listed in `peak_pciefd_tbl`.
- Board/system and per-channel register offsets/bits define clock, timestamp, command, DMA, and IRQ controls.
- `struct pciefd_rx_dma`, `struct pciefd_tx_link`, `struct pciefd_page`, `struct pciefd_can`, and `struct pciefd_board` model RX DMA records, TX page links, per-channel state, and board state.
- `pciefd_irq_handler()` processes one channel's DMA IRQ tag, RX message list, TX page-link completion, queue wake, and RX DMA rearm.
- Backend callbacks are `pciefd_pre_cmd()`, `pciefd_write_cmd()`, `pciefd_post_cmd()`, `pciefd_enable_tx_path()`, `pciefd_alloc_tx_msg()`, and `pciefd_write_tx_msg()`.
- `pciefd_can_probe()` allocates/registers one channel; `peak_pciefd_probe()` handles the whole PCI device.

## Control Flow
PCI probe enables the device, requests regions, reads subsystem ID to derive one to four CAN channels, allocates a flexible board structure, maps BAR0, reads FPGA firmware version, applies a 32-bit DMA mask workaround for old firmware on 64-bit DMA architectures, stops the system clock, sets bus master, probes each channel, resets the system timestamp counter, starts the system clock, and stores board drvdata.

Per-channel probe allocates a PEAK CAN FD netdev, fills common backend callbacks and command buffer, computes the channel register base, allocates coherent RX and TX DMA areas, resets channel timestamp/clock state, determines the CAN clock from the hardware clock selector, assigns the shared PCI IRQ, registers the candev, initializes `tx_lock`, and stores the channel in the board.

Entering normal/listen-only mode triggers `pciefd_pre_cmd()`: request the channel IRQ, program RX DMA address and IRQ coalescing limits, clear RX reset, reset channel timestamp, acknowledge the initial RX tag, and enable channel IRQ. The command is then written atomically as a 64-bit command through the board command lock. After reset-mode commands, `pciefd_post_cmd()` disables IRQs, clears TX/RX DMA, performs a read flush, frees the IRQ, and marks the channel stopped.

TX pages are 2 KiB regions inside the 4 KiB TX DMA area. `pciefd_alloc_tx_msg()` reserves space in the current page, emits a link record to a new page when the current page is full, tracks free pages, and returns available room to the common TX code. `pciefd_write_tx_msg()` advances the page offset and rings the TX request accumulator. IRQ link notifications free TX pages and wake the queue if echo space is available.

## State And Persistence
Per-board state includes BAR base, PCI device, channel count, and a command spinlock. Per-channel state includes register base, coherent RX/TX DMA virtual/logical addresses, TX page descriptors, free-page count, current page index, TX lock, last IRQ status, and expected IRQ tag. Hardware timestamp counter and DMA addresses are volatile hardware state.

## Dependencies And Integration Points
The backend depends on PCI, DMA coherent allocation, MMIO accessors, SocketCAN through `peak_canfd.c`, and PEAK uCAN protocol definitions. It shares the PCI IRQ across channels by requesting it per channel with `IRQF_SHARED`.

## Risks And Edge Cases
- `pciefd_can_probe()` returns `-ENOMEM` through the `failure` label even for `register_candev()` errors, losing the original error code.
- IRQs are requested during mode transition rather than PCI probe, so repeated open/close must balance request/free exactly.
- TX page allocation updates page offsets after the common code fills the returned message; concurrency relies on the netdev TX serialization plus `tx_lock` around page selection.
- Old firmware DMA mask workaround is conditional on decoded version; incorrect version decode could leave an incompatible 64-bit DMA mode.
- Shared IRQ tag matching assumes RX DMA status memory is coherent and updated before interrupt handling reads it.

## Test Signals
Test all supported PCI IDs/subsystem channel counts, firmware versions below and above 3.3.0 on 64-bit systems, shared IRQ handling across multiple channels, open/close request/free IRQ balancing, TX page rollover/link interrupts, RX DMA tag sequence, CAN FD TX/RX, bus-off/reset-mode cleanup, and remove after active channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/peak_canfd/peak_pciefd_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rcar/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/can/rcar/Kconfig

## Purpose
This Kconfig file defines Renesas R-Car/RZ-G CAN controller build options.

## Important APIs, Types, And Functions
- `CAN_RCAR` enables the classic Renesas R-Car and RZ/G CAN controller driver.
- `CAN_RCAR_CANFD` enables the Renesas R-Car CAN FD controller driver.
- Both depend on `ARCH_RENESAS || COMPILE_TEST`.

## Control Flow
The two options are independent tristates. Selecting each causes the corresponding object to be built by the local Makefile.

## State And Persistence
Only build-time configuration is represented.

## Dependencies And Integration Points
The dependency allows native Renesas builds and compile-test coverage elsewhere. The CAN FD help notes that the FD driver runs the controller in CAN FD only mode while interoperating with CAN 2.0 nodes.

## Risks And Edge Cases
- Users expecting a dedicated classic CAN 2.0 mode from `CAN_RCAR_CANFD` may be surprised; the help explicitly says FD-only controller mode.
- Runtime dependencies such as clocks, resets, IRQs, and device-tree bindings are not expressed in this Kconfig fragment.

## Test Signals
Check build visibility under Renesas and COMPILE_TEST configs, and verify module names `rcar_can` and `rcar_canfd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rcar/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rcar/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/can/rcar/Makefile

## Purpose
This Makefile maps Renesas R-Car CAN Kconfig symbols to driver objects.

## Important APIs, Types, And Functions
- `obj-$(CONFIG_CAN_RCAR) += rcar_can.o` builds the classic CAN driver.
- `obj-$(CONFIG_CAN_RCAR_CANFD) += rcar_canfd.o` builds the CAN FD driver.

## Control Flow
Kbuild includes each object independently according to its Kconfig symbol.

## State And Persistence
No runtime state is defined here.

## Dependencies And Integration Points
The file is paired with `rcar/Kconfig` and relies on driver source files outside this subset for actual implementation.

## Risks And Edge Cases
- There is no composite-object logic, so any shared helper code between `rcar_can.o` and `rcar_canfd.o` would need to live elsewhere or be duplicated.

## Test Signals
Build each option independently and together to verify object inclusion and module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/rcar/Makefile -->
