# Research: subset-b-004570

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600.c

## Purpose
This file implements the Linux netdev SPI driver for the Microchip ENCX24J600 Ethernet controller. It binds as an SPI driver named `encx24j600`, allocates an Ethernet netdev, initializes the chip through the ENCX24J600 regmap layer, moves frames through the chip SRAM, handles the interrupt line, and exposes basic ethtool operations.

## Important APIs, Types, and Functions
The central private state is `struct encx24j600_priv`, which holds the `net_device`, a device-access mutex, the regmap/SPI context from `encx24j600_hw.h`, a single outstanding `tx_skb`, a kthread worker, RX cursor `next_packet`, link configuration, RX filter mode, and message level. Register helpers `encx24j600_read_reg`, `encx24j600_write_reg`, `encx24j600_update_reg`, `encx24j600_read_phy`, and `encx24j600_write_phy` wrap regmap access and log failures. Raw SRAM access goes through `encx24j600_raw_read` and `encx24j600_raw_write`, protected by the regmap context mutex.

Netdev entry points are collected in `encx24j600_netdev_ops`: `encx24j600_open`, `encx24j600_stop`, `encx24j600_tx`, `encx24j600_set_multicast_list`, `encx24j600_set_mac_address`, `encx24j600_tx_timeout`, and `eth_validate_addr`. Ettool support includes register dump, driver info, message level, and link settings.

## Control Flow
Probe allocates the netdev, installs driver data, configures default 100/full autoneg settings, initializes the ENCX24J600 regmaps, resets and initializes hardware, starts a kthread worker for TX and RX-filter reconfiguration, reads the MAC address from MAADR registers, registers the netdev, then validates the device ID from `EIDLED`.

Open requests a threaded falling-edge IRQ, disables hardware, reinitializes MAC/PHY/TX/RX registers, enables interrupts/RX, and starts the queue. Stop stops the queue and frees the IRQ. TX is serialized by stopping the netdev queue and storing one `tx_skb`; the kthread worker copies the frame into SRAM via `WGPDATA`, programs `ETXST`/`ETXLEN`, and issues `SETTXRTS`. TX completion is reported by `TXIF` or `TXABTIF` in the ISR, which frees the skb, updates stats, and wakes the queue.

The threaded ISR disables chip interrupts, samples `EIR`, handles link changes, TX completion, RX aborts, and packet interrupts, then reenables interrupts. RX drains the hardware packet count from low `ESTAT`, reads each receive-status vector from `RRXDATA`, validates `RSV_RXOK` and length, allocates an skb, copies payload bytes from RX SRAM, submits it with `netif_rx`, advances `next_packet`, decrements the packet counter, and updates `ERXTAIL`.

## State and Persistence
Persistent runtime state is in `encx24j600_priv`: link mode, queue state, `tx_skb`, RX SRAM cursor, enabled flag, and RX filter mode. Hardware state is entirely register/SRAM based and rebuilt during probe/open. The driver does not persist configuration outside the kernel object; MAC changes update `dev_addr` and hardware registers only while the interface is down.

## Dependencies and Integration Points
This driver depends on SPI, regmap, netdev, ethtool, kthread worker, IRQ, and SKB APIs. It depends on `encx24j600_hw.h` for register constants and on `devm_regmap_init_encx24j600` plus raw SPI helpers implemented outside this file. It integrates with the kernel networking stack through `register_netdev`, `netif_carrier_on/off`, `netif_rx`, and ethtool link settings.

## Risks
The design permits only one outstanding TX skb; correctness relies on stopping the queue before setting `tx_skb` and waking it only after completion. `encx24j600_tx_complete` calls `BUG()` if completion arrives without an skb, making interrupt ordering bugs severe. `encx24j600_stop` frees the IRQ but does not explicitly disable hardware/RX or flush queued kthread work, so teardown and close paths deserve attention. The RX path sets `CHECKSUM_COMPLETE` without calculating or storing a checksum value. Autoneg polling uses busy `cpu_relax` loops until jiffies timeout, which can be costly. `encx24j600_setlink` appears to assign `priv->speed = (speed == SPEED_100)` in the disabled path, storing a boolean instead of `SPEED_10` or `SPEED_100`.

