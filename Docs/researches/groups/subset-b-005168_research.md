# subset-b-005168 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_ines.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_ines.c

Purpose: implements the ZHAW InES PTP timestamping IP controller as a Device Tree platform driver and MII timestamping controller. It does not register a PHC of its own; instead it gives Ethernet PHY/MAC users a `struct mii_timestamper` per hardware port, matches hardware FIFO timestamps to PTPv2 packets, and completes RX/TX hardware timestamps for the network stack.

Important APIs/types/functions: `struct ines_clock` owns the MMIO base and three `struct ines_port` instances. Each port keeps timestamp FIFOs, `rxts_enabled`/`txts_enabled`, a delayed TX work item, a pending TX skb, and an event object pool. `ines_ptp_ctrl_probe()` maps registers, initializes ports, registers `ines_ctrl` through `register_mii_tstamp_controller()`, and stores the clock in the global `ines_clocks` list. `ines_ptp_probe_channel()` returns the port `mii_timestamper` with `hwtstamp_set/get`, `rxtstamp`, `txtstamp`, `link_state`, and `ts_info` callbacks. `ines_rxfifo_read()`, `ines_find_rxts()`, `ines_find_txts()`, `ines_match()`, and `tag_to_msgtype()` are the packet-to-FIFO matching core.

Control flow: probe initializes the global and per-port register mappings, creates the free timestamp pool, writes default PTPv2 1G port configuration, registers the MII timestamping controller, and then publishes the clock in `ines_clocks`. Channel probing locates the platform controller by OF node and port index. RX timestamping reads the RX FIFO under the port spinlock, expires stale entries, matches PTPv2 message type/clock identity/port/sequence ID, attaches `skb_hwtstamps()`, and reinjects the skb with `netif_rx()`. TX timestamping drops one-step Sync/Pdelay response skbs, otherwise stores one pending skb and schedules delayed work; the worker drains the TX FIFO, matches the skb, and calls `skb_complete_tx_timestamp()`.

State and persistence: all state is runtime-only. The global `ines_clocks` list is protected by `ines_clocks_lock`; per-port event lists and pending TX skb are protected by `port->lock`. RX events expire after one second and are recycled into the fixed pool. Hardware timestamping enablement and link speed are stored in hardware registers and mirrored in booleans, but no state persists across driver removal or reboot.

Dependencies and integration: integrates with OF platform devices compatible with `ines,ptp-ctrl`, MMIO helpers, PHY link-state callbacks, `linux/mii_timestamper.h`, `ptp_classify_raw()`, PTP header parsing, skb timestamp APIs, and ethtool hardware timestamp reporting. VLAN inclusion is handled through the classifier and parser rather than ad hoc offsets.

Risks and test signals: only PTPv2 is supported; PTPv1 filters are rejected or ignored. The fixed event pool can overflow if userspace/network consumers do not match events quickly enough. TX only tracks one pending skb per port, so a second TX request discards the prior skb. `ines_txtstamp_work()` assumes the saved skb is valid when work runs. FIFO read-position checks and debug logs are key diagnostics. Test with `SIOCSHWTSTAMP` filter negotiation, one-step P2P mode, RX/TX timestamp matching across all three ports, link speed changes, FIFO-empty and pool-empty paths, and remove-time delayed work cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_ines.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_arm.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_arm.c

Purpose: supplies the ARM architecture backend for the KVM virtual PTP clock. The common `ptp_kvm_common.c` module owns PHC registration; this file only verifies that the KVM hypervisor service is available and routes simple clock reads through the architecture crosstimestamp implementation.

Important APIs/types/functions: `kvm_arch_ptp_init()` checks `kvm_arm_hyp_service_available(ARM_SMCCC_KVM_FUNC_PTP)` and returns `-EOPNOTSUPP` when unavailable. `kvm_arch_ptp_exit()` is a no-op. `kvm_arch_ptp_get_clock()` calls `kvm_arch_ptp_get_crosststamp(NULL, ts, NULL)`, relying on the ARM implementation declared in `linux/ptp_kvm.h` and architecture support.

Control flow: module initialization in the common file invokes `kvm_arch_ptp_init()`. If the SMCCC KVM PTP function is present, common registration continues; otherwise the module exits quietly for unsupported guests. Runtime `gettime64` requests call `kvm_arch_ptp_get_clock()`, which delegates to crosstimestamp acquisition.

State and persistence: no local state, no allocations, no hardware programming, and no persistent data. Availability is probed each load.

