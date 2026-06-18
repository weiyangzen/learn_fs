# subset-b-003854 research

Grouped research for the I2C bus driver sources listed in work item `subset-b-003854`. Each section is wrapped with the exact file-research markers expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-platform.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-platform.c

Purpose: this is the platform-bus wrapper for the PA Semi/Apple SMBus controller shared core in `i2c-pasemi-core.h`. It binds Apple DT compatibles such as `apple,t8103-i2c` and `apple,i2c`, maps the MMIO resource, enables the reference clock, derives the SMBus clock divider, and delegates adapter setup to `pasemi_i2c_common_probe()`.

Important APIs, types, and functions: `struct pasemi_platform_i2c_data` embeds `struct pasemi_smbus` plus a reference clock. `pasemi_platform_i2c_calc_clk_div()` uses `clk_get_rate()` and `DIV_ROUND_UP()` to compute `smbus.clk_div` as source clock divided by `16 * frequency`, rejecting dividers outside the hardware byte range. `pasemi_platform_i2c_probe()` uses devm allocation, `devm_platform_ioremap_resource()`, `of_property_read_u32("clock-frequency")`, `devm_clk_get_enabled()`, `pasemi_i2c_common_probe()`, `platform_get_irq()`, and `devm_request_irq()` with `pasemi_irq_handler`. The remove callback is intentionally empty because resources are devm-managed and common teardown is apparently handled by managed adapter registration in the core.

Control flow: probe allocates state, initializes `smbus->dev`, maps registers, reads or defaults the bus frequency to standard mode, enables the clock, calculates the divider, assigns the adapter OF node, calls the common core probe, then tries to attach an IRQ. IRQ request failure is not fatal; it simply leaves `smbus->use_irq` unset so the common core can operate without interrupts. Driver registration is via `module_platform_driver()`.

State and persistence: all runtime state is in the device-managed `pasemi_platform_i2c_data`. Persistent hardware state consists of the clock divider and interrupt mode in the shared `pasemi_smbus` structure. There is no disk persistence, global mutable state, or explicit remove teardown in this wrapper.

Dependencies and integration points: it depends on Linux clock, OF, platform, MMIO, and I2C subsystems plus the local PASemi common core. DT supplies MMIO, optional `clock-frequency`, clock, IRQ, and compatible strings. The core provides actual SMBus transaction behavior and interrupt handling.

Risks: invalid clock rates can make frequencies too fast or too slow and probe fails. IRQ acquisition is best-effort, so latency and timeout behavior depend on the common core polling path when no IRQ is usable. The empty remove path is safe only if common adapter/resources are devm-managed by `pasemi_i2c_common_probe()`.

Test signals: boot/probe on Apple hardware should show adapter registration and working standard-mode transfers. Negative tests include zero clock rate, out-of-range `clock-frequency`, missing MMIO, missing clock, no IRQ fallback, and client SMBus reads/writes through the resulting adapter.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pasemi-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pca-isa.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pca-isa.c

Purpose: this driver exposes PCA9564/PCA9665 I2C controllers wired on ISA I/O ports. It provides the bus-specific register access and completion callbacks required by the generic `i2c-algo-pca` algorithm, with module parameters for base address, IRQ, and controller clock.

Important APIs, types, and functions: global parameters `base`, `irq`, and `clock` configure the ISA instance. `pca_isa_writebyte()` and `pca_isa_readbyte()` perform byte I/O with `outb()` and `inb()` at `base + reg`. `pca_isa_waitforcompletion()` either blocks on `pca_wait` until `I2C_PCA_CON_SI` is set or polls with `udelay(100)`. `pca_handler()` wakes the wait queue. `pca_isa_data` wires these callbacks into `struct i2c_algo_pca_data`; `pca_isa_ops` is the statically allocated `struct i2c_adapter`. Probe requests the I/O region, optionally requests the IRQ, sets the algorithm clock, and calls `i2c_pca_add_bus()`.

Control flow: `pca_isa_match()` requires a nonzero module-supplied base address and warns if polling mode will be used. Probe initializes the wait queue, validates legacy PPC I/O availability, reserves four I/O ports, requests the IRQ if specified, sets `i2c_clock`, and registers the adapter. Failure unwinds IRQ and region allocation. Remove deletes the adapter, disables/frees IRQ when present, and releases the I/O region.