## Test Signals
Useful signals are SPI probe success, EIDLED device/revision match, `ip link set up/down`, carrier transitions on cable plug/unplug, TX completion interrupts, RX packet counts and stats, multicast/promiscuous filter changes, ethtool register dumps, and forced link-setting rejection while the interface is running.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600_hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600_hw.h

## Purpose
This header is the hardware contract for the ENCX24J600 family driver. It defines the SPI command opcodes, banked and unbanked SFR addresses, register bit masks, PHY registers, SRAM layout constants, receive-status-vector layout, and the regmap context shared by the main driver and regmap transport implementation.

## Important APIs, Types, and Functions
`struct encx24j600_context` stores the SPI device, normal register regmap, PHY regmap, regmap mutex, and currently selected register bank. The exported setup/API declarations are `devm_regmap_init_encx24j600`, `regmap_encx24j600_spi_write`, and `regmap_encx24j600_spi_read`. `struct rsv` describes the hardware RX status vector consumed by `encx24j600.c`: `next_packet`, `len`, and `rxstat`.

Key macro groups include single-byte commands like `SETETHRST`, `SETPKTDEC`, `SETTXRTS`, `ENABLERX`, `DISABLERX`, `SETEIE`, and `CLREIE`; register access commands like `RCR`, `WCR`, `BFS`, `BFC`, and raw buffer commands `RGPDATA`/`WGPDATA`/`RRXDATA`; banked register addresses such as `ETXST`, `ERXST`, `ERXTAIL`, `MACON1`, `MACON2`, `MAADR*`, and `EIE`; and bit definitions for `ESTAT`, `EIR`, `ECON1`, filters, MAC options, PHY status, and interrupt enables.

## Control Flow and State
The header itself has no executable control flow, but its layout dictates the driver sequence: select/register access via banked addresses, read/write PHY through a PHY regmap, split SRAM into TX and RX regions, and decode RX packets using `struct rsv` plus `RSV_GETBIT`. `RX_BUFFER_SIZE`, `SRAM_SIZE`, `ERXST_VAL`, `RXSTART_INIT`, and `RXEND_INIT` describe the receive ring region used by the runtime driver.

## Dependencies and Integration Points
It depends on Linux SPI, regmap, mutex, and device types being available through includers. The constants must match the external regmap implementation and the ENCX24J600 datasheet. The main driver depends on this header for all hardware register names and bit meanings.

## Risks
Many constants encode silicon-specific behavior; any mismatch corrupts packet memory or changes interrupt semantics. `MAX_FRAMELEN` is 1518 and used by the driver as a hard RX validation limit, so VLAN or jumbo frames are outside this implementation. Several defined constants are unused in the main driver, increasing the chance that future users assume untested coverage.

