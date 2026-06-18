# Research Group: subset-b-004342

This grouped report covers the AMD XGBE driver files requested for `subset-b-004342`. Each section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-ethtool.c

## Purpose
`xgbe-ethtool.c` exposes the AMD XGBE driver's ethtool control plane. It reports driver identity, link modes, pause settings, MMC and extended statistics, RSS settings, timestamp capability, SFP module EEPROM information, descriptor ring sizes, channel counts, and offline self-tests. It is mostly a validation and dispatch layer: it translates ethtool requests into updates on `struct xgbe_prv_data`, then calls PHY or hardware function pointers to apply the change.

## Important APIs, Types, And Functions
- `struct xgbe_stats` plus `XGMAC_MMC_STAT` and `XGMAC_EXT_STAT` map ethtool statistic names to offsets in `struct xgbe_prv_data`.
- `xgbe_get_strings`, `xgbe_get_ethtool_stats`, and `xgbe_get_sset_count` implement the stats and self-test string sets.
- `xgbe_get_link_ksettings` and `xgbe_set_link_ksettings` expose and update `pdata->phy.lks`, validating PHY address, autonegotiation, speed, and duplex.
- `xgbe_get_pauseparam` and `xgbe_set_pauseparam` map pause autoneg/TX/RX settings to link-mode advertisement bits.
- `xgbe_get_coalesce` and `xgbe_set_coalesce` expose RX interrupt watchdog and TX timer coalescing, with range checks against descriptor counts, RIWT limits, and jiffy granularity.
- RSS operations use `get_rxfh*`/`set_rxfh` and delegate table/key writes to `hw_if->set_rss_lookup_table` and `hw_if->set_rss_hash_key`.
- `xgbe_get_ts_info` advertises PTP hardware timestamp support and reports `ptp_clock_index` when a PHC is registered.
- `xgbe_get_module_info` and `xgbe_get_module_eeprom` delegate to `phy_if` for SFP information.
- `xgbe_set_ringparam` and `xgbe_set_channels` change descriptor and queue/channel geometry and trigger `xgbe_restart_dev` or `xgbe_full_restart_dev`.
- `xgbe_get_ethtool_ops` returns the file-local `struct ethtool_ops`.

## Control Flow
The netdev setup path assigns `netdev->ethtool_ops = xgbe_get_ethtool_ops()`. ethtool calls enter one of the handlers, obtain `pdata` via `netdev_priv`, validate user-provided values, update cached driver state, and optionally reconfigure live hardware. Link and pause changes call `phy_if.phy_config_aneg` when the interface is running. Coalescing changes immediately call the hardware coalescing hooks. Ring count changes restart the device if rounded descriptor counts differ. Channel count changes stage `new_rx_ring_count`/`new_tx_ring_count` and request a full restart.

## State And Persistence
State is kept in `struct xgbe_prv_data`: `phy.lks`, `phy.autoneg`, `phy.speed`, pause flags, RSS key/table, coalescing fields, descriptor counts, ring/channel counts, and debug message level. These values are runtime configuration, not durable storage; they persist while the netdev instance exists and are re-applied through restart paths when needed.

## Dependencies And Integration Points
This file depends on Linux ethtool/netdev APIs, timestamping constants, link-mode bit helpers from `xgbe.h`, hardware callbacks in `pdata->hw_if`, PHY callbacks in `pdata->phy_if`, and self-test callbacks from `xgbe-selftest.c`. It also depends on `xgbe-main.c` for netdev registration and on the PHY implementation files for validating speeds and serving module EEPROM requests.

## Risks
User-triggered channel or ring changes can restart the device and disrupt traffic. Coalescing accepts TX usecs after rounding, returning a netlink extended-ack message rather than a hard failure for granularity adjustment. Statistics are read by offset and cast to `u64`; the table must remain aligned with actual stat field widths. Pause advertising changes are subtle because symmetric/asymmetric pause uses bit combinations. Module EEPROM calls depend on PHY implementation support and can fail for non-SFP ports or down interfaces.

## Test Signals
Useful tests include `ethtool -i`, `ethtool -S`, `ethtool -k`, `ethtool -c/-C`, `ethtool -g/-G`, `ethtool -l/-L`, `ethtool -x/-X`, `ethtool --show-eee` if applicable, `ethtool --test offline`, and link-mode changes through `ethtool -s`. Kernel logs should be checked for validation messages and restart behavior after ring/channel changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-hwtstamp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-hwtstamp.c

## Purpose
`xgbe-hwtstamp.c` implements hardware timestamp register programming, TX/RX timestamp extraction, user timestamp filter configuration, and PTP clock initialization for the AMD XGBE MAC. It bridges Linux hwtstamp/PTP configuration to MAC timestamp control registers.