State and persistence: the driver is effectively singleton-style because the adapter, wait queue, and configuration are static globals. Runtime transfer state is mostly held in the generic PCA algorithm; this file stores no per-transfer buffers. Configuration persists only for the module lifetime.

Dependencies and integration points: it depends on the ISA bus, module parameters, legacy I/O port allocation, optional IRQ delivery, wait queues, and `i2c-algo-pca`. It integrates into the I2C core through `i2c_pca_add_bus()` and exposes clock choices matching PCA9564/PCA9665 hardware capabilities.

Risks: there is no hardware auto-discovery; wrong `base` or `force`-style configuration can access unrelated I/O ports. The reset callback only logs that reset is unsupported, so stuck hardware may require external reset. Polling mode has coarser latency and depends on jiffies timeout. The static singleton model is inappropriate for multiple ISA adapters.

Test signals: load with valid `base`, with and without `irq`, verify adapter creation, simple I2C transfers, timeout behavior when SI never sets, region conflict handling, IRQ wakeup behavior, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pca-isa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pca-platform.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pca-platform.c

Purpose: this is the platform/OF wrapper for memory-mapped PCA9564/PCA9665 controllers. Like the ISA variant, it supplies register access, wait, interrupt, and reset callbacks to the shared `i2c-algo-pca` engine, but supports platform resources, MMIO register strides, optional GPIO reset, and numbered adapter registration.

Important APIs, types, and functions: `struct i2c_pca_pf_data` contains MMIO base, optional IRQ, reset GPIO, wait queue, adapter, and `i2c_algo_pca_data`. Separate `readbyte`/`writebyte` helpers handle 8-, 16-, and 32-bit memory resource spacing while still performing byte I/O. `i2c_pca_pf_waitforcompletion()` waits on IRQ or polls `I2C_PCA_CON_SI`. `i2c_pca_pf_handler()` filters interrupts by checking SI before waking waiters. Reset is either GPIO pulse in `i2c_pca_pf_resetchip()` or a warning-only dummy reset.

Control flow: probe obtains an optional IRQ, allocates driver state, maps the first memory resource, initializes adapter fields, gets optional `reset` GPIO, reads `clock-frequency` or defaults to 59000 Hz, lets platform data override timeout and clock, assigns callbacks, selects register spacing from `IORESOURCE_MEM_TYPE_MASK`, requests IRQ if present, and calls `i2c_pca_add_numbered_bus()`. Remove deletes the adapter; devm handles mappings, GPIO, memory, and IRQ.

State and persistence: per-device state is entirely in `i2c_pca_pf_data`. The wait queue and adapter timeout are persistent for device lifetime. Hardware state includes PCA algorithm registers and optional reset GPIO state. No persistent storage is used.

Dependencies and integration points: this file depends on platform resources, OF compatibles `nxp,pca9564` and `nxp,pca9665`, device properties, GPIO descriptors, IRQs, and `i2c-algo-pca`. It can also consume legacy `i2c_pca9564_pf_platform_data`.

Risks: incorrect resource flags select the wrong register stride and break register access. Without a reset GPIO, bus recovery is limited to algorithm-level behavior and the chip may remain stuck. IRQ is optional and polling fallback must be validated on slow systems. Platform data can override DT-derived clock and timeout in ways that produce unexpected bus timing.

Test signals: DT and platform-data probe paths, 8/16/32-bit resource spacing, IRQ and polling completion, reset GPIO pulse on recovery paths, adapter numbering, and transfer behavior against devices that NACK or hold SI low.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pca-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-piix4.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-piix4.c

Purpose: this PCI driver supports the PIIX4-compatible SMBus host controller family across Intel, ServerWorks, ATI, AMD, and Hygon chipsets. It registers one or more `i2c_adapter` instances that expose SMBus quick, byte, byte-data, word-data, and block-data transactions. Newer SB800/Hudson/KernCZ style chips support multiplexed main ports and an auxiliary port.