## Test Signals
Compile coverage validates macro availability. Runtime signals are successful reset using `EUDAST_TEST_VAL`, correct device ID extraction from `EIDLED`, stable RX cursor behavior around `RXSTART_INIT`/`RXEND_INIT`, and correct decode of RX error counters from `rxstat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/encx24j600_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/Kconfig

## Purpose
This Kconfig fragment defines `CONFIG_FDMA`, the build switch for the shared Microchip Frame DMA API.

## Important APIs and Integration
`config FDMA` is a boolean option presented as `"FDMA API"` only under `COMPILE_TEST`. Other Microchip switchcore drivers select it directly, so normal product builds are expected to enable it via dependent drivers rather than through a user-visible prompt.

## Control Flow and State
Kconfig has no runtime control flow. Its state is the build-time symbol `CONFIG_FDMA`, which controls whether `fdma/Makefile` builds `fdma.o`.

## Dependencies and Risks
The option has no explicit dependencies beyond optional visibility under `COMPILE_TEST`. The main risk is dependency hygiene: any driver that calls FDMA helpers must `select FDMA` or depend on it, otherwise link failures occur. Because the prompt is hidden outside compile testing, direct user configuration is intentionally limited.

## Test Signals
`allyesconfig`, `allmodconfig`, and `COMPILE_TEST` builds should include `fdma_api.o`. Drivers such as `lan966x` and `sparx5` selecting `FDMA` are the practical integration checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/Makefile

## Purpose
This Makefile builds the Microchip shared FDMA helper object when `CONFIG_FDMA` is enabled.

## Important Rules
`obj-$(CONFIG_FDMA) += fdma.o` creates the composite object, and `fdma-y += fdma_api.o` adds the implementation file. There are no conditional subfeatures.

## Control Flow, State, and Dependencies
The file participates only in kbuild. Its only state is the build-time `CONFIG_FDMA` symbol. It depends on the parent Microchip Ethernet Makefile descending into `fdma/`, which is guarded by the same symbol.

## Risks and Test Signals
The Makefile is intentionally minimal; the main risk is future source additions not being appended to `fdma-y`. Build tests with `CONFIG_FDMA=y` or a driver selecting FDMA should produce `fdma.o` and export the symbols from `fdma_api.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/fdma_api.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/fdma_api.c

## Purpose
This file implements the shared Microchip Frame DMA descriptor-control-block helper API. It initializes DCB/DB rings, uses caller-provided callbacks to populate hardware pointer fields, allocates backing memory either as coherent DMA or physical memory, and reports allocation sizes.

## Important APIs, Types, and Functions
The exported functions are `fdma_db_add`, `__fdma_dcb_add`, `fdma_dcb_add`, `fdma_dcbs_init`, `fdma_alloc_coherent`, `fdma_alloc_phys`, `fdma_free_coherent`, `fdma_free_phys`, `fdma_get_size`, and `fdma_get_size_contiguous`. The internal `__fdma_db_add` writes a DB status value then calls a dataptr callback. `__fdma_dcb_add` initializes all DBs for a DCB, updates the previous `last_dcb->nextptr` through a nextptr callback, marks the new DCB as last, invalidates its next pointer, and sets its info.

## Control Flow
Callers initialize an `fdma` object with dimensions and callbacks, compute and set `fdma->size`, allocate memory, and call `fdma_dcbs_init`. Initialization sets `last_dcb`, `db_index`, and `dcb_index` to the start of the ring, then adds every DCB. Each added DCB fills every DB data pointer and links the prior DCB to the new DCB. The last initialized DCB remains with `FDMA_DCB_INVALID_DATA` as its next pointer, making later additions or consumer logic responsible for ring progression.

## State and Persistence
The mutable state is all in `struct fdma`: DCB memory, `dma`, `size`, indices, counts, DB size, channel ID, and callbacks. Memory lifetime is explicit via allocation/free helpers. No persistent storage exists beyond the allocated descriptor area shared with hardware.

## Dependencies and Integration Points
This file depends on DMA mapping, `kzalloc`, `virt_to_phys`, alignment macros, and the layout from `fdma_api.h`. It exports GPL symbols for Microchip switch drivers. Users must provide correct `dataptr_cb` and `nextptr_cb` callbacks for the addressing mode they use.

## Risks
The helpers do not validate `n_dbs <= FDMA_DB_MAX`, index bounds, callback presence, or that `fdma->size` was set before allocation. `fdma_alloc_phys` uses `virt_to_phys` on `kzalloc` memory, which is suitable only for hardware paths expecting CPU physical addresses and not general DMA API semantics. Failed initialization may leave partially populated descriptor memory. Callback errors are returned but no rollback is attempted.

