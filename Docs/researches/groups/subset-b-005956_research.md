# subset-b-005956

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_ana.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_ana.h

Purpose: defines register bit masks, field encoders, field masks, and field extractors for the Microsemi/Microchip Ocelot ANA analyzer block. It covers ingress learning/aging, storm control, flooding, sFlow, VLAN and ISDX tables, stream/SFID/SG tables, per-port VLAN/QoS/VCAP/CPU-forwarding policy, PFC, OAM/IPT, DSCP, VCAP ranges, policers, and aggregation controls.

Important APIs/types/functions: this header exports macros only. Important groups include `ANA_TABLES_MACACCESS_*` plus `MACACCESS_CMD_*` for MAC table transactions, `ANA_TABLES_VLANACCESS_*` and command constants for VLAN table writes, `ANA_PORT_*` groups for per-port policy, `ANA_CPUQ_*` for exception queues, `ANA_POL_*` for ingress policers, and `*_RSZ`/`*_GSZ` constants used to index replicated registers.

Control flow: none is implemented in the header. Runtime flow is imposed by consumers that compose values with these macros, write index/data registers, then trigger hardware table commands and poll for completion. The table command constants define the key state transitions visible to software, such as learn, forget, age, get-next, init, read, and write.

State and persistence: all persistent state is hardware state in analyzer registers and SRAM/TCAM-style tables. Writes affect forwarding, learning, VLAN classification, CPU trapping, QoS classification, stream gates, and policer state until reset or later driver reconfiguration.

Dependencies and integration: depends on Linux `BIT()` and `GENMASK()` macro availability through includers. It is included by the common Ocelot Ethernet driver and DSA variants, including Felix/Seville support, where it integrates with bridge/VLAN, switchdev, tc flower, PTP trapping, MRP, policing, and statistics paths.

Risks: field widths are hardware ABI. Bad masks, shifts, port bitmaps, or command values can corrupt forwarding state, leak traffic between VLANs, drop control traffic, or stall table accesses. Replicated register size constants must match register-map definitions. Test signals are switchdev VLAN/bridge tests, tc flower offload tests, PTP trap tests, MRP tests, traffic flooding/learning checks, and hardware register readback on Ocelot/Felix boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_ana.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_dev.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_dev.h

Purpose: defines bitfields for Ocelot per-port DEV blocks, including port reset and link speed, MAC enable/mode/tag/IFG/half-duplex/debug/sticky status, Energy Efficient Ethernet, PTP prediction, MAC Merge preemption status, 1G PCS/SGMII/auto-negotiation/LPI/test-pattern controls, and 100FX PCS controls.

Important APIs/types/functions: macro-only API. Key groups are `DEV_CLOCK_CFG_*`, `DEV_MAC_*`, `DEV_EEE_CFG_*`, `DEV_MM_*`, `PCS1G_*`, and `DEV_PCS_FX100_*`. Encoder and extractor macros provide the values consumed by `ocelot_port` setup, phylink, MAC Merge, and link-state paths.

Control flow: none in the header. Consumers sequence reset, PCS/MAC mode setup, link speed encoding, enabling RX/TX, then status or sticky-bit inspection. Auto-negotiation and LPI behavior is driven by hardware once the fields are programmed.

State and persistence: persistent state is in port device registers. Sticky status bits persist until cleared by the driver. MAC Merge verification and PCS auto-negotiation status represent hardware progress rather than software-owned state.

Dependencies and integration: uses `BIT()`/`GENMASK()` and is included by the MSCC Ethernet stack, DSA Ocelot/Felix code, and MAC Merge support. It integrates with phylink, ethtool link mode reporting, frame preemption, and PTP timing support.

Risks: wrong reset ordering or speed encodings can leave the MAC/PCS unusable. Sticky-bit handling can lose diagnostics if cleared too eagerly. MAC Merge fields affect express/preemptible traffic behavior, so regressions can break TSN/preemption tests. Test signals include link-up/down across speeds, SGMII auto-negotiation, EEE, 100FX, frame preemption, and register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_hsio.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_hsio.h

Purpose: maps the Ocelot HSIO register space and bitfields for PLL5G, resistance compensation, recovered clock, 1G and 6G SerDes lanes, memory-control-block access, QSGMII, clock division, and the temperature sensor.

Important APIs/types/functions: macro-only API. It defines register offsets such as `HSIO_PLL5G_CFG0`, `HSIO_S1G_*`, `HSIO_S6G_*`, `HSIO_MCB_*`, and `HSIO_TEMP_SENSOR_*`, plus field encoders/extractors for PLL calibration, lane power/reset, signal detect, serializer/deserializer tuning, BIST, QSGMII lane status, and temperature samples.

Control flow: no C control flow is present. Consumer drivers program PLL and lane parameters, trigger one-shot MCB reads/writes, poll calibration/lock/status bits, and enable or reset SerDes lanes. Hardware state machines perform PLL locking, input-buffer calibration, PRBS/BIST, and temperature sampling.

State and persistence: persistent state is in HSIO registers and lane analog configuration. Status bits expose lock, calibration, signal-detect, BIST, revision, and temperature state. These settings are reset-sensitive and board/link-mode dependent.