Important APIs, types, and functions: `struct i2c_piix4_adapdata` stores the SMBus base address, SB800 port metadata, IMC notification flag, and optional MMIO config. `piix4_setup()` handles legacy PCI config registers, DMI blacklists, forced enable/address options, ACPI region checks, and I/O region reservation. `piix4_setup_sb800()` and `piix4_setup_sb800_smba()` locate SB800-style bases through indexed I/O or FCH MMIO and configure port-selection metadata. Exported helpers `piix4_sb800_region_request()`, `piix4_sb800_region_release()`, `piix4_sb800_port_sel()`, and `piix4_transaction()` are shared through the `PIIX4_SMBUS` namespace. `piix4_access()` translates SMBus operations into host registers; `piix4_access_sb800()` wraps it with region locking, semaphore acquisition, port selection, and optional IMC sleep/wakeup.

Control flow: PCI probe chooses SB800-style setup for newer ATI/AMD/Hygon IDs, otherwise legacy setup. It registers all main adapters, then probes possible auxiliary SMBus controllers while avoiding the aux path when ACPI ASF is present. Each adapter uses either `smbus_algorithm` or `piix4_smbus_algorithm_sb800`. A transaction programs address, command, data, and size registers, sets the start bit, polls `SMBHSTSTS` up to `MAX_TIMEOUT`, maps error bits to `-ETIMEDOUT`, `-EIO`, or `-ENXIO`, clears status, and copies read data back. Remove walks registered adapters, deletes them, frees adapter data, and releases the shared I/O region once for main port 0 plus aux as needed.

State and persistence: global arrays track up to four main adapters and one auxiliary adapter, plus global SB800 port-selection register metadata and a ServerWorks delay flag. Per-adapter state is heap allocated. Hardware state includes SMBus enable bits, current SB800 selected port, semaphores, and transaction registers. No disk persistence exists, but module parameters can dangerously change hardware configuration for the module lifetime.

Dependencies and integration points: the driver depends on PCI IDs, DMI safety tables, ACPI resource checks/ASF detection, I/O port and MMIO region APIs, the I2C/SMBus core, and optional SPD write-enable registration on non-aux port 0. It also exports SB800 helpers for related drivers.

Risks: `force` and `force_addr` can enable or relocate SMBus hardware unsafely. DMI blacklist and IBM checks protect known EEPROM-corrupting systems. SB800 port selection must be restored after each access or firmware/other ports can break. IMC coordination failures degrade to warning-and-continue behavior, risking collisions on long block transactions. Adapter globals assume only one physical PIIX4-like PCI device.

Test signals: probe on legacy and SB800-class hardware, DMI blacklist refusal, force-address behavior only in controlled environments, block read/write with IMC active, multi-port enumeration, aux suppression when ASF exists, NACK/collision/timeout status mapping, exported helper users, and remove/unload resource cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-piix4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-piix4.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-piix4.h

Purpose: this header defines the register-offset macros and exported helper prototypes shared by the PIIX4/SB800 SMBus implementation and any companion code needing controlled SB800 port selection or transactions.

Important APIs, types, and functions: the `SMBHSTSTS`, `SMBHSLVSTS`, `SMBHSTCNT`, `SMBHSTCMD`, `SMBHSTADD`, `SMBHSTDAT0`, `SMBHSTDAT1`, `SMBBLKDAT`, `SMBSLVCNT`, `SMBSHDWCMD`, `SMBSLVEVT`, and `SMBSLVDAT` macros derive I/O port addresses from a local variable named `piix4_smba`. `PIIX4_BLOCK_DATA` defines the encoded controller operation for SMBus block transfers. `struct sb800_mmio_cfg` carries an optional mapped FCH MMIO pointer and a `use_mmio` selector. Function declarations expose `piix4_sb800_port_sel()`, `piix4_transaction()`, `piix4_sb800_region_request()`, and `piix4_sb800_region_release()`.

Control flow: there is no executable control flow in the header, but the macro design intentionally requires callers to have a `piix4_smba` variable in scope. The region request/release prototypes define the expected bracket around SB800 indexed or MMIO access, while `piix4_sb800_port_sel()` is used to change and restore multiplexed SMBus port state around a transaction.

State and persistence: `struct sb800_mmio_cfg` is transient per caller and points to mapped MMIO only while the region is held. The macros do not store state; they compute port addresses for inb/outb operations.

Dependencies and integration points: it includes `linux/types.h` and expects Linux `struct device` and `struct i2c_adapter` declarations through including translation units. The helper functions are exported from `i2c-piix4.c` in the `PIIX4_SMBUS` namespace.