Dependencies and integration: depends on ARM SMCCC, ARM arch timer support, hypervisor detection, and the common KVM PTP module. It is intentionally tiny because ARM-specific crosstimestamp mechanics live outside this file.

Risks and test signals: the main risk is availability mismatch between advertised SMCCC support and working crosstimestamp calls. Build tests need ARM configurations with `CONFIG_PTP_1588_CLOCK_KVM`; runtime tests need KVM guests with and without `ARM_SMCCC_KVM_FUNC_PTP`, plus `phc2sys` or `testptp` reads confirming `-EOPNOTSUPP` on unsupported hosts and stable timestamps on supported hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_common.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_common.c

Purpose: registers a read-only PTP hardware clock backed by KVM host wall-clock pairing. Architecture-specific files provide init, plain clock reads, and crosstimestamp reads; this common file exposes them through the kernel PTP class.

Important APIs/types/functions: `struct kvm_ptp_clock` stores the registered `ptp_clock` and its copied `ptp_clock_info`. `ptp_kvm_caps` names the PHC `"KVM virtual PTP"` and implements `gettime64` plus `getcrosststamp`; adjustment, setting, and event enable operations return `-EOPNOTSUPP`. `ptp_kvm_get_time_fn()` wraps `kvm_arch_ptp_get_crosststamp()` for `get_device_system_crosststamp()`. `ptp_kvm_init()` calls `kvm_arch_ptp_init()` and `ptp_clock_register()`, while `ptp_kvm_exit()` unregisters and calls architecture cleanup.

Control flow: init probes architecture support first. If unsupported, the module returns `-EOPNOTSUPP` without registering a PHC. `gettime64` serializes with `kvm_ptp_lock`, calls `kvm_arch_ptp_get_clock()`, and copies the returned `timespec64`. `getcrosststamp` uses a callback that disables preemption around architecture pairing so the returned cycle value and clocksource ID remain CPU-consistent.

State and persistence: the only persistent module state is the single global `kvm_ptp_clock` plus `kvm_ptp_lock`. There is no adjustable offset, no event queue, and no persistence beyond module lifetime.

Dependencies and integration: integrates with `linux/ptp_clock_kernel.h`, KVM paravirtual interfaces, architecture `ptp_kvm.h` hooks, `get_device_system_crosststamp()`, and system counter IDs. Userspace sees a normal `/dev/ptpN` device but cannot discipline or set it.

Risks and test signals: lock ordering around preemption is important; early error paths must re-enable preemption and release the spinlock. Since adjustment APIs are unsupported, time-sync daemons must treat this as a reference source, not a steerable clock. Test signals include module load on KVM and non-KVM guests, `PTP_SYS_OFFSET_PRECISE`, repeated `gettime64`, architecture hypercall failures, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_x86.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_x86.c

Purpose: supplies the x86 KVM backend for the virtual PTP clock. It uses the `KVM_HC_CLOCK_PAIRING` hypercall to pair host wall time with a guest TSC value, and converts that TSC through pvclock state for precise crosstimestamps.

Important APIs/types/functions: globals `clock_pair_gpa`, `clock_pair_glbl`, and `clock_pair` hold the shared hypercall result page. `kvm_arch_ptp_init()` validates KVM paravirt support, allocates/decrypts a page for encrypted guests, verifies pvclock CPU0 state, and checks the clock-pairing hypercall. `kvm_arch_ptp_exit()` re-encrypts and frees the page for confidential-computing guests. `kvm_arch_ptp_get_clock()` performs a wall-clock pairing and returns seconds/nanoseconds. `kvm_arch_ptp_get_crosststamp()` reads `this_cpu_pvti()`, retries on pvclock version changes, invokes the hypercall, converts `clock_pair->tsc` with `__pvclock_read_cycles()`, and reports `CSID_X86_KVM_CLK`.

Control flow: common init calls x86 init; encrypted guests use a dynamically allocated decrypted page while normal guests use a static global structure. Runtime reads issue `KVM_HC_CLOCK_PAIRING` with `KVM_CLOCK_PAIRING_WALLCLOCK`. Crosstimestamp reads loop until pvclock metadata is stable, so the host-provided TSC and the guest system counter conversion agree.

State and persistence: state is one shared clock-pairing memory area and its guest physical address. It is module-lifetime only. Confidential guest memory state is explicitly restored in exit and in init failure paths.