Dependencies and integration: included by `drivers/phy/mscc/phy-ocelot-serdes.c` and Ocelot Ethernet initialization code. It integrates the switch driver with PHY/SerDes lane configuration, QSGMII setup, recovered-clock output, and thermal/status diagnostics.

Risks: these fields control analog SerDes behavior, so incorrect masks or initialization order can prevent link training, destabilize clocks, or misconfigure QSGMII lanes. BIST/status polarity such as done/not-done bits must be handled carefully. Test signals include SerDes probe, link at 1G/2.5G/QSGMII modes, PLL lock polling, PRBS/BIST where available, and temperature register readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_hsio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_ptp.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_ptp.h

Purpose: declares the Ocelot PTP hardware clock interface and exposes PTP pin/action and clock-adjustment register bits used by the MSCC switch driver.

Important APIs/types/functions: exports `ocelot_ptp_gettime64`, `ocelot_ptp_settime64`, `ocelot_ptp_adjtime`, `ocelot_ptp_adjfine`, `ocelot_ptp_verify`, `ocelot_ptp_enable`, `ocelot_init_timestamp`, and `ocelot_deinit_timestamp`. It also defines `OCELOT_MAX_PTP_ID`, `OCELOT_PTP_FIFO_SIZE`, pin register strides, `PTP_PIN_ACTION_*`, `PTP_CFG_MISC_PTP_EN`, and clock adjustment bits.

Control flow: implementations in `ocelot_ptp.c` bind these callbacks into `struct ptp_clock_info`, read/set TOD registers, adjust time or frequency, configure external timestamp/perout pins, and install VCAP traps for PTP packets. The header is the common contract used by platform-specific Ocelot and Felix drivers.

State and persistence: state lives in hardware TOD, adjustment registers, timestamp FIFOs, pin configuration, and VCAP trap rules. Initialization registers a PHC and deinitialization tears it down.

Dependencies and integration: depends on `linux/ptp_clock_kernel.h` and `soc/mscc/ocelot.h`. It integrates with Linux PTP, DSA tagging transmit rewrite operations, RX/TX timestamp handling, IRQ handlers, and VCAP filters for L2/IPv4/IPv6 PTP trapping.

Risks: timestamp FIFO overflow, wrong pin action encoding, or incorrect one-step/two-step rewrite handling can corrupt time sync. Test signals include PHC get/set/adj tests, `ptp4l` traffic, external timestamp/perout validation, TX/RX timestamp paths, and FIFO overflow handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_qsys.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_qsys.h

Purpose: defines register bitfields for the Ocelot QSYS queuing and scheduling block. It covers port dequeue modes, drop/stat counter modes, EEE thresholds, external CPU queues, queue-to-scheduler mapping, timed-frame control, RED profiles, resource counters, queue maximum SDU, frame preemption, shapers, scheduler elements, DLB sensing, TAS gate-list programming, and tag configuration.

Important APIs/types/functions: macro-only API. Important groups include `QSYS_PORT_MODE_*`, `QSYS_QMAP_*`, `QSYS_TFRM_*`, `QSYS_PREEMPTION_CFG_*`, `QSYS_CIR_CFG_*`, `QSYS_EIR_CFG_*`, `QSYS_SE_*`, `QSYS_TAG_CONFIG_*`, and `QSYS_TAS_*`.

Control flow: runtime code writes queue/shaper/scheduler fields, connects scheduler elements, updates preemption/TAS parameters, and polls status registers for pending configuration or resource state. The header encodes hardware operations but does not execute them.

State and persistence: persistent hardware state includes scheduler tree topology, shaper rates and buckets, queue limits, frame preemption configuration, gate-control lists, and statistics modes. State is reset or replaced by later switch configuration.

Dependencies and integration: included by Ocelot/Felix Ethernet and DSA code and by MAC Merge support. It integrates with tc/taprio, mqprio, frame preemption, QoS, pause/PFC, CPU-port handling, and switch statistics.

Risks: scheduler and TAS fields are timing-sensitive. Bad queue maps or shaper values can starve traffic, violate gate schedules, or break preemption. Test signals include traffic shaping, taprio gate schedules, preemption verification, max-SDU enforcement, queue stats, and CPU-port forwarding tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_qsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_sys.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_sys.h

Purpose: defines bitfields for the Ocelot SYS block, which provides port counters, front-port mode, frame aging, statistics view/clear controls, switch status, PTP timestamp extraction, pause/flow-control configuration, memory manager counters, event status, and RAM initialization.

Important APIs/types/functions: macro-only API. Key groups include `SYS_COUNT_*`, `SYS_STAT_CFG_*`, `SYS_MAC_FC_CFG_*`, `SYS_MMGT_*`, `SYS_EVENTS_*`, `SYS_PTP_STATUS_*`, `SYS_PTP_TXSTAMP_*`, `SYS_PTP_CFG_*`, and `SYS_RAM_INIT_*`.

Control flow: consumers select counter views, clear statistics, configure flow-control thresholds, read memory-manager status, and pull PTP TX timestamp messages by checking status and advancing with `SYS_PTP_NXT_PTP_NXT`.

State and persistence: state is in SYS registers, counters, memory-manager status, flow-control configuration, and PTP timestamp FIFO/status fields. Counter and sticky-like event state persists until cleared or advanced.