Risks: macro dependence on an in-scope `piix4_smba` name is easy to misuse and cannot be type-checked. Callers must pair region request/release and restore previous SB800 port selection. The header exposes low-level register operations, so misuse can collide with firmware or other controllers.

Test signals: build coverage for all including files, namespace symbol resolution, sparse/compiler warnings around missing declarations, and runtime tests that region request/release and port selection are paired correctly by users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-piix4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pnx.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pnx.c

Purpose: this platform driver supports Philips/NXP PNX IP3204-style I2C controllers. It implements a full interrupt-driven `i2c_algorithm` with START/STOP generation, byte transmit/receive through FIFOs, timeout/reset handling, clock divider programming, OF binding, and suspend/resume clock control.

Important APIs, types, and functions: `struct i2c_pnx_mif` carries per-transfer return code, mode, completion, buffer pointer, remaining length, and receive-order count. `struct i2c_pnx_algo_data` stores MMIO base, transfer state, last-message flag, clock, adapter, IRQ, and timeout. `i2c_pnx_start()`, `i2c_pnx_stop()`, `i2c_pnx_master_xmit()`, and `i2c_pnx_master_rcv()` implement the core state machine. `i2c_pnx_interrupt()` dispatches arbitration failure, NACK, transmit-data-needed, and receive-data events. `i2c_pnx_xfer()` is the adapter transfer entry point.

Control flow: probe maps registers, enables the clock, calculates clock high/low dividers from `clock-frequency`, resets the controller, requests IRQ, and adds a numbered adapter. A transfer resets active/stale bus state, iterates messages, rejects ten-bit addresses, initializes `mif`, enables master interrupts, writes START and address, then waits for completion. TX interrupts push bytes and attach STOP to the final byte of the last message; RX uses dummy writes to clock data into the receive FIFO and NACK/STOP on the final byte. Timeout disables interrupts, resets the controller, and returns `-EIO`. After all messages, stale active/FIFO/NACK state triggers reset cleanup.

State and persistence: transfer state lives in `mif` and is cleared after each `i2c_pnx_xfer()`. Adapter and clock state persist for device lifetime. Runtime PM-like simple suspend/resume only disables/enables the clock; register contents are not fully reinitialized on resume in this file.

Dependencies and integration points: it uses platform resources, OF compatible `nxp,pnx-i2c`, Linux clocks, completions, IRQs, MMIO, and I2C core registration. `subsys_initcall()` ensures this adapter is available before USB initialization.

Risks: only 7-bit addressing is supported. Busy-bus and FIFO cleanup rely on reset and fixed timeouts. STOP wait in interrupt context uses a tight microsecond loop. Clock divider math clamps high values but does not validate all low-frequency timing corners beyond the clamp. Resume only enables the clock, so external reset or lost register state could require additional reconfiguration.

Test signals: transfer tests for read, write, zero-length write, multi-message sequences, NACK, arbitration loss, busy bus at start, timeout recovery, clock-frequency variants, suspend/resume transfer after clock cycling, and early boot ordering with dependent devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pnx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-powermac.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-powermac.c

Purpose: this driver bridges Apple PowerMac low-level I2C buses (`pmac_i2c_bus`) into Linux `i2c_adapter` instances. It supports legacy Apple Keywest, PMU, and SMU bus types, implements SMBus and single-message I2C transfers through `pmac_i2c_*` firmware/platform calls, and performs custom child-device registration for Apple device-tree quirks.

Important APIs, types, and functions: `i2c_powermac_smbus_xfer()` maps SMBus quick, byte, byte-data, word-data, block-data, and I2C-block-data operations to `pmac_i2c_open()`, `pmac_i2c_setmode()`, and `pmac_i2c_xfer()`. `i2c_powermac_xfer()` handles only one generic I2C message, enforced by `i2c_powermac_quirks.max_num_msgs = 1`. `i2c_powermac_get_addr()`, `i2c_powermac_get_type()`, `i2c_powermac_register_devices()`, and `i2c_powermac_add_missing()` translate Apple OF child nodes into `i2c_board_info` and instantiate clients with `MAC,`-prefixed modaliases.