## Test Signals
Unit-like tests can instantiate small `fdma` objects with callbacks that record expected pointer values. Integration tests should verify descriptor linkage, DB status/data pointers, DMA-coherent allocation and free, contiguous size calculations, and build/link visibility for switchcore drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/fdma_api.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/fdma_api.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/fdma_api.h

## Purpose
This header defines the common data structures, bit encoders, inline helpers, callbacks, and function prototypes for Microchip Frame DMA descriptors.

## Important APIs, Types, and Functions
`struct fdma_db` stores one data pointer and status word. `struct fdma_dcb` stores a next pointer, info word, and up to `FDMA_DB_MAX` DBs. `struct fdma_ops` supplies the dataptr and nextptr callbacks. `struct fdma` contains caller private data, DCB memory, DMA base, allocation size, active DCB/DB indices, descriptor dimensions, channel ID, and callbacks.

Inline helpers advance and reset indices (`fdma_dcb_advance`, `fdma_db_advance`, `fdma_db_reset`), test descriptor state (`fdma_dcb_is_reusable`, `fdma_db_is_done`, `fdma_has_frames`, `fdma_is_last`), access current or indexed DCB/DB objects, decode DB length, set DCB length, compute default next pointers, and compute contiguous data buffer DMA/virtual addresses with `XDP_PACKET_HEADROOM`.

## Control Flow and State
The header supports ring-style consumption by keeping `dcb_index` and `db_index` in `struct fdma`. Callers inspect `fdma_has_frames`, process the current DB/DCB, advance indices, and use `fdma_dcb_is_reusable` when a DCB contains multiple DBs. The default pointer helpers assume a contiguous descriptor-and-buffer layout.

## Dependencies and Integration Points
It includes Linux bit, Ethernet, and type definitions, and uses DMA address types, `GENMASK`, `BIT`, `XDP_PACKET_HEADROOM`, and `PAGE_SIZE`-aligned allocation assumptions from the implementation. Switch drivers include this header, often with an include path from their Makefiles.

## Risks
Most helpers do no bounds checks, so bad indices corrupt adjacent descriptor memory. `fdma_dcb_len_set` overwrites `info` rather than masking in the length, which is safe only if callers intend to replace all info bits. Contiguous pointer helpers are valid only when DCBs and data buffers are allocated in the combined layout described by `fdma_get_size_contiguous`.

## Test Signals
Compile users should cover all inline helpers. Runtime tests should exercise multi-DB advancement, descriptor done detection, contiguous pointer arithmetic, XDP headroom alignment, and `FDMA_DCB_STATUS_*`/`FDMA_DCB_INFO_*` bit encoders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/fdma/fdma_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ethtool.c

## Purpose
This file implements ethtool support for the LAN743x PCIe Ethernet driver: EEPROM/OTP access, driver info, message levels, statistics, private flags, RSS hash configuration, hardware timestamp capability reporting, EEE, link settings, WOL, pause parameters, and register dumps.

## Important APIs, Types, and Functions
The exported object is `const struct ethtool_ops lan743x_ethtool_ops`. EEPROM/OTP helpers include legacy `lan743x_otp_*`/`lan743x_eeprom_*` paths and high-speed PCI11x1x `lan743x_hs_otp_*`/`lan743x_hs_eeprom_*` paths. `lan743x_hs_syslock_acquire` and `lan743x_hs_syslock_release` are exported through `lan743x_main.h` and protect shared Hearthstone system registers with a hardware lock plus local spinlock/refcount.

Stats support is table-driven through string arrays and register-address arrays. RSS support reads/writes `RFE_INDX` and `RFE_HASH_KEY`. Timestamp, EEE, link settings, WOL, and pause operations mostly delegate to PTP state or phylink.