Dependencies and integration: depends on x86 KVM paravirt, pvclock, `cc_platform_has(CC_ATTR_GUEST_MEM_ENCRYPT)`, `set_memory_decrypted/encrypted()`, KVM UAPI hypercall constants, and the common PTP KVM module.

Risks and test signals: encrypted guest setup is sensitive to cleanup ordering; `clock_pair` must not remain decrypted or leaked on init errors. Crosstimestamp correctness depends on stable pvclock metadata and CPU-local preemption handling in the common layer. Test on non-KVM, KVM without clock pairing, regular KVM, and memory-encrypted guests; verify `PTP_SYS_OFFSET_PRECISE`, rate-limited hypercall error logs, and module unload memory restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_kvm_x86.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_mock.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_mock.c

Purpose: provides an exported helper for virtual network devices to create a mock PTP hardware clock backed by `CLOCK_MONOTONIC_RAW`. It behaves like an adjustable PHC without hardware, useful for tests and virtual drivers that need a PHC index.

Important APIs/types/functions: `struct mock_phc` stores `ptp_clock_info`, registered clock, `timecounter`, `cyclecounter`, and a spinlock. `mock_phc_create()` allocates the object, initializes a cyclecounter whose `read` returns `ktime_get_raw_ns()`, registers the PTP clock, and schedules periodic worker refresh. `mock_phc_destroy()` unregisters and frees it. `mock_phc_index()` returns `ptp_clock_index()`. Clock operations include `mock_phc_adjfine()`, `mock_phc_adjtime()`, `mock_phc_settime64()`, `mock_phc_gettime64()`, and `mock_phc_refresh()`.

Control flow: callers create a mock PHC with a parent device. Reads call `timecounter_read()` under lock. Frequency adjustments first read the counter to preserve continuity, then update `cc.mult` using the scaled-ppm conversion. Time adjustments use `timecounter_adjtime()`, and settime reinitializes the timecounter origin. The aux worker periodically reads the clock so the timecounter is refreshed before overflow-sensitive deltas become too large.

State and persistence: time and frequency offset exist only in the in-memory timecounter/cyclecounter. No settings persist after destroy or reboot. The spinlock serializes all timecounter and multiplier changes.

Dependencies and integration: exports GPL symbols through `linux/ptp_mock.h`, uses the PTP class, `linux/timecounter.h`, and raw monotonic kernel time. It is intended as a library-style module rather than an enumerated platform or PCI driver.

Risks and test signals: the refresh interval is chosen to avoid 64-bit multiplication overflow in `timecounter_read_delta()` under the maximum allowed frequency adjustment; changing max adjustment, shift, or refresh interval must be reviewed together. Test by creating/destroying from a virtual net driver, reading `/dev/ptpN`, applying positive and negative `adjfine`, settime/adjtime continuity, and ensuring worker scheduling stops at unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_mock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_netc.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_netc.c

Purpose: implements the NXP NETC V4 Timer as a PCI PTP hardware clock. It exposes adjustable time, PPS, three periodic outputs, two external timestamp channels, periodic-output loopback, and MSI-X interrupt delivery.

Important APIs/types/functions: `struct netc_timer` owns the PCI device, MMIO base, PTP clock, clock source parameters, spinlock, interrupt state, alarm allocation bitmap, selected PPS channel, and three `struct netc_pp` periodic-pulse channel records. `netc_timer_ptp_caps` wires `adjfine`, `adjtime`, `gettimex64`, `settime64`, `enable`, and `perout_loopback`. Low-level helpers read/write split 64-bit counter, offset, current-time, alarm, FIPER, and external timestamp registers in the hardware-required order. Probe helpers are `netc_timer_pci_probe()`, `netc_timer_parse_dt()`, `netc_timer_init_msix_irq()`, `netc_timer_init()`, and `netc_timer_probe()`.

Control flow: PCI probe resets/enables the device, maps BAR0, reads the global IP revision, derives available alarm count, selects a reference clock from optional DT clocks or the default 333 MHz system clock, initializes period fixed-point values, requests one MSI-X vector, programs the timer, and registers the PHC. `gettimex64` reads current hardware time bracketed by system timestamp pre/post calls. `settime64` disables FIPER outputs, clears offset, writes the counter, and restores outputs. `adjtime` adjusts `TMR_OFF` rather than `TMR_CNT` to avoid counter write latency, again temporarily disabling FIPER. `adjfine` computes a new fixed-point timer period and updates `TCLK_PERIOD`/`TMR_ADD`, disabling/re-enabling FIPER if the integral period changes.