## Important APIs, Types, And Functions
- `xgbe_update_tstamp_time`, `xgbe_update_tstamp_addend`, and `xgbe_set_tstamp_time` write MAC timestamp update/init registers and poll completion bits.
- `xgbe_get_tstamp_time`, `xgbe_get_tx_tstamp`, and `xgbe_get_rx_tstamp` convert MAC timestamp registers or descriptor context fields into nanoseconds.
- `xgbe_config_tstamp` ORs timestamp control bits into `MAC_TSCR`.
- `xgbe_tx_tstamp` completes deferred TX timestamp delivery for `pdata->tx_tstamp_skb`.
- `xgbe_get_hwtstamp_settings` and `xgbe_set_hwtstamp_settings` implement the netdev hwtstamp get/set path.
- `xgbe_prep_tx_tstamp` marks outbound PTP packets for hardware timestamping and enforces one in-flight TX timestamp SKB.
- `xgbe_init_ptp` programs timestamp increments/addend and initializes system time from `ktime_get_real_ts64`.

## Control Flow
PTP registration is done from `xgbe-main.c`; timestamp hardware setup occurs when the device initializes or timestamping is requested. User hwtstamp settings are validated through the TX type and RX filter switches, translated into `MAC_TSCR` bits, written to hardware, and cached in `pdata->tstamp_config`. TX timestamping is prepared during packet transmit and completed asynchronously through `tx_tstamp_work`. RX timestamps are consumed from receive context descriptors when valid.

## State And Persistence
The file maintains `pdata->tstamp_config`, `pdata->tstamp_addend`, `pdata->tx_tstamp_skb`, and `pdata->tx_tstamp`. All are runtime state. `tstamp_lock` protects timestamp adjustment and TX timestamp SKB ownership. Hardware state lives in MAC timestamp registers and is reinitialized by `xgbe_init_ptp`.

## Dependencies And Integration Points
This code depends on MAC register macros from `xgbe-common.h`, `struct xgbe_prv_data` timestamp fields from `xgbe.h`, Linux hwtstamp/PTP APIs, SKB timestamp helpers, and version data flags such as `tx_tstamp_workaround` and `tstamp_ptp_clock_freq`. It integrates with `xgbe-ptp.c` for PHC operations and `xgbe-ethtool.c` for timestamp capability reporting.

## Risks
The polling loops must not silently miss stuck hardware; most paths log timeout errors but continue. `xgbe_update_tstamp_time` checks `count < 0` after a decrementing loop even though the loop exits at zero, so the timeout diagnostic condition is weaker than the addend/init paths. Only one TX timestamp SKB is tracked, so concurrent timestamp requests can be dropped by clearing the packet PTP attribute. Correct addend calculation depends on `ptpclk_rate` being initialized by platform/PCI probing.

## Test Signals
Test with `hwstamp_ctl`, `phc2sys`, `ptp4l`, and `ethtool -T`. Exercise TX and RX PTP filters, interface restart, link-speed-specific timestamp initialization, and error logs for timestamp init/addend timeouts. Packet capture or application-level PTP tests should confirm monotonic PHC behavior and valid TX/RX hardware timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-hwtstamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-i2c.c

## Purpose
`xgbe-i2c.c` implements the driver's private I2C master used mainly by the v2 PHY path for SFP EEPROM/GPIO access, SFP PHY-over-I2C access, and I2C-attached redrivers. It wraps the DesignWare-style I2C register interface behind `struct xgbe_i2c_if`.

## Important APIs, Types, And Functions
- `xgbe_i2c_abort`, `xgbe_i2c_set_enable`, `xgbe_i2c_enable`, and `xgbe_i2c_disable` control the I2C master and recover from disable failures.
- `xgbe_i2c_write` and `xgbe_i2c_read` drive FIFO fill/drain for the current `xgbe_i2c_op_state`.
- `xgbe_i2c_isr_bh_work`, `xgbe_i2c_isr`, and `xgbe_i2c_combined_isr` handle I2C interrupts and support both separate and combined IRQ routing.
- `xgbe_i2c_xfer` is the synchronous transfer API exposed through `i2c_if->i2c_xfer`.
- `xgbe_i2c_start`, `xgbe_i2c_stop`, and `xgbe_i2c_init` manage IRQ registration and controller setup.
- `xgbe_init_function_ptrs_i2c` fills `struct xgbe_i2c_if`.

## Control Flow
The PHY v2 start path starts I2C before SFP detection. Each transfer takes `pdata->i2c_mutex`, disables the controller, programs the target address and operation state, clears interrupts, enables the controller, and unmasks I2C interrupts. The TX-empty interrupt seeds read or write commands into the FIFO; RX-full drains read data; STOP or TX-abort completes `pdata->i2c_complete`. The caller waits up to one second and maps abort causes to `-ENOTCONN` or `-EAGAIN`.

## State And Persistence
Runtime state is in `pdata->i2c`: controller feature sizes, `started`, and a single active `op_state`. `pdata->i2c_complete` synchronizes interrupt completion with callers, and `pdata->i2c_mutex` serializes transfers. No state is persistent across device teardown.

## Dependencies And Integration Points
This file depends on XI2C register macros, Linux IRQ/workqueue/completion/mutex APIs, `system_bh_wq`, and `pdata->vdata->irq_reissue_support`. The primary consumers are `xgbe-phy-v2.c` SFP, external PHY, and redriver code. Platform and PCI probing supply `xi2c_regs` and the I2C IRQ.