## Control Flow
`get_eeprom_len`, `get_eeprom`, and `set_eeprom` choose EEPROM versus OTP based on `LAN743X_ADAPTER_FLAG_OTP`, and choose legacy versus high-speed register blocks using `adapter->is_pci11x1x`. Writes require magic values: `LAN743X_EEPROM_MAGIC` or `LAN743X_OTP_MAGIC`. High-speed EEPROM/OTP operations acquire/release the hardware syslock around setup and per-byte commands; command completion is polled with `readx_poll_timeout`.

Stats flow copies string names to ethtool buffers and reads hardware counters plus per-queue software frame counts. RSS flow maps the 128-entry indirection table as 32 dwords and the 40-byte Toeplitz key as 10 dwords. Register dump flow writes common CSR values and, when SGMII is enabled, reads a curated set of SGMII MMD registers using `lan743x_sgmii_read`.

## State and Persistence
Ettool can mutate adapter state: `msg_enable`, `adapter->flags` for OTP access selection, RSS registers, EEPROM/OTP contents, WOL option fields and SecureOn password, wakeup enablement, EEE settings through phylink, and pause settings. EEPROM/OTP writes persist on device media; OTP writes are one-time programming and irreversible.

## Dependencies and Integration Points
This file depends on `lan743x_main.h` register definitions and CSR accessors, phylink ethtool helpers, PTP clock state, PCI naming, netdev ethtool APIs, and PM support for WOL. `lan743x_main.c` installs `lan743x_ethtool_ops` during probe.

## Risks
`set_priv_flags` accepts arbitrary flags without masking to known private flags. EEPROM and OTP access are byte-at-a-time and can be slow; OTP writes are dangerous by nature. Some high-speed OTP error paths return while holding no obvious cleanup for prior state, so lock/power sequencing needs careful review on failures. WOL split between PHY and MAC is subtle, especially for `WAKE_MAGICSECURE`. Register dumps read SGMII registers that may fail; failures are represented as `0xFFFF`.

## Test Signals
Useful tests include `ethtool -i`, `ethtool -d`, `ethtool -S`, RSS get/set round trips, private flag toggling for OTP access, EEPROM read/write with correct and incorrect magic, WOL option validation, EEE get/set through phylink, pause parameter changes, and SGMII register dump on PCI11x1x SGMII devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ethtool.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ethtool.h

## Purpose
This header declares the LAN743x ethtool register-dump ABI used by `lan743x_ethtool.c` and exports the driver's ethtool operations table.

## Important APIs and Types
`LAN743X_ETH_REG_VERSION` identifies the register-dump format. The first enum indexes common Ethernet registers in the dump buffer, ending at `MAX_LAN743X_ETH_COMMON_REGS`. The second enum indexes SGMII registers, ending at `MAX_LAN743X_ETH_SGMII_REGS`. `extern const struct ethtool_ops lan743x_ethtool_ops` is consumed by `lan743x_main.c`.

## Control Flow and State
There is no runtime control flow in the header. Its enum ordering is persistent ABI-like state for ethtool register dump interpretation: `lan743x_get_regs` writes values into a `u32` array at these indexes and advertises version 1.

## Dependencies and Integration Points
The header includes ethtool declarations and is shared between main probe code and ethtool implementation. The enum names map directly to CSR and SGMII MMD reads in `lan743x_ethtool.c`.

## Risks
Adding or reordering enum members changes the register dump layout. The comments require new registers to be added above the max sentinel; tooling that decodes dumps must track `LAN743X_ETH_REG_VERSION`.

## Test Signals
`ethtool -d` should report a buffer length matching common registers plus SGMII registers when `adapter->is_sgmii_en` is true. Build coverage catches missing ethtool ops declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_ethtool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_main.c

## Purpose
This file is the main LAN743x/PCI11x1x PCIe Ethernet driver. It owns PCI enablement, CSR mapping/reset, interrupt setup, MDIO and SGMII access, MAC/RFE/DMAC initialization, TX/RX descriptor rings, NAPI polling, phylink integration, netdev operations, probe/remove/shutdown, and suspend/resume WOL programming.