State and persistence: PPS and perout state are kept in `priv->pp[]`, `pps_channel`, `fs_alarm_bitmap`, and `tmr_emask`; hardware FIPER/alarm registers are reprogrammed whenever time or period changes. State is runtime-only and is cleared on remove by masking events and disabling the timer.

Dependencies and integration: uses PCI, MSI-X, OF-provided clocks via `devm_clk_get_optional_enabled()`, NXP NETC global register access, PTP core requests, and kernel PPS/extts event delivery. The driver distinguishes revision 4.1, which has only one function-select alarm.

Risks and test signals: channel allocation is shared between PPS and PEROUT, so conflicts return `-EBUSY`. Period ranges depend on current integral timer period and generated clock period. External timestamp enables reject both-edge mode. Interrupt handling clears masked events and may consume FIFO timestamps until valid bits clear. Test with all combinations of PPS/PEROUT channel allocation, alarm exhaustion on rev 4.1, boundary perout periods, falling/rising EXTS, adjtime while outputs are active, MSI-X allocation failure, and remove-time interrupt masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_netc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_ocp.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_ocp.c

Purpose: implements the Open Compute TimeCard family driver for Meta/Celestica, Orolia ART, and ADVA PCIe time cards. It registers a PHC, creates a `timecard` class device, exposes SMA routing and board controls through sysfs, registers serial/I2C/SPI child devices, supports firmware updates through devlink, publishes debugfs summaries, and integrates SMA connectors with the DPLL subsystem.

Important APIs/types/functions: `struct ptp_ocp` is the central state object: PCI device, embedded class `device`, spinlock, mapped register blocks, timestamp/signal resources, serial port descriptors, child platform devices, watchdog/sync work, firmware/eeprom metadata, PTP info, SMA connector state, DPLL handles, and per-signal configuration. Resource tables `ocp_fb_resource`, `ocp_art_resource`, `ocp_adva_resource`, and `ocp_adva_x1_resource` describe MMIO windows, IRQ vectors, child bus devices, and variant-specific board initialization. `ptp_ocp_clock_info` implements PHC operations. Board init functions set firmware capabilities, EEPROM maps, SMA operations, pins, sysfs groups, TOD/NMEA/signal defaults, and clock servo configuration.

Control flow: module init creates debugfs root, registers the `timecard` class, subscribes to I2C bus notifications, and registers the PCI driver. Probe allocates a devlink object with `struct ptp_ocp` private data, enables PCI, creates the class device with an IDR id, allocates MSI/MSI-X vectors, registers resources from the selected table, registers the PHC, creates symlinks to PTP/PPS/I2C children, logs board info, registers devlink and DPLL devices/pins, then starts delayed sync tracking. Remove cancels sync work, unregisters DPLL pins/device, unregisters devlink, tears down sysfs/debugfs/timers/ext IRQs/serial/child devices/PHC, disables PCI, and frees devlink.

State and persistence: PHC time is hardware state. Driver runtime state includes SMA direction/function, signal generator period/duty/phase/start/running values, PPS request map, UTC-TAI offset, timestamp-window adjustment, GNSS-lost timestamp, firmware capability flags, and EEPROM-read identity data. Persistent operations include SPI flash updates through devlink and ART EEPROM binary sysfs writes for disciplining config and temperature table. Most sysfs routing/configuration is runtime hardware programming, not persisted by this driver.

Dependencies and integration: integrates with PCI, MSI/MSI-X, PTP/PPS, serial8250, platform I2C and SPI controllers, clkdev, nvmem EEPROMs, MTD, devlink flash/info APIs, debugfs, sysfs attribute groups, DPLL netlink devices/pins, and I2C bus notifiers. It also creates user-facing class devices and symlinks to child `/dev/ptpN`, PPS, tty, and I2C objects.

Important behavior: `ptp_ocp_gettimex()` latches hardware time with PCI timing compensation. Small `adjtime` writes offset registers; large adjustments read current time and set a new time. `adjfine` and `adjphase` are deliberately unsupported except zero frequency adjustment. `ptp_ocp_enable()` routes EXTS/PPS/PEROUT requests to timestamp or signal-generator resources; PEROUT index 0 is accepted only as manual 1PPS, while indexes 1-4 program signal generators. SMA sysfs and `verify()` translate PTP pin operations to input/output routing strings. The watchdog clears drift on GNSS supervisor error and distributes UTC offset from TOD when valid. DPLL state follows PHC sync status and SMA direction/frequency operations call the same routing helpers.