## Risks
All transfers are serialized and use a fixed one-second timeout, which can delay link handling if hardware is wedged. Transfer completion relies on interrupts; incorrect IRQ routing or reissue behavior can stall operations. The FIFO logic assumes the controller is configured to avoid RX overflow. Error handling disables interrupts and controller state, but callers must tolerate `-ETIMEDOUT`, `-ENOTCONN`, `-EAGAIN`, and `-EIO` during SFP probing.

## Test Signals
Exercise SFP insertion/removal, EEPROM reads via `ethtool -m`, SFP GPIO signal changes, and redriver configuration on hardware using separate and combined IRQs. Kernel logs for "i2c operation timed out", TX abort diagnostics, and controller enable/disable failures are important regression signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-main.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-main.c

## Purpose
`xgbe-main.c` is the top-level module and netdev configuration file. It allocates `struct xgbe_prv_data`, initializes function-pointer tables, derives channel/queue counts, configures the net_device feature set, registers/unregisters the netdev and PTP clock, and registers both platform and PCI bus drivers at module load.

## Important APIs, Types, And Functions
- Module metadata and the `debug` module parameter establish driver identity and default message logging.
- `xgbe_default_config` seeds DMA, FIFO threshold, flow-control, PHY speed, and power defaults.
- `xgbe_init_all_fptrs` wires hardware, generic PHY, I2C, descriptor, and version-specific PHY implementation callbacks.
- `xgbe_alloc_pdata`/`xgbe_free_pdata` allocate and free an `alloc_etherdev_mq` netdev with private data.
- `xgbe_set_counts` reads hardware features and determines initial TX/RX rings and queues.
- `xgbe_config_netdev` performs reset, default configuration, DMA mask setup, PHY init, netdev ops/features setup, coalescing init, registration, PTP registration, and debugfs init.
- `xgbe_deconfig_netdev` reverses debugfs, PTP, netdev, and PHY registration.
- `xgbe_netdev_event` handles rename events for debugfs.
- `xgbe_mod_init`/`xgbe_mod_exit` register/unregister the notifier plus platform and PCI drivers.

## Control Flow
Bus-specific probe code allocates `pdata`, fills resources and version data, calls `xgbe_set_counts`, then calls `xgbe_config_netdev`. That routine resets hardware through `hw_if.exit`, applies defaults, configures DMA capabilities and descriptor counts, constrains channels by IRQ availability, initializes RSS, runs PHY init, assigns ops, sets netdev offload features, initializes coalescing, registers the netdev, registers PTP if available, and initializes debugfs. Module init registers platform first, then PCI; failures unwind in reverse.

## State And Persistence
`pdata` owns all runtime state: locks, completions, feature flags, rings, counts, PHY state, timestamping, work items, and resources. Defaults are in-memory only. `msg_enable` persists for the lifetime of the device and can be modified through ethtool. The netdev registration makes this runtime state visible to the networking stack.

## Dependencies And Integration Points
This file integrates all driver subsystems: hardware operations, descriptors, PHY/MDIO, I2C, ethtool, netdev ops, optional DCB, PTP, debugfs, platform probing, and PCI probing. It depends on bus-specific code to populate MMIO addresses, clocks, IRQs, MAC address, version data, and device property registers before `xgbe_config_netdev` runs.

## Risks
The order of initialization matters: function pointers and hardware features must be valid before count calculation and netdev setup. A failure after partial registration must unwind cleanly; this file delegates much of that to bus-specific devm/pcim cleanup and `xgbe_deconfig_netdev`. Feature flags must match hardware capabilities or the stack can hand unsupported traffic to the driver. Channel count logic depends on CPU count, hardware limits, and IRQ count.

## Test Signals
Module load/unload, PCI and platform probe/remove, netdev rename, PTP registration, debugfs creation, and feature advertisement through `ethtool -k/-i` are primary signals. Regression tests should include probe failure injection around PHY init and netdev registration, plus suspend/resume through the bus-specific files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-mdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-mdio.c

## Purpose
`xgbe-mdio.c` implements the common PHY/MDIO orchestration layer above version-specific PHY implementations. It manages Clause 37 and Clause 73 auto-negotiation, link status transitions, flow-control resolution, PHY start/stop/reset, and function-pointer export through `struct xgbe_phy_if`.

## Important APIs, Types, And Functions
- Module EEPROM wrappers `xgbe_phy_module_info` and `xgbe_phy_module_eeprom` delegate optional SFP support to the implementation.
- AN interrupt helpers configure and clear CL37/CL73 interrupt masks.
- Mode helpers (`xgbe_kr_mode`, `xgbe_kx_2500_mode`, `xgbe_sfi_mode`, etc.) set MAC speed and delegate PHY mode programming to `phy_impl.set_mode`.
- `xgbe_an73_*` and `xgbe_an37_*` functions implement auto-negotiation page handling, incompatible-link fallback, and completion/error handling.
- `xgbe_an_state_machine` serializes AN work under `pdata->an_mutex`.
- `xgbe_phy_config_aneg` and `xgbe_phy_reconfig_aneg` initialize mode, advertisement, interrupts, and AN state.
- `xgbe_phy_status` polls implementation link status, handles AN timeout/restart, sets carrier, and updates flow control and queues.
- `xgbe_phy_init`, `xgbe_phy_start`, `xgbe_phy_stop`, `xgbe_phy_reset`, and `xgbe_phy_exit` provide the generic PHY interface.
- `xgbe_init_function_ptrs_phy` fills `struct xgbe_phy_if`.