Dependencies and integration: included by common Ocelot code, DSA variants, and `ocelot_ptp.c`. It integrates with ethtool stats, pause/PFC support, PTP TX timestamp reporting, and low-level switch initialization.

Risks: incorrect counter view selection can report wrong stats; mishandling PTP FIFO valid/next bits can drop timestamps; bad flow-control thresholds can cause pause storms or loss. Test signals include stats read/clear tests, pause frame behavior, PTP TX timestamp validation, and RAM init/probe checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_sys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_vcap.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_vcap.h

Purpose: defines the public model for Ocelot VCAP programmable classification blocks ES0, IS1, and IS2. It describes hardware properties, TCAM update registers, key/action field IDs, typed match structures, action payloads, filter identity/statistics, private driver cookies, and filter management APIs.

Important APIs/types/functions: key exports are `struct vcap_props`, `struct vcap_field`, typed match structs such as `ocelot_vcap_key_vlan`, `ocelot_vcap_key_ipv4`, and `ocelot_vcap_key_ipv6`, `struct ocelot_vcap_action`, `struct ocelot_vcap_filter`, and APIs `ocelot_vcap_filter_add`, `ocelot_vcap_filter_del`, `ocelot_vcap_filter_replace`, and `ocelot_vcap_block_find_filter_by_id`.

Control flow: users allocate and populate `struct ocelot_vcap_filter`, choose a block/key/action, set cookie/offload identity, then add, replace, delete, or query stats through `ocelot_vcap.c`. The implementation packs fields using the property tables, writes cache rows, issues VCAP update commands, and maintains ordered filter lists.

State and persistence: software state is in per-block filter lists, cookies, TC offload IDs, stats, policer indices, and trap flags. Persistent hardware state is TCAM entries, masks, actions, counters, and optional policers until removed or reset.

Dependencies and integration: depends on `soc/mscc/ocelot.h`, Linux list/netlink types through includers, and VSC7514/Felix property tables. It integrates with tc flower, VLAN tag push/pop rules, PTP and MRP traps, mirroring, policing, DSA tag rules, and switchdev offload.

Risks: VCAP packing is bit-exact and priority/order-sensitive. Duplicate cookies, wrong key type, mismatched port masks, or bad action widths can shadow rules, leak traffic, mis-trap PTP/MRP packets, or corrupt counters. Test signals include tc flower add/delete/replace/stats, VLAN rewrite, PTP trap installation, MRP trap tests, policer resource cleanup, and hardware hit counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_vcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/vsc7514_regs.h -->
# sources/distributed-fs/ceph-client/include/soc/mscc/vsc7514_regs.h

Purpose: declares the VSC7514-specific Ocelot register-map data shared by platform and DSA glue.

Important APIs/types/functions: exports `vsc7514_vcap_props[]`, `vsc7514_regfields[REGFIELD_MAX]`, and `vsc7514_regmap[TARGET_MAX]`. These are defined in `drivers/net/ethernet/mscc/vsc7514_regs.c`.

Control flow: none in the header. Probe code selects these tables to bind generic Ocelot register targets, regfields, and VCAP property descriptions to VSC7514 hardware.

State and persistence: the header owns no mutable state. The declared arrays are static hardware-description data used to compute register offsets and field positions at runtime.

Dependencies and integration: includes `soc/mscc/ocelot_vcap.h` and relies on Ocelot target/regfield enums from the broader switch headers. It is included by VSC7514 Ethernet and DSA extension code.

Risks: any mismatch between these arrays and silicon layout redirects register writes to the wrong block. Test signals include VSC7514 probe, regmap access, VCAP rule programming, PTP initialization, and DSA/ext switch operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/mscc/vsc7514_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/nuvoton/clock-npcm8xx.h -->
# sources/distributed-fs/ceph-client/include/soc/nuvoton/clock-npcm8xx.h

Purpose: defines the auxiliary-bus wrapper used to share NPCM8xx clock-controller register base state with auxiliary child devices.

Important APIs/types/functions: provides `struct npcm_clock_adev` with `void __iomem *base` and embedded `struct auxiliary_device adev`, plus `to_npcm_clock_adev()` using `container_of()`.

Control flow: no runtime flow beyond the inline cast helper. The primary clock driver creates or passes auxiliary devices; reset or other child drivers recover the containing object with the helper.

State and persistence: the persistent state is the MMIO base pointer and auxiliary-device lifetime. The header does not allocate, free, or modify hardware state.

Dependencies and integration: depends on `linux/auxiliary_bus.h` and `linux/container_of.h`. It is included by `drivers/clk/clk-npcm8xx.c` and `drivers/reset/reset-npcm.c`.

Risks: container casts require that the supplied auxiliary device is embedded in `struct npcm_clock_adev`. A wrong object type corrupts memory access. Test signals include NPCM8xx clock/reset probe, auxiliary-device binding, and reset register operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/nuvoton/clock-npcm8xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/cmd-db.h -->
# sources/distributed-fs/ceph-client/include/soc/qcom/cmd-db.h

Purpose: declares the Qualcomm Command DB API used to look up firmware-described resource addresses, auxiliary data, resource address matching, and hardware slave IDs for RPMh-managed resources.