Risks and test signals: this is a large multi-subsystem driver, so cleanup ordering is the highest risk. Some failure paths after devlink registration and partial DPLL setup must unwind class devices, child devices, IRQs, and PHC consistently. Firmware capability gating controls which sysfs groups exist; tests need old firmware with reduced IRQs and missing SMA maps. `ptp_ocp_init_clock()` writes `servo_drift_p` into both drift P and drift I registers, which deserves review against hardware docs. `ptp_ocp_dpll_frequency_set()` passes the selector table index rather than selector value to `ptp_ocp_sma_store_val()`, a potential routing bug. Test signals include probe/remove for every PCI ID, IRQ timestamp/PPS delivery, SMA sysfs and DPLL direction/frequency changes, devlink image header/CRC/vendor checks, EEPROM reads/writes, debugfs summary, GNSS-loss watchdog behavior, and suspend-like hot remove during active signal outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_ocp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_pch.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_pch.c

Purpose: implements a PCI PTP clock for the Intel EG20T/LAPIS PCH IEEE 1588 timer. It also exports helper functions used by companion Ethernet/CAN logic to access channel control/event, station UUID, and RX/TX snapshot registers.

Important APIs/types/functions: `struct pch_ts_regs` maps the hardware register block. `struct pch_dev` stores the mapped regs, registered PHC, external timestamp enable flags, IRQ, PCI device, and register spinlock. Exported APIs include `pch_ch_control_write()`, `pch_ch_event_read/write()`, `pch_src_uuid_lo_read()`, `pch_src_uuid_hi_read()`, `pch_rx_snap_read()`, `pch_tx_snap_read()`, and `pch_set_station_address()`. `ptp_pch_caps` wires `adjfine`, `adjtime`, `gettime64`, `settime64`, and EXTS enable.

Control flow: PCI probe enables the device with managed PCI helpers, maps BAR1, registers the PHC, requests a shared IRQ, stores drvdata, resets the hardware, writes the default addend, clears the target-time pending bit, enables Ethernet timestamp selection, and optionally programs the `station=` module parameter. The ISR reads event bits, emits `PTP_CLOCK_EXTTS` for enabled SNS/SNM channels, acknowledges handled bits, and ignores the always-set TTIPEND except for acking.

State and persistence: external timestamp enables are runtime booleans only. System time and addend live in hardware registers. The station address module parameter is read-only after load and programs hardware at probe; it is not persisted by the driver.

Dependencies and integration: uses PCI, MMIO, PTP core, shared IRQs, MAC string parsing, and exported symbols for other PCH-related drivers. Time registers store ticks shifted by `TICKS_NS_SHIFT`, so all public helpers convert to nanoseconds.

Risks and test signals: `ptp_pch_adjfine()` writes the addend without taking `register_lock`, unlike get/set/adjtime. The ISR uses the same ASMS timestamp register for both external timestamp channels, which should match hardware expectations. Station parsing stores a parsed MAC into a `u64` and writes it little-endian through `iowrite64_lo_hi`; byte order should be tested with real hardware. Test module load/unload, IRQ sharing, both EXTS channels, settime/adjtime frequency adjustment, exported snapshot readers, invalid station parameter handling, and probe failure after PHC registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_pch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_private.h -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_private.h

Purpose: defines private data structures and internal interfaces shared by the PTP core implementation files. It is not a hardware driver; it is the internal contract for the PTP class device, character-device operations, sysfs, pin handling, event queues, auxiliary work, virtual clocks, and debugfs state.

Important APIs/types/functions: `struct timestamp_event_queue` is the external timestamp FIFO with lock, head/tail indices, optional mask, list linkage, and debugfs metadata. `struct ptp_clock` embeds the POSIX clock and device, stores the driver `ptp_clock_info`, PPS source, event queue list, pin config attributes, worker state, virtual-clock limits and indexes, flags for virtual/has-cycles behavior, and debugfs root. `struct ptp_vclock` defines child virtual PHCs backed by a parent clock, cyclecounter/timecounter pair, mutex, and RCU hash linkage. Inline helpers are `queue_cnt()`, `ptp_vclock_in_use()`, and `ptp_clock_freerun()`.