## Control Flow
Generic PHY init initializes AN work, reads FEC ability, calls the version-specific PHY init to populate supported link modes, copies supported to advertising, and seeds pause settings. Start calls implementation start, requests a separate AN IRQ when needed, chooses an initial supported mode, initializes AN registers, enables AN interrupts, and starts negotiation. AN IRQs schedule work; the state machine consumes pending AN bits and either completes, retries in another mode, starts KR training, or marks errors. The periodic PHY status path checks link state, waits for AN completion, applies negotiated mode, controls carrier, and stops/wakes TX queues on link changes.

## State And Persistence
The file maintains `pdata->an_result`, `an_state`, `kr_state`, `kx_state`, `an_int`, `an_status`, `an_start`, `kr_start_time`, `parallel_detect`, `fec_ability`, `phy_link`, `phy_speed`, and flow-control fields. It also owns `an_mutex`, `an_work`, `an_irq_work`, and optional `an_bh_work`. All state is runtime and reset on PHY reconfiguration or device teardown.

## Dependencies And Integration Points
This layer depends on version-specific implementations in `xgbe-phy-v1.c` and `xgbe-phy-v2.c` through `phy_impl`, hardware callbacks in `hw_if`, Linux MDIO definitions, netdev carrier/queue APIs, IRQ/workqueue APIs, and ethtool link mode helpers. `xgbe-ethtool.c` calls into `phy_config_aneg` and `phy_valid_speed`; `xgbe-main.c` invokes PHY init/exit; bus probes supply `an_irq`.

## Risks
AN logic is stateful and race-sensitive. IRQ masking, workqueue flushing, and `an_mutex` must prevent concurrent mode changes. Link timeout logic can restart AN; KR training adds a wait loop to avoid premature restart. Incorrect implementation callbacks can leave MAC speed and PHY mode mismatched. Link-down handling stops TX queues without resetting BQL, relying on descriptor cleanup. Failure to re-enable AN interrupts or reissue IRQs can stall negotiation.

## Test Signals
Test CL73 backplane negotiation, CL37 Base-X, CL37 SGMII, fixed-speed operation, incompatible-link fallback between KR/KX, KR training, pause resolution, link flap behavior, and external PHY/SFP modes through the v2 implementation. Kernel link messages, carrier state, queue wake/stop behavior, and `ethtool` link partner advertisement are useful observability points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-pci.c

## Purpose
`xgbe-pci.c` is the PCI bus binding for newer AMD XGBE devices. It maps PCI BARs, configures XPCS indirect addressing, reads port property registers, assigns MAC address/clock/DMA settings, configures MSI/MSI-X or single IRQs, registers the netdev, and handles PCI suspend/resume.

## Important APIs, Types, And Functions
- `xgbe_config_multi_msi` and `xgbe_config_irqs` allocate IRQ vectors and assign device, ECC, I2C, AN, and channel IRQs.
- `xgbe_pci_probe` performs the full PCI discovery and netdev enable path.
- `xgbe_pci_remove` deconfigures the netdev, frees IRQ vectors, disables hardware interrupts, and frees private data.
- `xgbe_pci_synchronize_irqs` drains IRQ handlers before suspend.
- `xgbe_pci_suspend` and `xgbe_pci_resume` handle power state transitions and PHY low-power mode.
- Version data instances `xgbe_v2a`, `xgbe_v2b`, and `xgbe_v3` select PHY v2 callbacks, XPCS access style, FIFO limits, timestamp behavior, ECC/I2C support, and workarounds.
- `xgbe_pci_init`/`xgbe_pci_exit` register and unregister the `pci_driver`.

## Control Flow
Probe allocates `pdata`, stores version data from the PCI ID table, enables the device, maps BARs, sets XGMAC/XPCS/property/I2C register pointers, determines XPCS window registers from the root AMD device ID, reads XPCS window definitions via SMN for v3 or MMIO for v2, enables PCI bus mastering and device interrupts, reads a valid MAC address, sets fixed PCI clock rates and DMA coherency values, reads port properties, computes counts and FIFO limits, configures IRQs, and calls `xgbe_config_netdev`. Suspend powers down the running netdev, disables interrupts, synchronizes IRQs, puts PCS in low power, disables bus mastering, saves config, and enters D3hot. Resume restores D0/config, re-enables the device and interrupts, clears low-power mode, powers up, and schedules restart if needed.

## State And Persistence
PCI probe populates runtime fields in `pdata`: BAR pointers, `pcidev`, property registers, XPCS window metadata, IRQ numbers/counts, clocks, DMA coherency settings, FIFO/channel limits, MAC address, and version-data workarounds. Suspend stores `lpm_ctrl`. PCI configuration state is saved/restored through the kernel PCI APIs.

## Dependencies And Integration Points
This file depends on Linux PCI APIs, SMN access from `xgbe-smn.h`, XPCS/window register macros, root AMD device IDs, and common netdev setup in `xgbe-main.c`. It uses PHY v2 implementation through version data. It also depends on power-management callbacks and the driver-wide `xgbe_powerdown`/`xgbe_powerup` paths.