Control flow: probe receives a `pmac_i2c_bus` as platform data, gets the preallocated adapter from the low-level bus layer, names it according to bus type/channel, assigns algorithm and quirks, clears `of_node` to avoid standard child auto-registration, adds the adapter, restores the OF node, then manually registers children. Transfers open the low-level bus, set mode (`std`, `stdsub`, or `combined`), execute the transfer, log errors with NACKs at debug level, and always close the bus.

State and persistence: adapter storage is owned by the pmac low-level layer and is zeroed on remove after `i2c_del_adapter()`. Per-transfer state is local. Device registration intentionally keeps interrupt mappings allocated because other consumers may have used direct DT lookup.

Dependencies and integration points: it depends on PowerMac-specific `<asm/pmac_low_i2c.h>`, OF node parsing, OF IRQ mapping, platform devices, and I2C core client creation. It deliberately avoids generic I2C driver modaliases for Apple thermal/audio devices unless those drivers are MAC-aware.

Risks: SMBus block read semantics are noted as broken relative to the expected SMBus API because returned length handling is not standard. Generic I2C supports only a single message, so repeated-start I2C users must use SMBus-like paths or fail. Child registration contains Apple-specific address/type workarounds and may miss unknown nodes. Remove zeroes shared adapter memory, which assumes no users remain after adapter deletion.

Test signals: PowerMac boot enumeration, child client creation for DT nodes, Onyx audio fallback probing, single-message I2C read/write, SMBus word endian behavior, block operation consumers, and refusal of ten-bit or multi-message generic I2C transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-powermac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa-pci.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa-pci.c

Purpose: this built-in PCI glue driver exposes Intel CE4100 PCI I2C controllers as three platform devices consumed by the main PXA I2C platform driver. CE4100 hardware is similar enough to PXA I2C to reuse `i2c-pxa.c`, but each PCI BAR represents a separate controller and target/slave mode is unsupported.

Important APIs, types, and functions: `struct ce4100_devices` stores the three created platform devices. `add_i2c_device()` builds a `struct i2c_pxa_platform_data`, two resources (MMIO and IRQ), locates the matching child DT node for the BAR, reads optional `fast-mode`, allocates a `platform_device` named `ce4100-i2c`, attaches resources and platform data, and registers it. `ce4100_i2c_probe()` enables the PCI function with `pcim_enable_device()`, requires a device tree node, allocates state, and creates devices for all three BARs.

Control flow: PCI probe performs managed PCI enable, validates OF presence, allocates `ce4100_devices`, then loops over BARs 0..2. Each BAR is matched against child OF `reg` resources by start, end, and flags. If any platform-device registration fails, previously created devices are unregistered and the state object is freed. Successful probe stores state with `pci_set_drvdata()`. There is no remove callback because the driver is built in via `builtin_pci_driver()`.

State and persistence: state is limited to the allocated list of platform-device pointers and a static incrementing `devnum` used for platform IDs. The generated platform devices hold the resource and pdata copies for the PXA driver lifetime.

Dependencies and integration points: it depends on PCI ID `8086:2e68`, OF child address translation, platform-device registration, and `linux/platform_data/i2c-pxa.h`. It integrates with `i2c-pxa.c` through the platform device name `ce4100-i2c` and `REGS_CE4100` platform ID entry.

Risks: probe fails without a DT node or if any BAR cannot be matched to a child node. All child controllers share the same PCI IRQ. There is no hot-unplug/remove cleanup path, acceptable only for built-in/non-hotpluggable assumptions. The static `devnum` is global and monotonically increasing.

Test signals: CE4100 boot should create three `ce4100-i2c` platform devices, match each BAR to a DT child, propagate `fast-mode`, share IRQ resources correctly, and unwind all earlier devices if one BAR setup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa.c

Purpose: this is the main I2C adapter driver for Intel/Marvell PXA-style controllers, including PXA2xx, PXA3xx power I2C, CE4100, PXA910/MMP TWSI, and Armada 3700 variants. It supports interrupt-driven master transfers, optional polling mode, optional slave mode, high/fast mode configuration, GPIO/pinctrl bus recovery, OF and platform-data probing, and suspend/resume.