Control flow: the header declares operations implemented in `ptp_chardev.c`, `ptp_sysfs.c`, and `ptp_vclock.c`. `queue_cnt()` uses `READ_ONCE()` to allow lockless non-empty checks paired with writer `WRITE_ONCE()` updates. `ptp_vclock_in_use()` avoids taking `n_vclocks_mux` on virtual clocks to prevent lockdep false positives from nested physical/virtual calls. `ptp_clock_freerun()` forces non-cycle-capable physical clocks into free-running behavior when virtual clocks depend on them.

State and persistence: all structures represent live kernel state. There is no on-disk persistence. The most durable state is user-visible device identity, event queues, pin attributes, virtual-clock child indexes, and debugfs entries for the lifetime of a registered PTP clock.

Dependencies and integration: includes cdev, device, kthread, mutex, posix-clock, PTP kernel/public APIs, list, bitmap, and debugfs headers. It is consumed by PTP core source files rather than external drivers.

Risks and test signals: this header encodes locking assumptions across the PTP core. Misusing `queue_cnt()` without understanding its non-empty-only guarantee can race with dequeues. Virtual-clock locking must avoid stacking virtual clocks on virtual clocks. Test through core PTP registration/unregistration, open/read/poll/ioctl, EXTS FIFO wraparound, pin sysfs creation/removal, vclock creation/deletion, and lockdep under concurrent physical and virtual clock operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_qoriq.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_qoriq.c

Purpose: implements the Freescale/NXP QorIQ 1588 timer PHC and exports reusable helpers for related DPAA/ENETC/eTSEC integrations. It supports time get/set/adjust, frequency adjustment, PPS events, two external timestamp inputs, optional third FIPER programming, endian-specific register access, and platform-driver probing from Device Tree.

Important APIs/types/functions: the private state type is `struct ptp_qoriq` from `linux/fsl/ptp_qoriq.h`. Exported functions include `extts_clean_up()`, `ptp_qoriq_isr()`, `ptp_qoriq_adjfine()`, `ptp_qoriq_adjtime()`, `ptp_qoriq_gettime()`, `ptp_qoriq_settime()`, `ptp_qoriq_enable()`, `ptp_qoriq_init()`, and `ptp_qoriq_free()`. `ptp_qoriq_caps` provides the default PTP operations. Register helpers read/write counter and offset registers, program alarm and FIPER values, and calculate automatic timer configuration from clock rate.

Control flow: platform probe allocates state, requests IRQ and memory resource, maps registers, then calls `ptp_qoriq_init()`. Init reads DT properties or computes defaults, selects little/big-endian accessors, chooses eTSEC versus DPAA/ENETC register layout, initializes lock and time, programs timer control/addend/prescaler/FIPER/alarm registers, starts the timer, registers the PHC, and stores the PHC index. Runtime `adjtime` adjusts `TMR_OFF` except on eTSEC, where it writes the counter directly due to hardware behavior. ISR reads event/mask, drains external timestamp FIFOs when present, emits PPS events, and acknowledges handled bits.

State and persistence: timer configuration is taken from DT or computed at probe and stored in `struct ptp_qoriq`; current time and offset are hardware state. External timestamp FIFO support, FIPER3 support, endian mode, eTSEC layout, and max adjustment are runtime configuration. Nothing is persisted by the driver.

Dependencies and integration: depends on OF platform resources, IRQs, clocks for auto-configuration, QorIQ register definitions and accessors, PTP core, and exported symbols used by other NXP networking drivers. Compatible strings include `fsl,etsec-ptp` and `fsl,fman-ptp-timer`, while init logic also recognizes `fsl,dpaa2-ptp` and `fsl,enetc-ptp` for FIPER3 behavior.

Risks and test signals: DT property omissions fall back to auto-config, which requires a clock above 100 MHz and a nominal frequency dividing 1000 MHz. `ptp_qoriq_adjfine()` does not take the main spinlock while writing `tmr_add`. External timestamp FIFO cleanup can emit multiple events per IRQ. Probe uses manual resource management, so each failure label must release the matching resource. Test with big/little endian DT, eTSEC and non-eTSEC layouts, missing-property auto-config, PPS and EXTS events, settime/adjtime while PPS active, exported helper users, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_qoriq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_s390.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_s390.c

Purpose: registers s390 architecture PTP clocks backed by the STCKE/TOD clock and the physical clock queried with PTFF QPT. These clocks are read-only references for s390 environments rather than steerable PHCs.