## Risks
XPCS indirect window setup varies by platform and can fail if SMN access is unavailable on v3 hardware. The code mutates version-data workaround flags based on root device ID; because version data objects are static, this can affect later devices using the same object. IRQ allocation falls back from multi-vector to single-vector, changing ISR execution mode and channel capacity. Suspend must avoid IRQ handlers touching disabled hardware, hence explicit synchronization.

## Test Signals
Probe on all listed PCI IDs, MSI-X/MSI/single-IRQ fallback, valid/invalid MAC handling, SMN read failures, suspend/resume under traffic, and link restart after resume should be tested. Logs around XPCS window values, property registers, IRQ assignment, and "net device enabled" are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-phy-v1.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-phy-v1.c

## Purpose
`xgbe-phy-v1.c` implements the PHY backend for first-generation platform devices. It supports backplane-style KR at 10G and either KX at 1G or KX at 2.5G depending on the `amd,speed-set` property. It directly programs PCS and SerDes registers using platform-provided SerDes resources.

## Important APIs, Types, And Functions
- `struct xgbe_phy_data` stores the speed set and per-speed SerDes tuning arrays.
- Property names such as `amd,serdes-blwc`, `amd,serdes-cdr-rate`, `amd,serdes-pq-skew`, `amd,serdes-tx-amp`, `amd,serdes-dfe-tap-config`, and `amd,serdes-dfe-tap-enable` override default tuning.
- `xgbe_phy_kr_mode`, `xgbe_phy_kx_2500_mode`, and `xgbe_phy_kx_1000_mode` program PCS and SerDes speed-specific registers.
- `xgbe_phy_start_ratechange`/`xgbe_phy_complete_ratechange` coordinate SerDes rate changes and RX reset.
- `xgbe_phy_an_outcome` resolves CL73 AN result and pause/FEC/link-partner advertisement.
- `xgbe_phy_use_mode`, `xgbe_phy_get_mode`, `xgbe_phy_switch_mode`, and `xgbe_phy_valid_speed` expose mode policy to the common MDIO layer.
- `xgbe_phy_reset` performs PCS software reset with timeout.
- `xgbe_init_function_ptrs_phy_v1` fills the implementation callback table.

## Control Flow
Init allocates PHY data, reads `amd,speed-set`, loads optional SerDes arrays or defaults, builds supported link modes, and records `pdata->phy_data`. The common MDIO layer then chooses modes and starts CL73 negotiation. Mode changes set PCS type/speed, power-cycle PCS, assert SerDes ratechange, write speed/tuning fields, release ratechange, wait for RX/TX ready, and reset RX DFE. AN outcome reads local and partner advertisement registers to choose KR or KX and resolve pause.

## State And Persistence
Persistent-for-device runtime state is the allocated `struct xgbe_phy_data`, including speed-set and tuning arrays. Link advertisement state is stored in `pdata->phy.lks`; current mode is inferred from PCS `MDIO_CTRL2` rather than cached. There is no external PHY or SFP state in v1.

## Dependencies And Integration Points
This backend is selected by platform version data in `xgbe-platform.c`. It depends on platform resources for `rxtx_regs`, `sir0_regs`, and `sir1_regs`, MDIO register access through common macros, and the common AN/link state machine in `xgbe-mdio.c`.

## Risks
SerDes tuning properties must have exactly `XGBE_SPEEDS` entries and valid board-specific values; bad firmware properties can prevent link. Ratechange waits only a bounded count and logs debug on not-ready status before continuing to RX reset. v1 supports only full duplex and a limited speed set; ethtool fixed-speed validation must reject unsupported values. PCS reset timeout returns `-ETIMEDOUT`.

## Test Signals
Test both `XGBE_SPEEDSET_1000_10000` and `XGBE_SPEEDSET_2500_10000`, default and firmware-provided SerDes tuning, CL73 KR/KX negotiation, fixed-speed configuration, PCS reset timeout handling, and link flap recovery. `ethtool` supported/advertised modes should match the speed-set property.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-phy-v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-phy-v2.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-phy-v2.c

## Purpose
`xgbe-phy-v2.c` is the PHY backend for newer PCI XGBE devices. It supports many port/connection types: backplane, backplane without AN, 2.5G backplane, Base-T via external MDIO PHYs, Base-X, 10GBase-R, SFP/SFP+, optional redrivers, mailbox-driven rate changes, receiver reset cycles, CDR workarounds, and RX adaptation.

## Important APIs, Types, And Functions
- Local enums define port modes, connection types, SFP communication/cable/base/speed types, MDIO reset types, and redriver interface/model/modes.
- `struct xgbe_phy_data` stores port properties, SFP state, external PHY state, redriver state, current/start mode, and CDR/RRC counters.
- I2C helpers (`xgbe_phy_i2c_read/write`, SFP mux helpers, redriver I2C write) wrap `xgbe-i2c.c`.
- `xgbe_phy_get_comm_ownership` and `xgbe_phy_put_comm_ownership` serialize software and hardware ownership of muxed I2C/MDIO/GPIO resources.
- MDIO bus callbacks expose internal/external Clause 22 and Clause 45 access through a registered `mii_bus`.
- SFP helpers read GPIOs and EEPROM, verify checksums, parse module type, expose module info/EEPROM, and detect copper SFP PHY availability.
- External PHY helpers create/destroy `phy_device`, apply Bel-Fuse and Finisar quirks, and start PHY AN.
- AN outcome helpers resolve CL37, CL37 SGMII, CL73, and CL73-with-redriver results.
- Mode helpers map speeds/ports to `enum xgbe_mode` and issue mailbox rate-change commands.
- RX adaptation helpers stop/start data path around adaptation, retry mailbox/RX EQ flows, and track `rx_adapt_done`.
- `xgbe_phy_init/start/stop/reset/exit` and `xgbe_init_function_ptrs_phy_v2` provide the implementation interface.