Important APIs/types/functions: defines `enum cmd_db_hw_type` with ARC, VRM, BCM, and all/invalid values. When `CONFIG_QCOM_COMMAND_DB` is enabled it exports `cmd_db_read_addr`, `cmd_db_read_aux_data`, `cmd_db_match_resource_addr`, `cmd_db_read_slave_id`, and `cmd_db_ready`; otherwise it provides `-ENODEV`, `ERR_PTR(-ENODEV)`, zero, or false stubs.

Control flow: callers normally wait for `cmd_db_ready()`, look up a resource ID, then use the returned address/slave data to build RPMh/TCS commands. Disabled-config flow fails fast through inline stubs.

State and persistence: command-db state is firmware/platform data parsed by `drivers/soc/qcom/cmd-db.c`; this header does not store state. Returned auxiliary data pointers are owned by the command DB implementation.

Dependencies and integration: depends on `linux/err.h`. Consumers include RPMh regulators, clocks, power domains, interconnect BCM voter code, GMU/HFI GPU code, and RPMh RSC.

Risks: resource IDs are firmware ABI strings. Missing DB readiness or bad address matching can vote the wrong resource or fail probe. Test signals include RPMh clock/regulator/interconnect probe, command DB lookup failures, and boot on configs with and without `CONFIG_QCOM_COMMAND_DB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/cmd-db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/ice.h -->
# sources/distributed-fs/ceph-client/include/soc/qcom/ice.h

Purpose: declares the Qualcomm Inline Crypto Engine API used by storage drivers to enable ICE, manage suspend/resume, program and evict crypto keys, and handle wrapped-key operations.

Important APIs/types/functions: forward-declares `struct qcom_ice` and exports `qcom_ice_enable`, `qcom_ice_resume`, `qcom_ice_suspend`, `qcom_ice_program_key`, `qcom_ice_evict_key`, `qcom_ice_get_supported_key_type`, `qcom_ice_derive_sw_secret`, `qcom_ice_generate_key`, `qcom_ice_prepare_key`, `qcom_ice_import_key`, and `devm_of_qcom_ice_get`.

Control flow: storage drivers acquire an ICE instance from device tree, enable or resume it, ask what key type is supported, program key slots for blk-crypto, evict slots when no longer needed, and use wrapped-key helpers for generate/import/prepare/derive flows.

State and persistence: state is held by the ICE driver and hardware key slots. Key material and wrapped-key buffers are security-sensitive and must be invalidated or evicted by callers.

Dependencies and integration: depends on `linux/blk-crypto.h` and `linux/types.h`. Consumers include `sdhci-msm` and `ufs-qcom`; implementation is in `drivers/soc/qcom/ice.c`.

Risks: slot mismatch, suspend/resume ordering, unsupported key type handling, or incorrect buffer sizes can break storage encryption or expose key material. Test signals include blk-crypto self-tests, UFS/eMMC encrypted IO, suspend/resume cycles, wrapped-key flows, and key eviction error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/ice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/kryo-l2-accessors.h -->
# sources/distributed-fs/ceph-client/include/soc/qcom/kryo-l2-accessors.h

Purpose: declares low-level accessors for Qualcomm Kryo L2 indirect registers.

Important APIs/types/functions: exports `kryo_l2_set_indirect_reg(u64 reg, u64 val)` and `kryo_l2_get_indirect_reg(u64 reg)`.

Control flow: consumers pass an indirect register selector and either write a value or read the current value. The implementation serializes the platform-specific indirect access sequence.

State and persistence: the accessors read and write CPU/L2 PMU and cache-control registers. Persistent effects depend on the selected register, including counter enables, event types, filters, overflow status, and CPU clock configuration fields.

Dependencies and integration: implemented in `drivers/soc/qcom/kryo-l2-accessors.c`. Consumers include `drivers/perf/qcom_l2_pmu.c` and Qualcomm CPU clock code.

Risks: these are privileged CPU-register accesses. Wrong register IDs or concurrency mistakes can corrupt PMU state or CPU clock behavior. Test signals include qcom L2 PMU perf event tests, counter overflow handling, CPU clock changes, and SMP stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/kryo-l2-accessors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/ocmem.h -->
# sources/distributed-fs/ceph-client/include/soc/qcom/ocmem.h

Purpose: declares the Qualcomm OCMEM allocator API for on-chip memory used by performance, latency, and power-sensitive clients such as GPU, camera/video, and audio blocks.

Important APIs/types/functions: defines `enum ocmem_client` with `OCMEM_GRAPHICS`, opaque `struct ocmem`, and `struct ocmem_buf` containing `offset`, `addr`, and `len`. When `CONFIG_QCOM_OCMEM` is enabled it exports `of_get_ocmem`, `ocmem_allocate`, and `ocmem_free`; otherwise it provides disabled stubs.

Control flow: clients get the OCMEM provider from device tree, allocate a buffer for a client ID and size, use the returned physical/address window, and release it with `ocmem_free`. Disabled builds fail with `ERR_PTR(-ENODEV)`.

State and persistence: state is allocator-owned OCMEM address space and per-client allocations. Buffers persist until explicitly freed or provider teardown.

Dependencies and integration: depends on `linux/device.h` and `linux/err.h`. Implementation is in `drivers/soc/qcom/ocmem.c`; consumers include MSM Adreno GPU code and SCM OCMEM lock/unlock paths.

Risks: limited client support, allocation lifetime leaks, and address/offset confusion can starve clients or program firmware with wrong ranges. Test signals include GPU probe/use on OCMEM SoCs, allocation/free failure paths, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/ocmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/qcom-spmi-pmic.h -->
# sources/distributed-fs/ceph-client/include/soc/qcom/qcom-spmi-pmic.h

Purpose: provides Qualcomm SPMI PMIC subtype/fabric constants and the PMIC identity structure used by child drivers to tailor behavior to exact PMIC revisions.

Important APIs/types/functions: defines many `*_SUBTYPE` constants, PMIC fabric IDs such as `PMI8998_FAB_ID_*` and `PM660_FAB_ID_*`, `struct qcom_spmi_pmic` with type, subtype, revision, fab ID, and name, and `qcom_pmic_get(struct device *dev)`.

Control flow: PMIC MFD code identifies the device, stores identity data, and consumers call `qcom_pmic_get()` from child devices to branch on subtype or revision.

State and persistence: the header owns no state. PMIC identity persists in the provider device data after SPMI probe.

Dependencies and integration: depends on `linux/device.h`. Used by `drivers/mfd/qcom-spmi-pmic.c` and consumers such as RRADC and other PMIC subdevice drivers.

Risks: subtype values are hardware ABI. Wrong constants or failed lookup can select invalid calibration, scaling, or quirks. Test signals include SPMI PMIC probe logs, child-device lookup, subtype-specific ADC/regulator behavior, and builds across PMIC families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/qcom-spmi-pmic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/rpmh.h -->
# sources/distributed-fs/ceph-client/include/soc/qcom/rpmh.h

Purpose: declares the public Qualcomm RPMh write API for sending TCS command arrays to the Resource Power Manager hardware accelerator.

Important APIs/types/functions: when `CONFIG_QCOM_RPMH` is enabled, exports `rpmh_write`, `rpmh_write_async`, `rpmh_write_batch`, and `rpmh_invalidate`; disabled builds return `-ENODEV` or no-op invalidate. The API consumes `enum rpmh_state` and `struct tcs_cmd` from `soc/qcom/tcs.h`.

Control flow: clients build one or more TCS commands, choose sleep, wake-only, or active-only state, then issue synchronous, asynchronous, or batch writes. `rpmh_invalidate()` clears cached/aggregated state for a device.

State and persistence: RPMh implementation maintains request aggregation and state caches; hardware stores active/sleep/wake votes in TCS/RSC resources. This header has no state.

Dependencies and integration: depends on `soc/qcom/tcs.h` and `linux/platform_device.h`. Consumers include RPMh regulators, clocks, power domains, interconnect BCM voting, and SoC drivers.

Risks: wrong state selection or command count can leave resources underpowered, overpowered, or stuck across suspend. Async writes have different completion semantics than sync writes. Test signals include RPMh regulator/clock/interconnect probe, suspend/resume, command timeout handling, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/rpmh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/spm.h -->
# sources/distributed-fs/ceph-client/include/soc/qcom/spm.h

Purpose: declares Qualcomm Subsystem Power Manager low-power mode selection for CPU idle paths.

Important APIs/types/functions: defines `enum pm_sleep_mode` with standby, retention, standalone power collapse, power collapse, and count values, forward-declares `struct spm_driver_data`, and exports `spm_set_low_power_mode()`.

Control flow: cpuidle or platform code selects a low-power mode and calls `spm_set_low_power_mode()` on driver data; the implementation updates SPM sequence/register programming for the next idle entry.

State and persistence: mode selection persists in SPM driver/hardware configuration until changed. The header owns no state.

Dependencies and integration: implemented in `drivers/soc/qcom/spm.c` and consumed by `drivers/cpuidle/cpuidle-qcom-spm.c`.

Risks: choosing an unsupported or wrong mode can break CPU idle, wakeup latency, or power-collapse resume. Test signals include cpuidle state transitions, suspend/resume, power measurements, and wakeup-source validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/spm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/tcs.h -->
# sources/distributed-fs/ceph-client/include/soc/qcom/tcs.h

Purpose: defines Qualcomm Trigger Command Set request structures and Bus Clock Manager command packing used by RPMh clients.

Important APIs/types/functions: defines `MAX_RPMH_PAYLOAD`, `enum rpmh_state`, `struct tcs_cmd`, `struct tcs_request`, BCM field masks, and `BCM_TCS_CMD(commit, valid, vote_x, vote_y)` built with `u32_encode_bits()`.

Control flow: clients build `struct tcs_cmd` arrays, optionally wrap them in `struct tcs_request`, then submit through RPMh APIs or RSC internals. The `wait` flag has specific meaning for active-only batch writes, while `rpmh_write()` and async writes impose their own completion semantics.

State and persistence: structures are request descriptors. Persistent effects occur in RPMh resources after commands are accepted by hardware.

Dependencies and integration: depends on `linux/bitfield.h` and `linux/bits.h`. Included by RPMh core, RPMh RSC, BCM interconnect voter, clock/regulator/power-domain drivers, and Adreno GMU/HFI code.

Risks: exceeding `MAX_RPMH_PAYLOAD`, bad address encoding, or incorrect wait semantics can fail requests or deadlock callers. BCM vote packing must preserve valid/commit bits and X/Y vote widths. Test signals include interconnect bandwidth votes, RPMh batch writes, active/sleep/wake state transitions, and compile-time checks for users of the structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/qcom/tcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/pm_domains.h -->
# sources/distributed-fs/ceph-client/include/soc/rockchip/pm_domains.h

Purpose: declares Rockchip PMU block/unblock helpers used by drivers that need to serialize sensitive PMU or DRAM-frequency interactions with power-domain changes.

Important APIs/types/functions: exports `rockchip_pmu_block()` and `rockchip_pmu_unblock()` when `CONFIG_ROCKCHIP_PM_DOMAINS` is enabled; otherwise provides success/no-op stubs.

Control flow: callers block PMU power-domain transitions, perform their protected operation, then unblock. Disabled builds allow callers to compile and proceed without PM-domain coordination.

State and persistence: implementation-owned block state likely gates PM-domain transitions. The header owns no state.

Dependencies and integration: consumed by Rockchip PM-domain and devfreq/DMC code such as `rk3399_dmc.c`.

Risks: missing unblock calls can freeze PM-domain changes, while missing block calls can race power changes. Test signals include Rockchip devfreq transitions, PM-domain on/off stress, suspend/resume, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/pm_domains.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rk3399_grf.h -->
# sources/distributed-fs/ceph-client/include/soc/rockchip/rk3399_grf.h

Purpose: defines RK3399 PMU GRF register offset and bit masks for DDR type and channel bus-width discovery.

Important APIs/types/functions: provides `RK3399_PMUGRF_OS_REG2`, `RK3399_PMUGRF_OS_REG2_DDRTYPE`, `RK3399_PMUGRF_OS_REG2_BW_CH0`, and `RK3399_PMUGRF_OS_REG2_BW_CH1`.

Control flow: consumers read PMU GRF OS_REG2 through regmap and extract memory type/channel width using the masks.

State and persistence: values are bootloader/firmware-populated GRF state describing DRAM configuration. The header has no mutable state.

Dependencies and integration: relies on `GENMASK()` via includers and is used by Rockchip DFI/devfreq/DMC code along with `rockchip_grf.h`.

Risks: wrong masks misidentify memory topology, leading to bad bandwidth or devfreq calculations. Test signals include RK3399 DMC/devfreq probe, DFI event reporting, and sysfs/devfreq bandwidth sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rk3399_grf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rk3568_grf.h -->
# sources/distributed-fs/ceph-client/include/soc/rockchip/rk3568_grf.h

Purpose: defines RK3568 PMU GRF OS register offsets and masks for DRAM type, channel width, DRAM type v3, and sysreg version.

Important APIs/types/functions: provides `RK3568_PMUGRF_OS_REG2`, `RK3568_PMUGRF_OS_REG2_DRAMTYPE_INFO`, `RK3568_PMUGRF_OS_REG2_BW_CH0`, `RK3568_PMUGRF_OS_REG3`, `RK3568_PMUGRF_OS_REG3_DRAMTYPE_INFO_V3`, and `RK3568_PMUGRF_OS_REG3_SYSREG_VERSION`.

Control flow: DFI/devfreq code reads OS registers, checks sysreg version, and selects old or v3 DRAM-type interpretation.

State and persistence: values are hardware/firmware-populated GRF configuration state. The header has no runtime state.

Dependencies and integration: depends on `GENMASK()` through includers. Used by Rockchip DFI event and memory bandwidth logic.

Risks: version-dependent interpretation can misclassify DRAM if masks are wrong. Test signals include RK3568 DFI probe, memory type reporting, devfreq event counts, and boot logs on boards with different sysreg versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rk3568_grf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rk3588_grf.h -->
# sources/distributed-fs/ceph-client/include/soc/rockchip/rk3588_grf.h

Purpose: defines RK3588 PMU GRF OS register offsets and masks for DRAM type, channel widths, channel information, sysreg version, and LPDDR5 bank/CKR mode.

Important APIs/types/functions: provides `RK3588_PMUGRF_OS_REG2` through `OS_REG6`, masks for `DRAMTYPE_INFO`, `BW_CH0`, `BW_CH1`, `CH_INFO`, `DRAMTYPE_INFO_V3`, `SYSREG_VERSION`, `LP5_BANK_MODE`, and `LP5_CKR`.

Control flow: consumers read GRF OS registers and derive memory topology and LPDDR5 mode for DFI/devfreq accounting.

State and persistence: register contents describe boot-time DRAM configuration and remain persistent platform state unless firmware rewrites them.

Dependencies and integration: uses `BIT()`/`GENMASK()` via includers. It is included by Rockchip DFI event code together with common DDR type definitions.

Risks: RK3588 has more channels and LPDDR5 modes, so missing masks can skew bandwidth scaling and event interpretation. Test signals include RK3588 DFI/devfreq operation, LPDDR5 board validation, and memory bandwidth counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rk3588_grf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rockchip_grf.h -->
# sources/distributed-fs/ceph-client/include/soc/rockchip/rockchip_grf.h

Purpose: centralizes Rockchip DDR type enum values shared by SoC-specific GRF readers.

Important APIs/types/functions: defines enum values for DDR3, LPDDR2, LPDDR3, LPDDR4, LPDDR4X, and LPDDR5 as `ROCKCHIP_DDRTYPE_*`.

Control flow: no executable flow. Consumers map extracted GRF DRAM type fields to these enum values.

State and persistence: no state. The enum is a shared ABI between GRF register interpretation and memory/devfreq logic.

Dependencies and integration: included by Rockchip DMC/devfreq and DFI event drivers with SoC-specific `rk*_grf.h` headers.

Risks: enum values must match firmware/GRF encodings. Wrong values break memory-type-specific bandwidth scaling and reporting. Test signals include memory type detection on multiple Rockchip boards and DFI/devfreq behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rockchip_grf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rockchip_sip.h -->
# sources/distributed-fs/ceph-client/include/soc/rockchip/rockchip_sip.h

Purpose: defines Rockchip secure monitor call IDs and subcommands for suspend and DRAM frequency management.

Important APIs/types/functions: provides `ROCKCHIP_SIP_SUSPEND_MODE`, `ROCKCHIP_SLEEP_PD_CONFIG`, `ROCKCHIP_SIP_DRAM_FREQ`, and `ROCKCHIP_SIP_CONFIG_DRAM_*` subcommands for init, set/round/get rate, set at self-refresh, get bandwidth, clear IRQ, set params, and ODT power-down.

Control flow: callers pass these constants to ARM SMCCC/SIP calls handled by secure firmware. Kernel code uses them to request DRAM clock operations or suspend power-domain configuration.

State and persistence: effects are secure-firmware controlled DRAM frequency and suspend configuration. The header owns no state.

Dependencies and integration: consumed by Rockchip clock DDR code, PM-domain code, and RK3399 DMC/devfreq code.

Risks: SIP IDs are firmware ABI. Wrong command IDs can fail calls or invoke the wrong secure service. Test signals include DRAM frequency scaling, suspend/resume, secure monitor return-code handling, and bandwidth query validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/rockchip/rockchip_sip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/sa1100/pwer.h -->
# sources/distributed-fs/ceph-client/include/soc/sa1100/pwer.h

Purpose: declares SA1100 wake-enable helpers for GPIO and system-controller interrupt sources.

Important APIs/types/functions: exports `sa11x0_gpio_set_wake(unsigned int gpio, unsigned int on)` and `sa11x0_sc_set_wake(unsigned int irq, unsigned int on)`.

Control flow: GPIO, IRQ, or machine code calls these helpers to enable or disable wake capability for a source before entering low-power states.

State and persistence: wake configuration persists in SA1100 power/wakeup registers until changed. The header owns no state.

Dependencies and integration: included by SA1100 IRQ, GPIO, and mach generic code.

Risks: incorrect source numbers or enable flags can prevent wakeup or cause unwanted wake events. Test signals include suspend/resume wake from GPIO and system-controller IRQs on SA1100 platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/sa1100/pwer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/sifive/sifive_ccache.h -->
# sources/distributed-fs/ceph-client/include/soc/sifive/sifive_ccache.h

Purpose: declares notifier registration for SiFive Composable Cache Controller error events and defines error type IDs.

Important APIs/types/functions: exports `register_sifive_ccache_error_notifier()` and `unregister_sifive_ccache_error_notifier()` for `struct notifier_block`, plus `SIFIVE_CCACHE_ERR_TYPE_CE` and `SIFIVE_CCACHE_ERR_TYPE_UE`.

Control flow: clients register a notifier, receive corrected or uncorrected cache error notifications from the ccache driver, and unregister during teardown.

State and persistence: notifier-chain membership is implementation-owned state. Error events are transient hardware interrupts/status reports.

Dependencies and integration: implemented in `drivers/cache/sifive_ccache.c` and consumed by `drivers/edac/sifive_edac.c`.

Risks: notifier lifetime errors can call freed memory or miss ECC events. Correct CE/UE classification is important for EDAC reporting. Test signals include ccache interrupt injection or hardware ECC events, EDAC report validation, and module unload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/sifive/sifive_ccache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/spacemit/ccu.h -->
# sources/distributed-fs/ceph-client/include/soc/spacemit/ccu.h

Purpose: defines the auxiliary-device wrapper shared by SpacemiT CCU clock and reset drivers.

Important APIs/types/functions: provides `struct spacemit_ccu_adev` containing an embedded `struct auxiliary_device` and `struct regmap *regmap`, plus `to_spacemit_ccu_adev()`.

Control flow: the CCU common/clock code creates auxiliary reset devices, and reset drivers recover the wrapper through the inline container helper before using the shared regmap.

State and persistence: persistent state is the auxiliary device and regmap pointer. Hardware state is accessed by consumers through regmap, not by this header.

Dependencies and integration: depends on `linux/auxiliary_bus.h` and `linux/regmap.h`. Used by SpacemiT clock and reset common code.

Risks: helper misuse with a non-SpacemiT auxiliary device corrupts container access. Regmap lifetime must outlive child reset devices. Test signals include K1/K3 CCU probe, reset auxiliary binding, and reset assert/deassert operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/spacemit/ccu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/spacemit/k1-syscon.h -->
# sources/distributed-fs/ceph-client/include/soc/spacemit/k1-syscon.h

Purpose: defines SpacemiT K1 clock/reset syscon register offsets and PLL lock bits for APBS, MPMU, APBC, APMU, RCPU, RCPU2, and APBC2 domains.

Important APIs/types/functions: macro-only API including `APBS_PLL*_SWCR*`, `MPMU_*`, `POSR_PLL*_LOCK`, many `APBC_*_CLK_RST`, `APMU_*_CLK_RES_CTRL`, `RCPU_*_CLK_RST`, `RCPU2_PWM*_CLK_RST`, and `APBC2_*_CLK_RST` offsets. It includes `ccu.h` for shared CCU auxiliary definitions.

Control flow: clock/reset drivers use the offsets to program gates, resets, muxes, dividers, and PLL controls through regmap. PLL lock bits are polled after PLL changes.

State and persistence: register contents represent persistent clock, reset, and PLL state for K1 functional blocks until reset or reconfiguration.

Dependencies and integration: included by `drivers/clk/spacemit/ccu-k1.c` and `drivers/reset/spacemit/reset-spacemit-k1.c`.

Risks: offset mistakes can gate/reset the wrong peripheral or misread PLL lock. K1 has many similarly named peripherals, so table alignment is important. Test signals include K1 clock tree registration, peripheral probe, reset controller tests, PLL lock polling, and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/spacemit/k1-syscon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/spacemit/k3-syscon.h -->
# sources/distributed-fs/ceph-client/include/soc/spacemit/k3-syscon.h

Purpose: defines SpacemiT K3 clock/reset syscon register offsets and PLL lock bits across APBS, MPMU, APBC, APMU, DCIU, RCPU SYSCTRL/UART/I2S/SPI/I2C/PWM/RPMU, and APBC2 SEC domains.

Important APIs/types/functions: macro-only API including eight PLL SWCR groups, `POSR_PLL1_LOCK` through `POSR_PLL8_LOCK`, large APBC/APMU peripheral offset sets, DCIU DMA reset/clock offsets, RCPU peripheral clock/reset offsets, and APBC2 SEC offsets. It includes `ccu.h`.

Control flow: K3 clock and reset drivers index SoC-specific clock/reset descriptors with these offsets, write through regmap, and poll PLL lock state where needed.

State and persistence: hardware clock, reset, PLL, and domain-control state persists in syscon registers until reset or later reconfiguration.

Dependencies and integration: included by `drivers/clk/spacemit/ccu-k3.c`, `drivers/reset/spacemit/reset-spacemit-k3.c`, and shared SpacemiT CCU/reset code.

Risks: K3 has a broad register surface; copied K1 names with changed offsets can create subtle peripheral failures. Duplicate-looking domains require correct reset-controller mapping. Test signals include K3 clock registration, reset-line enumeration, peripheral probe coverage, PLL lock checks, and boot smoke tests with clocks enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/spacemit/k3-syscon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/starfive/reset-starfive-jh71x0.h -->
# sources/distributed-fs/ceph-client/include/soc/starfive/reset-starfive-jh71x0.h

Purpose: defines the auxiliary-device wrapper used by StarFive JH71x0 reset drivers.

Important APIs/types/functions: provides `struct jh71x0_reset_adev` with an MMIO `base` pointer and embedded `struct auxiliary_device`, plus `to_jh71x0_reset_adev()` container macro.

Control flow: StarFive clock/syscon code creates an auxiliary reset device; reset drivers cast back to this wrapper to access the reset register base.

State and persistence: persistent state is the MMIO base and auxiliary-device lifetime. The header does not manipulate reset state directly.

Dependencies and integration: depends on auxiliary bus, compiler type, and container helpers. Used by StarFive JH7110 reset and clock support.

Risks: wrong auxiliary-device type or invalid base lifetime breaks reset register access. Test signals include JH7110 clock/reset probe, reset controller registration, and peripheral reset operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/starfive/reset-starfive-jh71x0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/ahb.h -->
# sources/distributed-fs/ceph-client/include/soc/tegra/ahb.h

Purpose: declares the Tegra AHB helper used to enable SMMU translation support through the AHB controller.

Important APIs/types/functions: exports `tegra_ahb_enable_smmu(struct device_node *ahb)`.

Control flow: Tegra SMMU code locates the AHB device node and calls this helper so the AHB driver can configure SMMU-related AHB registers.

State and persistence: the persistent state is AHB controller configuration enabling SMMU behavior. The header owns no state.

Dependencies and integration: implemented by `drivers/amba/tegra-ahb.c` and consumed by `drivers/iommu/tegra-smmu.c`; requires `struct device_node` from Open Firmware headers through includers.

Risks: failure to enable SMMU at the AHB level can leave IOMMU translations ineffective or devices inaccessible. Test signals include Tegra SMMU probe, DMA/IOMMU mapping tests, and boot on Tegra platforms using AHB-mediated SMMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/soc/tegra/ahb.h -->