## Important APIs, Types, and Functions
Externally visible functions are CSR accessors `lan743x_csr_read`/`lan743x_csr_write`, flow-control update `lan743x_mac_flow_ctrl_set_enables`, SGMII read `lan743x_sgmii_read`, and timestamp mode helpers referenced by PTP/ethtool. The file uses `struct lan743x_adapter` from `lan743x_main.h` as the top-level state container, with nested `lan743x_csr`, `lan743x_intr`, `lan743x_tx`, and `lan743x_rx` objects.

Key subsystems are: PCI setup (`lan743x_pci_init`, `lan743x_csr_init`), interrupts (`lan743x_intr_open/close`, `lan743x_intr_entry_isr`, TX/RX/shared handlers), MDIO/SGMII (`lan743x_mdiobus_*`, `lan743x_sgmii_*`, PCS power reset), MAC/RFE/DMAC setup (`lan743x_mac_init/open/close`, `lan743x_rfe_*`, `lan743x_dmac_init`), TX ring assembly/cleanup, RX buffer processing, phylink MAC callbacks, netdev ops, and PM/WOL routines.

## Control Flow
Probe allocates a multiqueue netdev sized for LAN743x or PCI11x1x, stores OF MAC if present, enables PCI memory access, maps BAR0, validates `ID_REV`, resets PHY, initializes hardware blocks, registers MDIO, attaches netdev and ethtool ops, enables checksum/TSO features, creates phylink, and registers the netdev.

Open first configures interrupts, then enables MAC, connects and starts phylink, opens PTP, enables RFE RSS, opens all RX rings, and opens the configured TX rings. Close reverses this: TX, RX, PTP, phylink, MAC, and interrupts. Xmit selects TX channel 0 for LAN743x or queue-mapped channels for PCI11x1x, then `lan743x_tx_xmit_frame` maps skb data/frags into descriptors, optionally adds LSO and timestamp bits, writes tail, and lets hardware run. TX NAPI cleans descriptors based on hardware head writeback, unmaps DMA, completes timestamped skbs, and wakes stopped queues.

RX open allocates descriptors, head writeback, and one skb/DMA buffer per descriptor, configures RX channel registers, enables NAPI and interrupts, starts DMAC, and enables FIFO flow control. RX NAPI processes descriptors until budget or no work. `lan743x_rx_process_buffer` handles multi-buffer frames through `skb_head`/`frag_list`, extension descriptors for timestamps, checksum status bits, FCS trimming, GRO submission, and descriptor reuse.

Interrupt setup prefers MSI-X, falls back to MSI, then legacy. Vector 0 starts shared; additional MSI-X vectors are assigned to TX/RX channels and removed from the shared mask. Flags encode whether status/enable bits are explicit, read-to-clear, or auto clear/set. A software interrupt self-test validates delivery.

Phylink creation chooses supported interfaces from chip ID, strap status, and MAC config: SGMII/1000BASE-X/2500BASE-X for PCI11x1x SGMII, GMII for LAN7430, MII for LAN7431 MII, otherwise RGMII. Link-up configures MAC speed/duplex, updates PTP latency, sets pause flow control, and wakes queues.

## State and Persistence
Runtime state persists in `adapter`: PCI device, mapped CSR base, interrupt vectors, MAC address, RX/TX rings, PTP, GPIO, MDIO, phylink, WOL fields, SGMII mode, hardware config saved for resume, and per-channel counters. Descriptor rings and head writebacks are DMA-coherent memory; skb buffers are streaming DMA mappings. Hardware counters are read on demand and reset by MAC counter reset during init. PM suspend saves PCI state, programs WOL if requested, and for PCI11x1x saves/restores `HW_CFG`.