## Control Flow
Init validates that the port is enabled, initializes I2C, reads hardware property registers `pp0`/`pp3`/`pp4`, validates port/connection/speed/redriver combinations, sets supported link modes and start mode based on port mode, configures SFP GPIO/mux metadata when needed, configures external MDIO mode, registers an internal `mii_bus`, and caches PHY data. Start begins I2C, configures redriver MDIO mode, sets the highest supported start mode, handles CDR tracking, detects SFP modules, and attaches an external PHY when present. Link status repeatedly detects SFP changes, polls external PHYs, reads PCS status, runs RX adaptation when enabled, restarts AN on relevant down states, and periodically triggers receiver reset cycles. Stop frees external PHYs, resets SFP state, restores CDR tracking, powers off PHY firmware, and stops I2C.

## State And Persistence
The file owns substantial runtime state in `struct xgbe_phy_data`: `port_mode`, `conn_type`, `port_speeds`, `mdio_addr`, SFP GPIO and EEPROM fields, `sfp_changed`, `sfp_mod_absent`, `sfp_phy_avail`, `phydev`, `mii`, reset/redriver metadata, `cur_mode`, `start_mode`, `rrc_count`, `phy_cdr_notrack`, and `phy_cdr_delay`. It also updates shared `pdata` fields such as `kr_redrv`, `an_again`, `en_rx_adap`, `rx_adapt_retries`, `rx_adapt_done`, `data_path_stopped`, and `mode_set`. State is runtime and re-derived on probe or SFP changes.

## Dependencies And Integration Points
This backend depends on PCI-populated property registers, the private I2C controller, hardware MDIO/GPIO callbacks, Linux PHYLIB, Linux ethtool module EEPROM APIs, mailbox scratch/int registers, common AN/link management in `xgbe-mdio.c`, and version-data workarounds from `xgbe-pci.c`. `xgbe-ethtool.c` reaches module info and EEPROM through this implementation.

## Risks
This is one of the highest-risk files in the subset. Hardware resource ownership spans a software mutex and hardware mutex registers; failure paths must always release ownership. SFP probing treats EEPROM/I2C errors as module absence, which is practical but can mask bus faults. Redriver settings are board-specific and validation must match supported models/lanes. Static version-data flags changed by PCI probing affect behavior such as RRC and CDR workarounds. RX adaptation deliberately stops TX/RX data path to prevent packet corruption; regressions here can cause link stalls or CRC errors. PHY quirks hard-code vendor/part behavior.

## Test Signals
Test every port mode available in hardware, including SFP insertion/removal, copper SFP external PHY attach/detach, `ethtool -m`, Base-T speeds from 10M to 10G, redriver MDIO and I2C paths, CL37/CL73 AN, no-AN backplane, RX adaptation success/failure, receiver reset cycles, suspend/resume via PCI, and mailbox timeout recovery. Important logs include SFP EEPROM/GPIO I2C errors, hardware mutex timeout, redriver setting errors, firmware mailbox timeout, and link mode transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-phy-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-platform.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-platform.c

## Purpose
`xgbe-platform.c` is the platform/ACPI/Device Tree binding for first-generation AMD XGBE devices. It obtains MMIO resources, clocks/properties, PHY resources, MAC address, interrupts, DMA coherency settings, and v1 version data before delegating to common netdev setup.

## Important APIs, Types, And Functions
- `xgbe_acpi_support` reads ACPI DMA and PTP clock frequencies.
- `xgbe_of_support` obtains `dma_clk` and `ptp_clk` through the clock framework.
- `xgbe_of_get_phy_pdev` and `xgbe_get_phy_pdev` support old split XGBE/PHY DT layouts and newer grouped layouts.
- `xgbe_resource_count` counts platform resources of a given type.
- `xgbe_platform_probe` performs platform discovery and netdev enablement.
- `xgbe_platform_remove` tears down the netdev and releases the PHY platform device.
- PM callbacks put PCS into low-power mode and call `xgbe_powerdown`/`xgbe_powerup`.
- `xgbe_v1` selects PHY v1 callbacks, XPCS access v1, FIFO limits, and TX timestamp workaround.
- `xgbe_platform_init`/`xgbe_platform_exit` register and unregister the platform driver.

## Control Flow
Probe allocates `pdata`, determines ACPI versus OF, gets version data, finds the PHY platform device, decides resource indexes for old/new layouts, maps XGMAC, XPCS, RxTx, SIR0, and SIR1 MMIO resources, reads MAC address and verifies `phy-mode` is `xgmii`, detects per-channel IRQ property, obtains clock rates, sets DMA coherency register values, applies FIFO limits, calculates counts, fetches device/channel/AN IRQs, and calls `xgbe_config_netdev`. Suspend/resume power down/up the netdev if running and toggle PCS low-power mode.