Important APIs/types/functions: globals `ptp_stcke_clock` and `ptp_qpt_clock` store the two registered PHCs. `ptp_s390_stcke_gettime()` requires `stp_enabled()`, calls `store_tod_clock_ext()`, and converts extended TOD to Unix `timespec64`. `ptp_s390_qpt_gettime()` calls `ptff(..., PTFF_QPT)`. `ptp_s390_getcrosststamp()` wraps `get_device_system_crosststamp()` with `s390_arch_ptp_get_crosststamp()`, which reports `CSID_S390_TOD`. Adjustment and settime callbacks return `-EOPNOTSUPP`.

Control flow: module init registers `"s390 STCKE Clock"` first, then `"s390 Physical Clock"`; if the second registration fails, the first is unregistered. Runtime reads convert TOD values relative to `TOD_UNIX_EPOCH`. Crosstimestamp is available only when STP is enabled.

State and persistence: no adjustable or persistent state. The module only stores registered clock pointers.

Dependencies and integration: depends on s390 STP/TOD architecture APIs, PTP core, and `ptp_private.h` for module-private PTP declarations. Userspace sees two PTP devices when registration succeeds.

Risks and test signals: STCKE read and crosstimestamp return unsupported when STP is disabled, but QPT read does not perform the same check. Conversion correctness depends on TOD epoch constants and nanosecond conversion helpers. Test module load/unload, both PHC names, STP enabled/disabled behavior, `PTP_SYS_OFFSET_PRECISE` for STCKE, and repeated QPT reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_s390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_sysfs.c

Purpose: implements the generic sysfs interface for PTP class devices. It exposes clock capability metadata, controls EXTS/PEROUT/PPS features, manages virtual clock creation limits, drains the external timestamp FIFO, and creates per-pin configuration attributes.

Important APIs/types/functions: `ptp_groups[]` exports the main attribute group. Static attributes include `clock_name`, max/count capability files, `max_phase_adjustment`, `extts_enable`, `fifo`, `period`, `pps_enable`, `n_vclocks`, and `max_vclocks`. `ptp_is_attribute_visible()` hides unsupported controls based on `ptp_clock_info`. `ptp_populate_pin_groups()` and `ptp_cleanup_pin_groups()` dynamically create and free the `pins/` group. `ptp_pin_store()` calls `ptp_set_pinfunc()` under `pincfg_mux`.

Control flow: stores parse simple text commands and call the driver `enable()` callback with a `struct ptp_clock_request`. `extts_enable` expects an index and enable flag. `period` expects index, start seconds/nanoseconds, and period seconds/nanoseconds, enabling when period is nonzero. `pps_enable` requires `CAP_SYS_TIME`. `fifo` reads and removes one event from the first timestamp queue. `n_vclocks_store()` creates or removes child virtual clocks to reach the requested count, updates the parent `vclock_index[]`, and logs free-running behavior for parents without cycle support. `max_vclocks_store()` resizes the index array when it will not truncate existing virtual clocks.

State and persistence: sysfs writes mutate live PTP device state only. Virtual clock count and max count persist for the lifetime of the parent `struct ptp_clock`; they are not stored across unregister/reboot. FIFO reads consume queued external timestamp events.

Dependencies and integration: depends on PTP private structures, capability checks, sysfs attribute groups, dynamic allocation helpers, child device iteration, and `ptp_vclock_register/unregister()`.

Risks and test signals: the sysfs FIFO intentionally drains only the first queue. `max_vclocks_store()` declares an `unsigned int *` for storage allocated and used as `int *`, which is type-inconsistent though same-sized on normal platforms. Vclock deletion uses `device_for_each_child_reverse()` and a non-error `-EINVAL` break convention. Test visibility for clocks with/without EXTS/PEROUT/PPS/phase support, permission checks for PPS, malformed store input, FIFO wraparound, growing/shrinking vclocks under concurrency, pin name lookup, and cleanup after partial pin group allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_vclock.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_vclock.c

Purpose: implements virtual PTP clocks layered on a physical PTP clock. A virtual clock has independent time and frequency adjustment while deriving its raw cycle base from the parent clock, allowing multiple consumers to discipline separate PHC views.

Important APIs/types/functions: `struct ptp_vclock` is defined in `ptp_private.h`. This file maintains an RCU hash table from virtual PHC index to vclock for timestamp conversion. `ptp_vclock_register()` creates and registers a child PTP clock. `ptp_vclock_unregister()` removes it. `ptp_get_vclocks_index()` returns child PHC indexes for a physical clock when the PTP core is built in. `ptp_convert_timestamp()` converts a hardware timestamp to a selected virtual clock domain. Clock operations include `ptp_vclock_adjfine()`, `adjtime()`, `gettime()`, `gettimex()`, `settime()`, `getcrosststamp()`, and periodic refresh.