Important APIs, types, and functions: `struct pxa_i2c` is the central state object containing message pointers, indices, wait queue, spinlock, adapter, clock, optional slave client, register pointers, feature flags, timing masks, bus recovery data, and reset-before-transfer flag. Register layouts are selected through `pxa_reg_layout` by OF or platform ID. Master flow is implemented by `i2c_pxa_wait_bus_not_busy()`, `i2c_pxa_set_master()`, `i2c_pxa_start_message()`, `i2c_pxa_irq_txempty()`, `i2c_pxa_irq_rxfull()`, `i2c_pxa_handler()`, `i2c_pxa_do_xfer()`, and retry wrapper `i2c_pxa_internal_xfer()`. Polling mode reuses the IRQ handler through `i2c_pxa_do_pio_xfer()`. Slave callbacks use `i2c_slave_event()` when `CONFIG_I2C_PXA_SLAVE` is enabled.

Control flow: probe maps registers, gets IRQ and clock, initializes optional recovery, reads DT or platform data, selects register offsets and algorithms, enables the clock, requests IRQ unless polling, resets the controller (or defers reset on Armada 3700 with recovery), and registers a numbered adapter. A normal IRQ transfer waits for bus idle, switches to master, optionally sends high-speed master code, initializes message state under lock, sends address/start, then waits up to five seconds for the interrupt handler to clear `msg_num`. The IRQ handler clears pending sources, services slave address/stop events, and in master mode advances TX/RX byte state until completion or error. Errors map to retry, no-slave, bus-error, or NAK codes and are retried according to adapter retries.

State and persistence: transfer progress is stored in `msg`, `msg_num`, `msg_idx`, `msg_ptr`, and IRQ debug logs. Persistent per-device state includes register layout, mode flags, recovery GPIO/pinctrl handles, and optional slave address. Suspend disables the clock at noirq; resume enables it and resets the controller. No disk persistence exists.

Dependencies and integration points: it depends on Linux platform/OF matching, clocks, IRQs, pinctrl, GPIO descriptors, I2C core, optional I2C slave core, and platform data. `i2c-pxa-pci.c` creates CE4100 platform devices that bind here. Recovery uses generic SCL recovery when both pinctrl states and SCL/SDA GPIOs are available.

Risks: the state machine is interrupt-sensitive and must handle spurious ALD, slave/master interleaving, NOSTART messages, zero-length messages, and timeout recovery. Optional slave mode disables GPIO bus recovery because ownership is ambiguous. Armada 3700 recovery/reset ordering is fragile enough to require delayed reset. PIO mode repeatedly invokes the IRQ handler and can diverge from hardware interrupt timing. Incorrect register-layout selection corrupts controller accesses.

Test signals: master read/write and repeated-start sequences on each supported layout, PIO and IRQ modes, NOSTART and protocol-mangling users, high/fast mode, no-slave and NAK retries, bus recovery with pinctrl/GPIOs, slave read/write events, suspend/resume transfers, and CE4100 platform glue integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-pxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qcom-cci.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qcom-cci.c

Purpose: this driver exposes Qualcomm Camera Control Interface controllers as one or two I2C adapters. CCI is queue-command based and intended for camera sensor/control traffic with small transfer limits. The driver programs master timing parameters for standard, fast, or fast-plus mode, loads write/read commands into per-master queues, waits for report/read-done interrupts, and integrates with runtime PM.

Important APIs, types, and functions: `struct cci` owns the MMIO base, IRQ, match data, clock bulk, and two possible `struct cci_master` objects. `struct cci_data` describes number of masters, queue sizes, adapter quirks, and per-speed `struct hw_params`. `cci_isr()` clears/handles reset, read-done, queue-report, halt-ack, and error interrupts. `cci_reset()`, `cci_halt()`, and `cci_init()` manage controller state and timing registers. `cci_i2c_write()` and `cci_i2c_read()` load queue commands and consume read FIFO data. `cci_xfer()` wraps multi-message transfers with `pm_runtime_get_sync()` and `pm_runtime_put_autosuspend()`.

Control flow: probe allocates the controller, reads match data, iterates available child nodes as masters, configures each adapter and speed mode from `clock-frequency`, maps MMIO, obtains all clocks, enables clocks, requests IRQ, resets and initializes the controller, enables runtime PM, and registers each configured master adapter. Transfers validate queue emptiness, write `SET_PARAM` and `READ`/`WRITE` commands to queue 1 or 0 respectively, add report commands for writes, start the queue, wait for completion, and return `num` on success. Read completion checks the expected read word count and discards the first status/metadata byte before copying data.