## State And Persistence
Probe populates `pdata->platdev`, `adev`, `phy_platdev`, `phy_dev`, MMIO pointers, `phy_mode`, IRQ numbers, clock handles/rates, DMA coherency fields, FIFO limits, per-channel IRQ mode, and `vdata`. This state lasts for the platform device lifetime. PM stores/restores low-power control through `pdata->lpm_ctrl`.

## Dependencies And Integration Points
This file depends on ACPI, OF, platform resource APIs, clock framework, device properties, DMA attribute APIs, and common netdev setup in `xgbe-main.c`. It selects `xgbe-phy-v1.c` as the implementation backend.

## Risks
Resource index calculations differ for old split and new grouped DT layouts; incorrect firmware descriptions can map the wrong PHY resources. Per-channel IRQ setup sets `channel_irq_count` to the array maximum after the loop, even if fewer IRQs were discovered before `dma_irqend`; downstream limits depend on accurate counts. The platform PM path does not perform the PCI file's explicit IRQ synchronization before low-power writes. `phy-mode` is strict and rejects anything other than `xgmii`.

## Test Signals
Test ACPI and OF boot paths, old and new DT PHY resource layouts, missing clock/property failures, MAC address validation, per-channel IRQ resources, probe/remove unwind, and suspend/resume with link up. Verify supported modes and SerDes resources through v1 PHY behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-pps.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-pps.c

## Purpose
`xgbe-pps.c` configures MAC Pulse Per Second/per-out outputs for the PTP clock. It programs start time, interval, pulse width, command, and target mode registers for a selected PPS output.

## Important APIs, Types, And Functions
- `get_pps_mask`, `get_pps_cmd`, and `get_target_mode_sel` compute per-output bitfields in `MAC_PPSCR`.
- `xgbe_pps_config` is the exported configuration routine used by `xgbe-ptp.c` for `PTP_CLK_REQ_PEROUT`.

## Control Flow
`xgbe_enable` in `xgbe-ptp.c` copies a PTP perout request into `pdata->pps[index]`, takes `tstamp_lock`, and calls `xgbe_pps_config`. The PPS routine checks whether the target time register is busy. For disable, it writes a stop command. For enable, it writes target start seconds/nanoseconds, converts requested period to hardware units using `XGBE_V2_TSTAMP_SSINC`, validates a minimum period, writes interval and 50 percent duty-cycle width, then writes a start pulse-train command.

## State And Persistence
Configuration values are cached in `pdata->pps[index]` by the caller and programmed into MAC PPS registers. State is runtime and tied to the PHC/netdev lifetime.

## Dependencies And Integration Points
This file depends on MAC PPS register definitions from `xgbe-common.h`, timestamp increment constants from `xgbe.h`, and PTP request plumbing in `xgbe-ptp.c`. Locking is provided by the caller.

## Risks
The conversion always uses `XGBE_V2_TSTAMP_SSINC`; this assumes the PPS hardware mode matches that increment. The caller must validate `index` against `ptp_clock_info.n_per_out`; this function itself does not bounds-check. Busy target registers return `-EBUSY`, and too-small periods return `-EINVAL`. Duty cycle is fixed at 50 percent.

## Test Signals
Use `testptp` or equivalent PHC perout tooling to enable/disable outputs at supported indices and periods. Check `-EBUSY` handling, minimum period validation, output frequency/duty cycle on hardware, and behavior after PHC or netdev restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-pps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-ptp.c

## Purpose
`xgbe-ptp.c` registers and implements the Linux PTP hardware clock interface for AMD XGBE. It provides PHC frequency adjustment, time adjustment, time get/set, and per-output PPS enablement.

## Important APIs, Types, And Functions
- `xgbe_adjfine` adjusts the timestamp addend using `adjust_by_scaled_ppm`.
- `xgbe_adjtime` applies positive or negative time deltas through timestamp update registers.
- `xgbe_gettimex` reads the hardware time with system timestamp bracketing.
- `xgbe_settime` initializes the hardware time.
- `xgbe_enable` handles `PTP_CLK_REQ_PEROUT` by calling `xgbe_pps_config`.
- `xgbe_ptp_register` fills `struct ptp_clock_info`, registers the PHC, disables timestamping by default, and initializes hwtstamp config to off.
- `xgbe_ptp_unregister` unregisters the PHC.

## Control Flow
`xgbe_config_netdev` calls `xgbe_ptp_register` when PTP support is reachable. PTP core operations call the registered callbacks, which recover `pdata` from the embedded `ptp_clock_info`, take `tstamp_lock` for register operations, and delegate low-level timestamp programming to `xgbe-hwtstamp.c`. Perout requests are copied into `pdata->pps[index]` and applied through `xgbe_pps_config`.

## State And Persistence
PTP state lives in `pdata->ptp_clock_info`, `pdata->ptp_clock`, `pdata->tstamp_addend`, `pdata->tstamp_config`, and `pdata->pps[]`. Hardware time and addend live in MAC registers. `tstamp_lock` serializes PHC operations with timestamp code.