## Dependencies and Integration Points
The file integrates with PCI, netdev, phylink, phylib/MDIO, NAPI, DMA mapping, PTP (`lan743x_ptp_*`), GPIO (`lan743x_gpio_init`), ethtool ops, OF MAC/PHY discovery, and PM. Register definitions and structures come from `lan743x_main.h`.

## Risks
TX/RX descriptor correctness is sensitive to DMA barriers, head/tail wrap, and cleanup on mapping failures. RX multi-buffer assembly can drop an in-progress frame on allocation failure and must keep descriptor reuse coherent. Interrupt flag combinations are complex across A0/B0/PCI11x1x and MSI-X/MSI/legacy paths. `lan743x_netdev_open` failure after `lan743x_ptp_open` but before RX/TX setup goes to `close_mac` rather than closing PTP/phylink in one path, which deserves review. Suspend/resume reinitializes hardware and reopens netdev while coordinating WOL and PHY state. MTU changes touch MAC RX live and require timeout checks.

## Test Signals
High-value tests are PCI probe/remove on all IDs, MSI-X/MSI/legacy interrupt delivery, software ISR self-test, iperf TX/RX with checksum/TSO, MTU changes, multicast/promiscuous filter behavior, RSS distribution, phylink modes including SGMII/1000BASE-X/2500BASE-X, PTP TX/RX timestamps, suspend/resume with WOL, and fault injection for DMA allocation/mapping failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_main.h

## Purpose
This header is the main LAN743x hardware and driver-state contract. It defines PCI IDs, CSR offsets and bit fields for MAC/RFE/DMAC/interrupt/PTP/SGMII/OTP/EEPROM/statistics blocks, channel counts, descriptor formats, ring state structures, adapter state, and cross-file function prototypes.

## Important APIs, Types, and Constants
Major constants include `DRIVER_NAME`, chip IDs for LAN7430/LAN7431/A011/A041, `ID_REV_IS_VALID_CHIP_ID_`, interrupt bits and vector flags, channel counts, max frame size, DMA descriptor spacing, TX/RX descriptor bit fields, and register offsets for all hardware blocks.

Important types are `struct lan743x_csr`, `struct lan743x_vector`, `struct lan743x_intr`, `struct lan743x_tx`, `struct lan743x_rx`, `enum lan743x_sgmii_lsd`, and `struct lan743x_adapter`. The adapter ties together netdev, mdiobus, PCI device, CSR state, interrupts, GPIO, PTP, MAC address, TX/RX rings, SGMII/syslock state, feature flags, phylink, and timestamp filter. Prototypes export CSR access, Hearthstone syslock, flow control, SGMII reads, and timestamp mode configuration to ethtool/PTP code.

## Control Flow and State
The header has no executable control flow, but it defines the state machine inputs used by `lan743x_main.c`: DMAC channel states, interrupt vector semantics, TX frame assembly flags, RX process results, and SGMII link-speed-duplex states. Ring structures store DMA-coherent descriptor bases, writeback head pointers, last head/tail indexes, NAPI instances, and skb bookkeeping.

## Dependencies and Integration Points
It includes phylink, phy, and `lan743x_ptp.h`, so it forms the bridge between the main driver, ethtool, PTP, GPIO, phylink, and MDIO logic. Register definitions must match the hardware manuals and the read/write sequences in `lan743x_main.c` and `lan743x_ethtool.c`.

## Risks
This file centralizes many bit masks and offsets; mistakes can silently program the wrong hardware block. Structure layout changes affect allocation and runtime behavior across multiple C files. `LAN743X_USED_*` compile-time constants limit enabled queues and have build-time guards against max values. Descriptor bit definitions and `DEFAULT_DMA_DESCRIPTOR_SPACING` must stay aligned with hardware requirements.

## Test Signals
Compile coverage catches missing declarations. Runtime validation comes from successful probe across supported device IDs, correct register dumps, working TX/RX ring operation, interrupt mode transitions, PTP and WOL behavior, SGMII mode setup, and statistics reads from the defined offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/lan743x_main.h -->