State and persistence: per-master completion and status persist for adapter lifetime. The controller timing registers are reprogrammed during init and runtime resume. Runtime suspend disables all clocks; resume enables clocks and calls `cci_init()`. No persistent storage exists.

Dependencies and integration points: it depends on platform/OF child nodes, clock bulk APIs, completions, IRQs, runtime PM, and I2C adapter quirks. OF compatibles select v1, v1.5, v2, or msm8953 timing/quirk tables. Child `reg` selects master index and child `clock-frequency` selects bus mode.

Risks: transfer sizes are limited by quirks (`max_write_len` around 10/11 and `max_read_len` 12), queue size, and the local fixed `load[12]` write buffer. Queue validation returns `-EINVAL` when full. Timeouts reset and reinitialize the whole controller. Error handling halts queues and maps NACK to `-ENXIO`, other CCI errors to `-EIO`. Probe error paths must carefully release OF node references for registered masters.

Test signals: probe with one-master and two-master compatibles, per-child clock-frequency modes, max-length write/read limits, NACK/error IRQ mapping, queue timeout reset/reinit path, runtime autosuspend/resume followed by transfer, and remove halting each master.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qcom-cci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qcom-geni.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qcom-geni.c

Purpose: this driver supports Qualcomm GENI Serial Engine I2C controllers, including normal FIFO/SE-DMA operation, GPI DMA operation when FIFO is disabled, and the I2C Master Hub variant. It provides runtime-PM-managed I2C adapters with clock-counter programming, interconnect bandwidth voting, DMA buffer handling, interrupt-driven completions, and system-suspend adapter gating.

Important APIs, types, and functions: `struct geni_i2c_dev` stores the GENI SE wrapper, IRQ, error state, adapter, current message, FIFO counters, clocks, DMA channels, GPI multi-descriptor state, and runtime suspend flag. Clock maps in `geni_i2c_clk_map_19p2mhz` and `_32mhz` feed `qcom_geni_i2c_conf()`. `geni_i2c_irq()` handles GENI master IRQs, FIFO watermarks, DMA IRQ status, error decoding, and transfer completion. FIFO/SE-DMA messages use `geni_i2c_rx_one_msg()` and `geni_i2c_tx_one_msg()`. GPI mode uses `geni_i2c_gpi_xfer()`, `geni_i2c_gpi()`, DMA callbacks, and multi-descriptor unmap/timeout helpers. `geni_i2c_xfer()` selects GPI or FIFO path after runtime resume and configuration.

Control flow: probe maps the SE registers, obtains optional core and SE clocks, reads `clock-frequency`, gets IRQ with `IRQF_NO_AUTOEN`, initializes interconnect paths, powers resources on, validates or loads GENI I2C firmware, chooses GPI DMA if FIFO is disabled or FIFO/SE-DMA otherwise, initializes packing/FIFO watermarks, powers resources back off, enables runtime PM, and registers the adapter. A transfer resumes resources, programs SCL counters, executes each message in FIFO/SE-DMA or GPI mode with STOP_STRETCH between messages, then autosuspends. IRQs populate RX FIFO data, feed TX FIFO data, clear DMA/GENI statuses, and complete on done/abort/DMA completion.

State and persistence: persistent state includes selected clock map, DMA mode, DMA channels, interconnect paths, and adapter. Per-transfer state includes `cur`, `cur_wr`, `cur_rd`, `dma_buf`, `xfer_len`, `dma_addr`, `err`, and GPI multi-descriptor counters. Runtime suspend disables IRQ, resources, core clock, and interconnect; resume restores them and enables IRQ. Shutdown marks the adapter suspended so late clients fail quickly.

Dependencies and integration points: it depends on Qualcomm GENI SE helpers, DMA engine/GPI DMA config, I2C DMA-safe buffer helpers, PM runtime, ACPI/OF matching, clocks, interconnect, and platform devices. Compatibles include `qcom,geni-i2c` and `qcom,geni-i2c-master-hub`; ACPI IDs include `QCOM0220` and `QCOM0411`.