## Dependencies And Integration Points
This file depends on Linux PTP clock APIs, timestamp helpers from `xgbe-hwtstamp.c`, PPS programming from `xgbe-pps.c`, and hardware feature counts for `n_per_out` and `n_ext_ts`. ethtool timestamp reporting references the registered PHC index.

## Risks
Perout indexing is taken from the PTP request; correctness depends on PTP core bounds relative to `n_per_out`. Negative `adjtime` handling writes sign and adjusted nanoseconds in MAC-specific format and must match `TSCTRLSSR`. `max_adj` is set to `ptpclk_rate`, so incorrect clock discovery affects user-visible adjustment limits. Unregister does not clear `pdata->ptp_clock` after unregistering.

## Test Signals
Use `ptp4l`, `phc2sys`, `phc_ctl`, and `testptp` to validate get/set, fine adjustment, negative and positive adjustments, PHC index reporting via `ethtool -T`, and PPS perout behavior. Re-test after interface restart and driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-selftest.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-selftest.c

## Purpose
`xgbe-selftest.c` implements ethtool offline self-tests for MAC loopback, PHY loopback, split-header operation, and jumbo frame loopback. It sends synthetic packets through the netdev and validates they return with expected headers and payload markers.

## Important APIs, Types, And Functions
- `struct xgbe_test` describes each test name, loopback mode requirement, and callback.
- `xgbe_test_loopback_validate` is a packet handler that validates Ethernet/IP/TCP/UDP fields and `NET_TEST_PKT_MAGIC`.
- `__xgbe_test_loopback` registers a temporary packet handler, creates a test SKB with `net_test_get_skb`, transmits via `dev_direct_xmit`, and waits for completion.
- `xgbe_test_mac_loopback`, `xgbe_test_phy_loopback`, `xgbe_test_sph`, and `xgbe_test_jumbo` implement individual tests.
- `xgbe_selftest_run` is the ethtool self-test entry point.
- `xgbe_selftest_get_strings` and `xgbe_selftest_get_count` supply ethtool test metadata.

## Control Flow
ethtool calls `xgbe_selftest_run` through `xgbe-ethtool.c`. The function requires offline mode and link carrier. It waits briefly for queues to drain, then for each test enables PHY loopback or MAC loopback as required, runs the test callback, stores the result in the ethtool buffer, marks overall failure for real failures, and disables loopback. Loopback validation completes a per-test completion when the expected packet is observed.

## State And Persistence
The file uses a static `xgbe_test_id` incremented per generated packet during a test run. Each loopback has temporary `net_test_priv` state, a completion, and a temporary packet handler. It observes driver state such as `pdata->sph`, `rx_split_header_packets`, `rx_buf_size`, netdev address, and optional `phydev`.

## Dependencies And Integration Points
This file depends on Linux networking selftest helpers, packet handlers, PHYLIB loopback APIs, MAC loopback helpers from elsewhere in the driver, and ethtool test plumbing in `xgbe-ethtool.c`.

## Risks
Tests are intrusive and only support offline mode. They require carrier and may fail if external PHY loopback is unsupported. Temporary packet handlers must be removed on all paths. `dev_direct_xmit` return semantics and packet ownership are important; the code cleans local test state but relies on networking helpers for SKB lifecycle after transmit. Split-header and jumbo tests depend on current driver feature/configuration state.

## Test Signals
Run `ethtool --test <dev> offline` with link up. Confirm expected `-EOPNOTSUPP` behavior for unsupported PHY loopback, split-header test behavior with SPH enabled/disabled, jumbo behavior with large RX buffers, and no leaked packet handlers or loopback state after failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-smn.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-smn.h

## Purpose
`xgbe-smn.h` abstracts access to AMD System Management Network reads/writes used by the PCI driver for XPCS v3 indirect window setup. It provides real AMD northbridge access when `CONFIG_AMD_NB` is enabled and safe stubs otherwise.

## Important APIs, Types, And Functions
- When `CONFIG_AMD_NB` is enabled, the header includes `<asm/amd/nb.h>` and exposes the platform `amd_smn_read`/`amd_smn_write` APIs.
- Otherwise, inline `amd_smn_write` and `amd_smn_read` return `-ENODEV`.

## Control Flow
`xgbe-pci.c` includes this header. During probe for v3 XPCS access, it computes an SMN address and calls `amd_smn_read` to read the XPCS window definition register. If the stub is active, probe fails for that path with `-ENODEV`.

## State And Persistence
The header owns no state. It only controls compile-time availability of SMN access.

## Dependencies And Integration Points
This file depends on the kernel AMD northbridge support configuration. Its sole integration in this subset is the PCI probe path for v3 hardware.

## Risks
Building without `CONFIG_AMD_NB` can make v3 PCI devices fail probe when SMN access is required. The stub behavior is explicit and safe, but it shifts the failure to runtime. Callers must check return codes, which `xgbe-pci.c` does.

## Test Signals
Build with and without `CONFIG_AMD_NB`. Probe v3 hardware and confirm successful SMN reads when enabled and clear probe failure logs when unavailable. Static analysis should confirm all SMN calls check return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-smn.h -->