Control flow: registration allocates a vclock, copies default info, selects `gettimex64` when the parent provides `getcyclesx64` otherwise `gettime64`, enables crosstimestamp if the parent provides `getcrosscycles`, registers the child with the parent device, sets a lockdep subclass, initializes the timecounter at zero, schedules refresh, and inserts into the hash. Reads either call parent `getcycles64()` through the cyclecounter or use parent cycle/crosstimestamp APIs to convert parent cycles through the virtual timecounter. Adjustments update the timecounter and multiplier under the vclock mutex.

State and persistence: virtual time offset/frequency live in the child timecounter/cyclecounter and are lost when the vclock is unregistered. The global RCU hash persists only while children exist. Parent `vclock_index[]` state is managed by sysfs code.

Dependencies and integration: tightly coupled to `ptp_sysfs.c`, `ptp_private.h`, parent PTP driver cycle APIs, timecounter/cyclecounter math, RCU, and PTP class device lookup. Built-in-only exported helpers are used by timestamp consumers that need to map hardware timestamps into virtual clock time.

Risks and test signals: virtual clocks cannot safely stack on other virtual clocks. Parent clocks without cycle support may need free-running behavior while children exist. `ptp_convert_timestamp()` returns zero time if the vclock index is not found or the mutex is interrupted, so callers need to treat zero carefully. Test child creation/deletion, parent removal with children, independent adjfine/adjtime/settime, crosstimestamp conversion, RCU lookup during unregister, and built-in export users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_vclock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_vmclock.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_vmclock.c

Purpose: implements a platform driver for the VMCLOCK shared-memory ABI used by virtual machines. It can expose the shared ABI page through a misc device and, when the ABI contains valid time data, register a read-only PTP clock with precise crosstimestamp support.

Important APIs/types/functions: `struct vmclock_state` stores the memory resource, mapped `struct vmclock_abi`, misc device, waitqueue, PTP info/clock, clocksource IDs, instance index, and name. `vmclock_get_crosststamp()` is the core ABI reader: it validates sequence counts and reliability, reads system/counter snapshots, applies counter period math, converts UTC to TAI when possible, and returns device time plus optional system counter. `vmclock_get_crosststamp_kvmclock()` handles x86 systems using KVM clock by converting TSC cycles through pvclock. `vmclock_ptp_register()` validates counter type and TAI semantics before registering the PHC. Misc operations are `mmap`, `read`, `poll`, `open`, and `release`.

Control flow: probe obtains the memory resource from ACPI `_CRS` or Device Tree, validates size/magic/version, maps it write-back/decrypted-capable, allocates an IDA index and name, installs cleanup actions, sets up ACPI or OF notification if advertised, registers a misc device when the ABI page is at least one page, and registers a PTP clock when time fields are present. `gettimex64` calls the seqcount-protected reader and fills system timestamp windows. `getcrosststamp` uses `get_device_system_crosststamp()` and, on x86, retries after detecting whether the system clocksource is TSC or KVM clock.

State and persistence: the authoritative clock data lives in hypervisor-owned shared memory. Driver state is runtime-only. Each opened misc file tracks the last observed sequence for poll/read behavior. Notifications wake `disrupt_wait` but do not persist any data.

Dependencies and integration: integrates with ACPI IDs `AMZNC10C`/`VMCLOCK`, OF compatible `amazon,vmclock`, platform resources, `devm_memremap()`, miscdevice, mmap, poll, PTP core, VM clock UAPI, generic cycles, and optional x86 KVM pvclock support.

Risks and test signals: sequence-count loops time out after 100 ms; bad hypervisor writes can produce `-ETIMEDOUT` or `-EINVAL`. The driver only registers PTP if time is unambiguous TAI or UTC with a valid TAI offset. Poll returns `POLLHUP` when notifications are not present to avoid sleeping forever. The probe check `if (!st->miscdev.minor && !st->ptp_clock)` is sensitive because dynamic minor zero can be a valid registered misc minor; this deserves review. Test ACPI and DT probing, malformed ABI headers, short regions, misc mmap/read/poll with and without notifications, TAI/UTC offset cases, unreliable clock status, x86 KVM-clock fallback, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_vmclock.c -->