Risks: DMA paths are complex and require exact unmap behavior on partial completion, errors, and multi-descriptor write transfers. Unsupported `clock-frequency` fails probe. Timeout paths must abort commands and reset DMA FSMs to avoid wedged engines. `pm_runtime_get_sync()` failure marks the device suspended. GPI write optimization excludes read messages; future read BEI optimization is explicitly TODO. IRQ disabled initially and runtime-managed ordering must be correct.

Test signals: FIFO read/write, SE-DMA fallback and DMA-safe buffer thresholds, GPI DMA read/write and multi-write descriptors, NACK/protocol/arbitration/overrun errors, timeout abort and DMA FSM reset, runtime autosuspend/resume, system suspend noirq adapter marking, ACPI and OF probe, and invalid frequency rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qcom-geni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qup.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qup.c

Purpose: this driver supports Qualcomm QUP I2C controllers in v1 and v2 hardware forms. It implements FIFO/block programmed I/O, optional BAM DMA for v2 transfers, runtime PM clock/interconnect management, ACPI/OF probing, adapter quirks, SMBus emulation minus quick command, and mode-specific tag generation for I2C protocol sequencing.

Important APIs, types, and functions: `struct qup_i2c_dev` holds MMIO, clocks, interconnect path, adapter, FIFO/block sizes, timing, current message, error flags, DMA/BAM resources, completion, and function pointers for version-specific FIFO handlers. `struct qup_i2c_block` tracks per-block transfer lengths, tag buffers, FIFO packing state, and read/write progress. `qup_i2c_interrupt()` services QUP operational flags, FIFO/block service requests, and error flags. v1 paths use `qup_i2c_xfer()`, `qup_i2c_conf_v1()`, `qup_i2c_write_tx_fifo_v1()`, and `qup_i2c_read_rx_fifo_v1()`. v2 paths use `qup_i2c_xfer_v2()`, `qup_i2c_xfer_v2_msg()`, `qup_i2c_set_tags()`, `qup_i2c_conf_xfer_v2()`, and BAM helpers.

Control flow: probe selects v1 or v2 by compatible, reads bus frequency or module override, optionally requests DMA channels for v2, maps MMIO, gets IRQ, obtains clocks or ACPI source clock, resets hardware, requests IRQ with `IRQF_NO_AUTOEN`, derives FIFO/block sizes from `QUP_IO_MODE`, computes clock divisors and transfer timeout, enables runtime PM, and registers the adapter. v1 transfers reset the core, configure I2C mini-core, then process each message separately in FIFO/block mode. v2 transfers determine whether to use DMA based on total length and vmalloc buffers, reset/configure v2 tags, then either schedule BAM descriptors for all messages or run each message/block with reconfiguration during run.

State and persistence: persistent state includes FIFO/block capacities, clock divisor, source clock, DMA channel/tag buffers, interconnect current vote, and adapter quirks. Per-transfer state includes `msg`, `pos`, `is_last`, `is_smbus_read`, error flags, block counters, and `use_dma`. Runtime suspend disables clocks, resets state, enables clock auto-gate, drops interconnect vote, and disables pclk; resume re-enables clocks.

Dependencies and integration points: it depends on platform, OF/ACPI, clock, interconnect, DMA engine, scatterlists, PM runtime, I2C core, and Qualcomm QUP register semantics. OF compatibles distinguish `qcom,i2c-qup-v1.1.1`, `v2.1.1`, and `v2.2.1`; ACPI uses `QCOM8010`. The module parameter `scl_freq` overrides firmware bus frequency.

Risks: v2 BAM DMA has many descriptor, tag-buffer, scatterlist, timeout, and flush edge cases. The driver avoids DMA for vmalloc buffers. SMBus block read is special-cased as a two-phase read with length validation. Interrupts are enabled only during transfers and must be disabled on every exit. Clock divisor math rejects frequencies above fast-mode-plus but still depends on source-clock accuracy. Remove disables IRQ and clocks before deleting adapter, which should be considered against in-flight transfer ordering.

Test signals: v1 and v2 probe, FIFO and block mode thresholds, v2 BAM DMA for long transfers, vmalloc-buffer no-DMA fallback, SMBus block read length and `-EPROTO`, NACK mapping to `-ENXIO`, QUP core error mapping to `-EIO`, timeout/reset/flush paths, runtime autosuspend/resume, ACPI source-clock property, and `scl_freq` override.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-qup.c -->
