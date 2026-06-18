# subset-b-005912 Research

Grouped research for Linux regulator, relay, remoteproc, resctrl, reset, resource, syscall-resume, rethook, rfkill, rhashtable, ring-buffer, and RapidIO headers under `sources/distributed-fs/ceph-client/include/linux`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/pca9450.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/pca9450.h

Purpose: this header is the register and bit-field contract for NXP PCA9450/PCA9451/PCA9452 PMIC regulator drivers. It identifies chip variants, regulator IDs for six buck converters and five LDOs, DVS levels, voltage selector counts, register offsets through `PCA9450_MAX_REGISTER`, and restart-handler priority.

Important APIs/types/functions: no callable functions are declared. The API surface is enum/macro data consumed by regulator and MFD code: `enum pca9450_chip_type`, regulator indexes `PCA9450_BUCK1` through `PCA9450_LDO5`, DVS constants, BUCK/LDO voltage counts, register offsets, enable modes, DVS voltage masks/defaults, ramp-rate fields, interrupt bits, power timing fields, watchdog reset modes, I2C low-power transfer fields, and `SW_RST_COMMAND`.

Control flow: consumers use the enum IDs to build `regulator_desc` tables and use the register/mask macros with regmap reads, writes, and `regmap_update_bits()`. The header encodes PMIC lifecycle decisions such as enable-mode selection, DVS register selection, interrupt masking, PMIC reset timing, and watchdog-triggered warm/cold restart behavior.

State and persistence: all state is hardware register state in the PMIC. The header gives selectors and masks for persistent voltage, enable, fault, and reset-control registers; it stores no kernel runtime state itself.

Dependencies and integration points: includes `linux/regmap.h` and integrates with Linux regulator core, PMIC interrupt handling, restart handlers, watchdog reset policy, and board/device-tree configuration that chooses chip type and initial constraints.

Risks: wrong masks or register offsets can program unsafe voltages or reset behavior. BUCK/LDO default constants are silicon-policy assumptions, and the PCA9450A/BC/PCA9451A/PCA9452 variants may not support identical rails. Test signals include boot-time regmap access, regulator voltage table validation, fault interrupt decoding, suspend/standby DVS behavior, and controlled restart/watchdog tests on supported boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/pca9450.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/pfuze100.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/pfuze100.h

Purpose: this header defines regulator ID numbers for Freescale/NXP PFUZE100-family PMIC variants. It lets board data, device-tree translation, and the PFUZE regulator driver agree on stable rail indexes.

Important APIs/types/functions: no functions or structs are declared. The exported surface is macro IDs for `PFUZE100_*`, `PFUZE200_*`, `PFUZE3000_*`, and `PFUZE3001_*` rails, plus `PFUZE100_MAX_REGULATOR`. IDs cover switching regulators, boost, SNVS/reference rails, VGEN/VLDO rails, coin-cell charger, VCCSD, and V33 rails depending on model.

Control flow: probe code selects a chip variant, builds regulator descriptors in the order declared here, and maps consumer constraints to these numeric IDs. Runtime control flow lives in the driver and regulator core; this header is a compile-time ABI between the driver and platform descriptions.

State and persistence: no runtime state. The only persistence concern is ID stability because existing device-tree bindings and platform data may rely on the numbering.

Dependencies and integration points: integrates with `drivers/regulator/pfuze100-regulator.c`, regulator init data, device-tree regulator nodes, and i.MX platform power trees.

Risks: changing values or reusing names for a different rail would silently bind constraints to the wrong output. Variant-specific omissions are easy to mishandle because PFUZE200/3000/3001 do not match PFUZE100 one-for-one. Test signals are successful regulator registration counts per variant, DT binding tests, rail-name/sysfs/regulator debugfs consistency, and boot validation on PFUZE-backed boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/pfuze100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/s2dos05.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/s2dos05.h

Purpose: this header describes the Samsung S2DOS05 regulator PMIC register map, regulator IDs, IRQ bits, voltage selector geometry, enable masks, ramp delay, and enable timing constants.

Important APIs/types/functions: no functions are declared. `enum S2DOS05_reg` gives register offsets for device ID, status, enable, LDO/buck config, IRQ mask/status, thermal/short-circuit, and over-current registers. `enum S2DOS05_regulators` exposes `S2DOS05_LDO1` through `S2DOS05_BUCK1`. Macros define IRQ bits, minimum voltages, selector steps, VSEL/fast-discharge masks, enable bits, ramp delay, enable times, and voltage count calculations.

Control flow: a regulator driver uses these constants to decode IRQ status, configure voltage selectors, enable or disable specific rails through `S2DOS05_REG_EN`, and report ramp/enable delays to the regulator core. Fast-discharge and buck/LDO selector masks constrain register update operations.

State and persistence: hardware registers hold the state. This header does not allocate memory or own kernel state, but its constants describe persistent PMIC enable, voltage, interrupt, and fault state.

Dependencies and integration points: depends on common bit macros and integrates with regulator core, regmap/I2C access, PMIC IRQ handling, and Samsung/Qualcomm board power descriptions using S2DOS05.

Risks: voltage constants directly affect regulator constraints; an off-by-one voltage count or wrong enable bit can expose unsafe rail behavior. Test signals include voltage list/range tests, enable mask verification, IRQ injection or fault decoding, and regulator boot/suspend checks on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/s2dos05.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/tps51632-regulator.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/tps51632-regulator.h

Purpose: this header provides legacy platform data for the TI TPS51632 D-CAP step-down controller with serial VID and DVFS support.

Important APIs/types/functions: it declares `struct tps51632_regulator_platform_data`, containing `reg_init_data`, `enable_pwm_dvfs`, `dvfs_step_20mV`, `max_voltage_uV`, and `base_voltage_uV`. There are no functions or macros beyond include guards.

Control flow: board/platform code fills this structure before regulator driver probe. The driver then uses it to decide whether PWM-DVFS is enabled, whether DVFS steps are 10 mV or 20 mV, and how to calculate voltage limits from base and maximum microvolt values. Runtime sequencing is delegated to the regulator core and the chip driver.

State and persistence: this is initialization data only. Persistent state is either board firmware data or regulator constraints; no mutable state is stored in the header.

Dependencies and integration points: it depends on `struct regulator_init_data` and `bool` being visible to includers, and integrates with NVIDIA-era platform files and the TPS51632 regulator driver.

Risks: platform-data configuration can conflict with actual board wiring or voltage tables, especially when PWM-DVFS step mode is wrong. Test signals include driver probe with platform data, DVFS voltage transition tests, regulator constraint validation, and compile coverage for platform builds that still include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/tps51632-regulator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/tps62360.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/tps62360.h

Purpose: this header defines platform data for the TI TPS62360 processor core supply regulator.

Important APIs/types/functions: `struct tps62360_regulator_platform_data` contains `reg_init_data`, `en_discharge`, `en_internal_pulldn`, and default state flags for `vsel0` and `vsel1`. There are no callable functions.

Control flow: platform or board code provides this data to the regulator driver during probe. The driver uses it to initialize output capacitor discharge, internal pulldown, and VSEL pin default assumptions before registering with the regulator core. Later voltage selection and enable operations happen in the driver.

State and persistence: the structure is initialization policy, not ongoing state. The real persistent state is chip register/pin state and regulator framework constraints.

Dependencies and integration points: depends on regulator core init data and normal kernel boolean types. It integrates with platform-data based ARM/NVIDIA board files and the TPS62360 regulator driver.

Risks: incorrect VSEL defaults can make the driver believe a different voltage bank is active than the hardware pin state, causing wrong voltage programming. Test signals include probe with board data, VSEL pin transition tests, suspend/resume retention checks, and regulator voltage readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/tps62360.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/tps6507x.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/tps6507x.h

Purpose: this minimal header exposes platform data for TI TPS6507x voltage regulator support.

Important APIs/types/functions: it declares `struct tps6507x_reg_platform_data` with one field, `defdcdc_default`, which selects whether the DCDC high or low register controls DCDC2/DCDC3 output voltage by default. No functions are declared.

Control flow: board setup passes the structure into the TPS6507x regulator driver. Probe uses `defdcdc_default` to decide initial voltage-register interpretation before registering DCDC regulators with the regulator core.

State and persistence: no owned runtime state. The field represents initial hardware policy and must match the PMIC strap/register state for persistent operation across boot and suspend.

Dependencies and integration points: integrates with the TPS6507x MFD/regulator driver stack and regulator constraints. It relies on includers for the definition of `bool`.

Risks: the field only applies to DCDC2/DCDC3; applying it elsewhere or setting it contrary to hardware state can produce wrong core voltage. Test signals include probe on TPS6507x platforms, regulator voltage readback, and coverage of both high-register and low-register default modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/tps6507x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/userspace-consumer.h -->
# sources/distributed-fs/ceph-client/include/linux/regulator/userspace-consumer.h

Purpose: this header defines initialization data for the regulator userspace consumer pseudo-device, which exposes a named regulator supply group for user-driven enable/disable control.

Important APIs/types/functions: `struct regulator_userspace_consumer_data` contains `name`, `num_supplies`, a `struct regulator_bulk_data *supplies` array, `init_on`, and `no_autoswitch`. It forward-declares `struct regulator_consumer_supply` but the actual data field uses bulk regulator data. No functions are declared.

Control flow: board/platform data creates a userspace consumer instance with one or more supplies. Probe obtains the bulk regulators, optionally enables them on initialization, and then exposes control through the userspace-consumer driver. `no_autoswitch` prevents automatic toggling in policies that need manual control.

State and persistence: the structure is static initialization policy. Runtime state lives in the driver and regulator core reference counts; hardware enable state may persist depending on PMIC behavior.

Dependencies and integration points: integrates with regulator bulk APIs, platform devices, and sysfs-facing userspace consumer support.

Risks: exposing regulator control to userspace can make power sequencing unsafe if supplies feed critical devices. Mismatched `num_supplies` and array contents can break probe. Test signals include probe with multiple supplies, sysfs enable/disable behavior, boot with `init_on`, and suspend/resume interaction with regulator reference counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/regulator/userspace-consumer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/relay.h -->
# sources/distributed-fs/ceph-client/include/linux/relay.h

Purpose: this header declares the relay channel API, a high-throughput per-CPU buffering interface used to stream kernel data to files, often through relayfs/debugfs.

Important APIs/types/functions: core types are `struct rchan`, `struct rchan_buf`, `struct rchan_callbacks`, and `struct rchan_buf_stats`. APIs include `relay_open()`, `relay_close()`, `relay_flush()`, `relay_stats()`, `relay_subbufs_consumed()`, `relay_reset()`, `relay_buf_full()`, `relay_switch_subbuf()`, `relay_write()`, `__relay_write()`, `relay_reserve()`, `subbuf_start_reserve()`, and exported `relay_file_operations`.

Control flow: clients open a channel with sub-buffer sizing and callbacks. The core creates one per-CPU buffer or one global buffer through `create_buf_file()`. Producers write to the current CPU buffer; if `offset + length` exceeds `subbuf_size`, `relay_switch_subbuf()` finalizes the current sub-buffer and starts another. Consumers read via relay file operations and report consumption with `relay_subbufs_consumed()`. `subbuf_start` may reserve header bytes at each new sub-buffer.

State and persistence: `rchan` owns channel geometry, callbacks, private data, per-CPU buffers, dentry metadata, and reference count. `rchan_buf` tracks buffer pointers, offsets, produced/consumed sub-buffer counters, wait queues, IRQ wakeups, padding, stats, CPU, and finalization state. Data is volatile kernel memory exposed through files while the channel exists.

Dependencies and integration points: depends on scheduler/preemption, timers, wait queues, lists, irq_work, VFS dentries/file operations, krefs, and percpu APIs. It integrates with tracing and custom kernel instrumentation.

Risks: callers must choose `relay_write()` for interrupt-context safety or `__relay_write()` for preemption-only protection; `relay_reserve()` performs no synchronization beyond CPU pinning. Incorrect consumed counts can stall writers or lose data. Test signals include per-CPU write/read tests, buffer-full/stat counter checks, callback sequencing, CPU hotplug via `relay_prepare_cpu`, and teardown while readers hold references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/relay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc.h -->
# sources/distributed-fs/ceph-client/include/linux/remoteproc.h

Purpose: this is the central public header for the Linux remote processor framework. It defines firmware resource-table formats, platform operation hooks, remoteproc lifecycle state, memory carveouts, coredump segments, virtio vring/vdev state, subdevices, and core registration/control APIs.

Important APIs/types/functions: firmware ABI types include `struct resource_table`, `struct fw_rsc_hdr`, `enum fw_resource_type`, `struct fw_rsc_carveout`, `fw_rsc_devmem`, `fw_rsc_trace`, `fw_rsc_vdev_vring`, and `fw_rsc_vdev`. Runtime types include `struct rproc_mem_entry`, `struct rproc_ops`, `enum rproc_state`, `enum rproc_crash_type`, `enum rproc_dump_mechanism`, `struct rproc_dump_segment`, `enum rproc_features`, `struct rproc`, `struct rproc_subdev`, `struct rproc_vring`, and `struct rproc_vdev`. APIs include allocation/registration (`rproc_alloc`, `rproc_add`, devm variants), lifecycle (`rproc_boot`, `rproc_shutdown`, `rproc_detach`, `rproc_set_firmware`), memory helpers, crash/coredump helpers, address translation, and subdevice management.

Control flow: a platform driver allocates an `rproc`, supplies `rproc_ops`, adds it to the core, and optionally auto-boots. Boot parses firmware, validates resource tables, allocates carveouts, maps devmem, creates trace buffers, instantiates static virtio devices, loads firmware, obtains boot address, and calls platform `prepare/start`. Shutdown reverses subdevices, virtio, mappings, carveouts, and platform power. Crash reporting schedules recovery/coredump behavior and may use attach-on-recovery.

State and persistence: `struct rproc` persists device identity, firmware name, platform private data, power refcount, state, locks, debugfs, carveout/mapping/vdev/subdev lists, notify IDR, resource-table copies, coredump segments, ELF info, char device, and feature bitmap. Firmware resource tables are mutable negotiation state because the host may write back allocated addresses and virtio status/features.

Dependencies and integration points: depends on device model, firmware loader, IOMMU, DMA, virtio, platform devices, cdev, completion, IDR, OF phandles, debugfs, and subsystem-specific drivers. Other headers in this group provide vendor-specific helpers for MediaTek SCP, PRUSS, Qualcomm SSR, and ST SLIM remoteprocs.

Risks: firmware resource tables can request unsafe devmem mappings; comments note this trust problem. Boot/shutdown ordering is delicate because subdevices, virtio, mappings, coredumps, and platform callbacks must unwind correctly. Test signals include firmware parse/load tests, carveout address negotiation, virtio rpmsg bring-up, crash recovery/coredump tests, attach/detach flows, reference-counted boot/shutdown, and invalid resource-table fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc/mtk_scp.h -->
# sources/distributed-fs/ceph-client/include/linux/remoteproc/mtk_scp.h

Purpose: this header exposes MediaTek SCP remoteproc helper APIs and inter-processor interrupt IDs for client drivers such as codecs, image processing, and ChromeOS host-command services.

Important APIs/types/functions: it defines `scp_ipi_handler_t`, opaque `struct mtk_scp`, and `enum scp_ipi_id` values from `SCP_IPI_INIT` through media, MDP, DIP/ISP/FD, CROS host, IMGSYS, namespace service, and `SCP_IPI_MAX`. APIs include `scp_get()`, `scp_put()`, `scp_get_device()`, `scp_get_rproc()`, `scp_ipi_register()`, `scp_ipi_unregister()`, `scp_ipi_send()`, capability getters, and `scp_mapping_dm_addr()`.

Control flow: a client obtains an SCP handle from its platform device, registers IPI handlers for message IDs, sends requests with bounded length and optional wait, maps SCP data-memory addresses when needed, and releases the handle on teardown. `SCP_IPI_INIT` is firmware-to-kernel initialization notification; other IDs are request-triggered.

State and persistence: the header owns no state. Runtime state is inside the SCP driver: handle refcounts, IPI handler table, firmware state, capabilities, and shared memory mappings.

Dependencies and integration points: includes `linux/platform_device.h` and integrates with remoteproc, MediaTek multimedia drivers, SCP firmware mailboxes, and platform device lifetime.

Risks: IPI ID collisions, buffer length mismatches, and use-after-put can break cross-processor communication. Test signals include client probe/remove refcounting, handler registration conflict tests, SCP firmware boot/init IPI, send timeout paths, and address translation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc/mtk_scp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc/pruss.h -->
# sources/distributed-fs/ceph-client/include/linux/remoteproc/pruss.h

Purpose: this header exposes TI PRU-ICSS remoteproc consumer helpers for acquiring PRU cores and configuring PRU constant-table entries.

Important APIs/types/functions: it defines `PRU_RPROC_DRVNAME`, `enum pruss_pru_id` (`PRUSS_PRU0`, `PRUSS_PRU1`, `PRUSS_NUM_PRUS`), `enum pru_ctable_idx` (`PRU_C24` through `PRU_C31`), and conditionally available APIs `pru_rproc_get()`, `pru_rproc_put()`, and `pru_rproc_set_ctable()`. `is_pru_rproc()` checks a device's driver string against `PRU_RPROC_DRVNAME`. When `CONFIG_PRU_REMOTEPROC` is disabled, stubs return `-EOPNOTSUPP` or no-op.

Control flow: PRUSS clients request a PRU by device-tree node and index, receive the PRU ID, configure constant table windows if needed, use normal remoteproc operations, and then release with `pru_rproc_put()`.

State and persistence: no state is stored in the header. PRU remoteproc ownership, firmware, and constant-table state live in the PRU remoteproc driver and hardware.

Dependencies and integration points: depends on `linux/device.h`, `linux/types.h`, OF nodes, remoteproc core, and TI PRUSS platform drivers.

Risks: `is_pru_rproc()` relies on driver-string comparison and must stay aligned with the real driver name. Constant table changes are hardware-visible and can break PRU firmware address assumptions. Test signals include disabled-config stub builds, DT PRU acquisition/release, ctable programming readback, and firmware that exercises configured constant entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc/pruss.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc/qcom_rproc.h -->
# sources/distributed-fs/ceph-client/include/linux/remoteproc/qcom_rproc.h

Purpose: this header declares Qualcomm subsystem restart notification types and notifier registration helpers used by clients interested in remoteproc power and crash transitions.

Important APIs/types/functions: `enum qcom_ssr_notify_type` describes before/after powerup and before/after shutdown events. `struct qcom_ssr_notify_data` carries subsystem `name` and whether shutdown is crash-related. APIs are `qcom_register_ssr_notifier()` and `qcom_unregister_ssr_notifier()` when `CONFIG_QCOM_RPROC_COMMON` is enabled; stubs return `NULL`/`0` otherwise.

Control flow: consumers register a notifier for a named remote subsystem. Qualcomm remoteproc common code calls notifiers around prepare/start and stop/unprepare phases, letting clients quiesce or reinitialize resources after SSR events.

State and persistence: notifier blocks and registration handles are runtime state in the Qualcomm common implementation, not in the header. The event payload is transient.

Dependencies and integration points: depends on notifier blocks and integrates with Qualcomm remoteproc drivers, subsystem restart, rpmsg clients, modem/audio/compute subsystems, and crash recovery logic.

Risks: clients must unregister before teardown and must tolerate disabled stubs. Event ordering matters: doing work in `BEFORE_SHUTDOWN` versus `AFTER_SHUTDOWN` can affect access to shared memory and clocks. Test signals include notifier registration/unregistration, crash versus orderly stop events, disabled-config builds, and client recovery after SSR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc/qcom_rproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc/st_slim_rproc.h -->
# sources/distributed-fs/ceph-client/include/linux/remoteproc/st_slim_rproc.h

Purpose: this header describes STMicroelectronics SLIM remote processor allocation support and its memory/register layout.

Important APIs/types/functions: constants `ST_SLIM_MEM_MAX` and `ST_SLIM_MAX_CLK` bound memory and clock arrays. Anonymous enum values identify `ST_SLIM_DMEM` and `ST_SLIM_IMEM`. `struct st_slim_mem` stores CPU virtual I/O address, bus address, and size. `struct st_slim_rproc` stores the `rproc` handle, DMEM/IMEM descriptors, `slimcore` and `peri` register mappings, and private clock pointers. APIs are `st_slim_rproc_alloc()` and `st_slim_rproc_put()`.

Control flow: platform code calls `st_slim_rproc_alloc()` with a device and firmware name, receiving a populated wrapper around remoteproc plus mapped memory/register resources and clocks. It later releases the object with `st_slim_rproc_put()`.

State and persistence: the wrapper persists remoteproc pointer, memory mappings, register bases, and clock handles for the SLIM device lifetime. Firmware and hardware memory contents are external state.

Dependencies and integration points: integrates with remoteproc core, platform devices, clock framework, MMIO mapping, and ST SLIM firmware loading.

Risks: array bounds are fixed at two memories and four clocks; new hardware with more resources would need header changes. Incorrect bus/CPU address pairing can corrupt firmware load or data access. Test signals include allocation failure unwinding, firmware load to IMEM/DMEM, clock enable/disable sequencing, and remoteproc boot/stop on ST platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/remoteproc/st_slim_rproc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resctrl.h -->
# sources/distributed-fs/ceph-client/include/linux/resctrl.h

Purpose: this header is the architecture/core contract for Linux resource control. It models cache allocation, memory bandwidth allocation, monitoring domains, CLOSID/RMID identifiers, pseudo-locking, MBM counter assignment, and architecture hooks used by the resctrl filesystem.

Important APIs/types/functions: key types include `enum resctrl_res_level`, `enum resctrl_conf_type`, `struct pseudo_lock_region`, `struct resctrl_staged_config`, `enum resctrl_domain_type`, `struct rdt_domain_hdr`, `struct rdt_ctrl_domain`, `struct mbm_cntr_cfg`, `struct rdt_l3_mon_domain`, `struct resctrl_cache`, `enum membw_throttle_mode`, `struct resctrl_membw`, `enum resctrl_scope`, `enum resctrl_schema_fmt`, `struct resctrl_mon`, `struct rdt_resource`, `struct resctrl_schema`, `struct resctrl_cpu_defaults`, and `struct resctrl_mon_config_info`. Important helpers include resource iteration macros, `domain_header_is_valid()`, `resctrl_get_default_ctrl()`, `resctrl_get_config_index()`, MBM iteration macros, and many `resctrl_arch_*` hooks.

Control flow: architecture code exposes resources through `resctrl_arch_get_resource()`. Mount/init paths call `resctrl_init()` and `resctrl_arch_pre_mount()`. User schemata changes stage values in `rdt_ctrl_domain`, then update domains and hardware via `resctrl_arch_update_domains()` and `resctrl_arch_update_one()`. CPU/group reassignment calls `resctrl_arch_sync_cpu_closid_rmid()`. Monitoring enables events, reads RMID/counter values on appropriate CPUs, handles overflow/limbo workers, and resets state when RMIDs are reused.

State and persistence: resources persist as `rdt_resource` instances with control and monitor domain lists, capability flags, cache/membw/monitor parameters, and schema metadata. Domains carry CPU masks, staged config, MBA software-controller values, MBM state arrays, delayed works, RMID busy maps, and assignable counter configuration. Hardware MSR/MPAM/QoS state is external but synchronized through hooks.

Dependencies and integration points: depends on cacheinfo, pid namespaces, lists, cpumasks, delayed work, resctrl event IDs, optional arch-specific `asm/resctrl.h`, procfs display, debugfs/pseudo-lock support, and the resctrl filesystem.

Risks: many hooks have strict CPU/context requirements; `resctrl_arch_rmid_read()` may sleep unless called with interrupts masked and may fail under NOHZ_FULL/IPI paths. CLOSID/RMID reuse, CDP index remapping, and MBM counter assignment are high-risk for accounting corruption. Test signals include resctrl selftests, schemata parsing and hardware readback, CPU hotplug domain updates, MBM overflow/limbo behavior, RMID reuse, CDP enable/disable, pseudo-lock measurement tests, and lockdep/debug atomic-sleep checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resctrl_types.h -->
# sources/distributed-fs/ceph-client/include/linux/resctrl_types.h

Purpose: this header holds small shared resctrl constants and event IDs that are needed outside the larger internal/core resctrl header.

Important APIs/types/functions: constants include `MAX_MBA_BW`, `MBM_OVERFLOW_INTERVAL`, configurable MBM transaction bits (`READS_TO_LOCAL_MEM`, `READS_TO_REMOTE_MEM`, non-temporal writes, slow-memory reads, dirty victims), `MAX_EVT_CONFIG_BITS`, and `NUM_MBM_TRANSACTIONS`. `enum resctrl_event_id` defines QoS events for L3 occupancy, total/local MBM bandwidth, and Intel telemetry events. Macros include `QOS_NUM_L3_MBM_EVENTS` and `MBM_STATE_IDX(evt)`.

Control flow: resctrl monitor and architecture code uses event IDs to enable, configure, read, and index monitoring counters. MBM bitmasks constrain user-visible event configuration and architecture programming.

State and persistence: no state is owned here. The constants define indexes into persistent state arrays such as MBM state tables and architecture counter assignment records.

Dependencies and integration points: used by `resctrl.h`, x86 RDT, Arm MPAM-style support, resctrl FS monitor code, and telemetry support.

Risks: enum values for `QOS_L3_*` must match hardware programming values on RDT systems. Adding events changes `QOS_NUM_EVENTS` and may affect array sizing. Test signals include build coverage across architectures, MBM event configuration tests, event-to-index tests for `MBM_STATE_IDX()`, and counter reads for all enabled events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resctrl_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset-controller.h -->
# sources/distributed-fs/ceph-client/include/linux/reset-controller.h

Purpose: this header declares the provider-side reset controller interface used by drivers that expose reset lines to other devices.

Important APIs/types/functions: `struct reset_control_ops` provides `reset`, `assert`, `deassert`, and `status` callbacks. `struct reset_controller_dev` stores ops, owner module, global/list state, requested reset-control list head, device and firmware nodes, OF/fwnode specifier cell counts, translation callbacks, reset count, and a mutex. Registration APIs are `reset_controller_register()`, `reset_controller_unregister()`, and `devm_reset_controller_register()`, with no-op stubs when reset controller support is disabled.

Control flow: a provider fills `reset_controller_dev`, including translation from firmware reset specifiers to numeric line IDs, then registers it. Consumers in `reset.h` acquire `struct reset_control` handles that call back into these ops. Unregistration removes the provider from the reset core and prevents new acquisitions.

State and persistence: provider state persists in `reset_controller_dev`, including a mutex-protected list of requested controls. Hardware reset-line state is external and represented through callbacks.

Dependencies and integration points: depends on lists, mutexes, modules, device tree, fwnode references, and the reset consumer API.

Risks: bad translation callbacks can route consumers to the wrong reset line. Providers must handle shared consumers and concurrent operations through reset core locking and their own hardware locking. Test signals include provider registration/unregistration, DT/fwnode translation, consumer get/assert/deassert/status paths, disabled-config builds, and devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset-controller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset.h -->
# sources/distributed-fs/ceph-client/include/linux/reset.h

Purpose: this header is the consumer-side reset-control API. It defines reset acquisition modes, optional/shared/exclusive semantics, bulk operations, managed variants, OF/fwnode helpers, and compatibility wrappers.

Important APIs/types/functions: `struct reset_control_bulk_data` stores reset IDs and handles. `enum reset_control_flags` combines shared, optional, acquired, and deasserted modes into exclusive/shared/optional/released/deasserted variants. Core APIs include reset/assert/deassert/status, acquire/release, bulk operations, `__reset_control_get()`, `__fwnode_reset_control_get()`, `reset_control_put()`, bulk get/put, `__device_reset()`, devm get/bulk get, array gets, and `reset_control_get_count()`. Many inline wrappers expose named, indexed, OF, optional, shared, exclusive, deasserted, released, devm, and array-specific forms.

Control flow: consumers acquire a reset handle, optionally acquire a temporarily released exclusive reset, assert/deassert/reset it, then release/put it. Shared resets maintain deassert counts: assert is only effective after matching deasserts, and `reset_control_reset()` is not valid on shared handles. Deasserted managed getters combine acquisition and initial deassert, with cleanup reasserting on detach.

State and persistence: the opaque `struct reset_control` state lives in reset core. This header encodes flag state passed into core acquisition and stub behavior when `CONFIG_RESET_CONTROLLER` is off. Hardware reset line state persists externally.

Dependencies and integration points: depends on bits, errors, errno, OF/fwnode, device model, reset-controller providers, and driver probe/remove sequencing.

Risks: optional APIs return `NULL` for absent resets while non-optional APIs return `ERR_PTR`; mixing those conventions is a common bug. Shared reset usage forbids assert-before-deassert and direct reset pulses. Temporarily exclusive released handles must be acquired before use. Test signals include compile tests with reset support disabled, probe paths for optional and required resets, shared deassert-count tests, devm cleanup reassertion, bulk ordering, and OF indexed lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset/bcm63xx_pmb.h -->
# sources/distributed-fs/ceph-client/include/linux/reset/bcm63xx_pmb.h

Purpose: this header provides inline Broadcom BCM63xx Processor Monitor Bus helpers shared by SMP and reset code.

Important APIs/types/functions: register offsets and bits cover `PMB_CTRL`, start/timeout/slave-error/busy/read/write fields, write/read data registers, timeout register, and bus ID shift. Inline APIs are `__bpcm_do_op()`, `bpcm_rd()`, and `bpcm_wr()`.

Control flow: `bpcm_wr()` writes data to `PMB_WR_DATA`, then calls `__bpcm_do_op()` with write opcode. `bpcm_rd()` issues a read operation and then reads `PMB_RD_DATA`. `__bpcm_do_op()` builds a command with start bit, address, offset shifted by word, and operation type, writes it to the master control register, then polls for completion up to 1000 microsecond delays, returning `0`, `-EIO`, or `-ETIMEDOUT`.

State and persistence: no kernel state is stored. The PMB master registers and target BPCM registers hold hardware state.

Dependencies and integration points: uses MMIO `readl`/`writel`, microsecond delay, error codes, and reset/SMP Broadcom platform code.

Risks: offset is divided by four, so callers must pass byte offsets. `bpcm_rd()` reads data even if `__bpcm_do_op()` failed, so callers must check return before trusting `*val`. Polling delays can be problematic in atomic or timing-sensitive contexts. Test signals include successful read/write of known BPCM registers, timeout/error paths, and reset-controller behavior on BCM63xx hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset/bcm63xx_pmb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset/reset-simple.h -->
# sources/distributed-fs/ceph-client/include/linux/reset/reset-simple.h

Purpose: this header defines shared data for simple memory-mapped reset controllers using bit operations over reset registers.

Important APIs/types/functions: `struct reset_simple_data` contains a spinlock, MMIO base, embedded `reset_controller_dev`, polarity flags `active_low` and `status_active_low`, and `reset_us` minimum assert-to-deassert delay. It declares `extern const struct reset_control_ops reset_simple_ops`.

Control flow: simple reset-controller drivers embed/populate `reset_simple_data`, register `rcdev`, and use `reset_simple_ops` for assert, deassert, status, and pulse reset behavior. The spinlock protects read-modify-write register updates.

State and persistence: driver state persists in the data structure. Hardware state is represented by bits in reset controller registers. `reset_us` controls whether the generic reset pulse operation is supported and how long it waits.

Dependencies and integration points: includes MMIO, reset-controller provider API, and spinlocks. It is shared by reset controller drivers with simple active-high or active-low bit layouts.

Risks: polarity flags must match hardware electrical/logical semantics; the comment notes they describe register assertion behavior, not physical voltage level. `reset_us == 0` means reset pulse is unsupported. Test signals include assert/deassert/status readback, active-low/status-active-low variants, reset pulse delay tests, and concurrent reset line updates under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset/reset-simple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset/socfpga.h -->
# sources/distributed-fs/ceph-client/include/linux/reset/socfpga.h

Purpose: this tiny header declares the early initialization hook for Altera/Intel SoCFPGA reset support.

Important APIs/types/functions: it declares `void __init socfpga_reset_init(void);` and no other symbols.

Control flow: architecture/platform initialization calls `socfpga_reset_init()` during early boot to set up SoCFPGA reset controller integration.

State and persistence: no state is defined in the header. The implementation initializes platform reset-controller state and hardware mappings.

Dependencies and integration points: integrates with SoCFPGA platform init code and the Linux reset controller framework. It relies on the `__init` annotation being visible to includers.

Risks: calling order matters because reset controllers may be needed by later device probes. Test signals include SoCFPGA boot logs, reset provider registration, and successful consumer reset lookup during device probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset/socfpga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset/sunxi.h -->
# sources/distributed-fs/ceph-client/include/linux/reset/sunxi.h

Purpose: this header declares the early initialization hook for Allwinner sun6i reset support.

Important APIs/types/functions: it declares `void __init sun6i_reset_init(void);` and no other API.

Control flow: Allwinner platform initialization calls `sun6i_reset_init()` during early boot so reset providers are available before dependent devices probe.

State and persistence: no state is declared here. The implementation owns MMIO mappings and registered reset-controller state.

Dependencies and integration points: integrates with sunxi platform init and reset-controller provider/consumer flows.

Risks: because this is an early init hook, incorrect placement can leave consumers without reset providers. Test signals include sunxi boot, provider registration, DT reset lookup by consumers, and reset pulse behavior on affected SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/reset/sunxi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resource.h -->
# sources/distributed-fs/ceph-client/include/linux/resource.h

Purpose: this header bridges kernel-internal resource-limit/rusage support to the UAPI resource definitions.

Important APIs/types/functions: it includes `uapi/linux/resource.h`, forward-declares `struct task_struct`, and declares `getrusage(struct task_struct *p, int who, struct rusage *ru)`.

Control flow: syscall or proc code calls `getrusage()` for a task and selector such as self/children/thread, filling a UAPI `struct rusage`. Implementation lives elsewhere.

State and persistence: no state is owned by the header. The reported data comes from task accounting fields and process/thread-group state.

Dependencies and integration points: integrates with task accounting, UAPI resource constants, wait/exit accounting, and syscall implementations for `getrusage`.

Risks: this header is small, but ABI coupling to `struct rusage` is strict. Test signals include `getrusage(2)` syscall tests for self/children/thread, compatibility ABI checks, and accounting correctness under CPU time and fault-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resource_ext.h -->
# sources/distributed-fs/ceph-client/include/linux/resource_ext.h

Purpose: this header provides common resource-window and resource-list helpers used by ACPI, PNP, PCI host bridge, and related bus enumeration code.

Important APIs/types/functions: `struct resource_win` stores a CPU-address-space `struct resource` plus bridge translation offset. `struct resource_entry` stores a list node, resource pointer, translation offset, and embedded default resource storage. APIs include `resource_list_create_entry()`, `resource_list_free()`, list add/add_tail/del/free/destroy helpers, iteration macros, and `resource_list_first_type()`.

Control flow: enumeration code creates entries for discovered I/O or memory windows, appends them to a list, searches by `resource_type()`, consumes them to configure bridges/devices, and frees/destroys the list on teardown.

State and persistence: list entries persist during bus/resource discovery. `res` may point at embedded `__res` or externally owned resources, so ownership must be clear.

Dependencies and integration points: depends on lists, I/O port resources, slab allocation, and resource type helpers. Integrates with ACPI resource parsing, PNP resource lists, PCI host bridge windows, and address translation logic.

Risks: confusing ownership of `res` versus `__res` can leak or free the wrong object. Translation `offset` must be consistently applied between bus and CPU address spaces. Test signals include ACPI/PCI host bridge enumeration, resource window translation, list free under failure unwinding, and type-filtered lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resource_ext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/restart_block.h -->
# sources/distributed-fs/ceph-client/include/linux/restart_block.h

Purpose: this header defines common state used to restart interrupted system calls after signal handling.

Important APIs/types/functions: `enum timespec_type` differentiates native and compat remaining-time pointers. `struct restart_block` stores architecture data, a restart function pointer, and a union for futex wait, nanosleep, and poll restart parameters. It declares `do_no_restart_syscall()`.

Control flow: when an interruptible syscall needs restart, kernel code fills the current task's restart block with operation-specific fields and a function. After signal handling, restart logic invokes `fn(restart_block *)`, which resumes or completes the syscall with saved parameters such as futex addresses, timeout expiry, nanosleep remaining-time pointer, or poll fd list/end time.

State and persistence: restart data persists in the task across return-to-user/signal boundaries. It contains user pointers and absolute expiry times, so it must remain valid only under syscall restart rules.

Dependencies and integration points: depends on compiler/user annotations, time64 types, futex, nanosleep, poll, signal return paths, and architecture syscall restart code.

Risks: stale user pointers, wrong compat/native timespec handling, and timeout recomputation errors can break ABI-visible syscall behavior. Test signals include interrupted `nanosleep`, `poll`, and futex waits under signals, compat 32-bit tests, and restart/no-restart syscall paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/restart_block.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resume_user_mode.h -->
# sources/distributed-fs/ceph-client/include/linux/resume_user_mode.h

Purpose: this header defines generic work that must run just before a task resumes user mode after `TIF_NOTIFY_RESUME`.

Important APIs/types/functions: `set_notify_resume(struct task_struct *task)` sets `TIF_NOTIFY_RESUME` and kicks the process if the flag was newly set. `resume_user_mode_work(struct pt_regs *regs)` clears the flag, runs pending task work, drops cached requested keys, handles memcg over-high throttling, maybe throttles blkcg, and handles rseq slow paths.

Control flow: kernel code calls `set_notify_resume()` when a task needs return-to-user work. Architecture exit-to-user code sees `TIF_NOTIFY_RESUME`, clears it before invoking `resume_user_mode_work()`, and may repeat if another asynchronous setter races. A memory barrier pairs with `task_work_add()` list insertion before checking `task_work_pending(current)`.

State and persistence: persistent state is the thread flag and queued task work on `task_struct`; cached key, memcg, blkcg, and rseq state are updated for the current task. The function itself stores no state.

Dependencies and integration points: depends on scheduler/thread flags, task_work, key request cache, memcg, blk-cgroup, restartable sequences, and architecture return-to-user paths.

Risks: missing the memory barrier or clearing the flag incorrectly can lose task_work execution. This code runs without locks, so called helpers must handle their own synchronization and may affect latency on return to user. Test signals include task_work execution before user return, rseq abort/signal tests, memcg over-high throttling, cached key cleanup, and architecture exit-path tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/resume_user_mode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rethook.h -->
# sources/distributed-fs/ceph-client/include/linux/rethook.h

Purpose: this header declares the generic return-hook framework, which uses a per-task list-based shadow stack to intercept function returns for tracing/probing infrastructure.

Important APIs/types/functions: `rethook_handler_t` is the callback type. `struct rethook` stores user data, RCU-protected handler pointer, object pool, and RCU head. `struct rethook_node` stores RCU/list linkage, owning rethook, real return address, and frame pointer. APIs include `rethook_alloc()`, `rethook_stop()`, `rethook_free()`, `rethook_try_get()`, `rethook_recycle()`, `rethook_hook()`, `rethook_find_ret_addr()`, architecture hooks `arch_rethook_prepare()`, `arch_rethook_trampoline()`, `arch_rethook_fixup_return()`, generic `rethook_trampoline_handler()`, `is_rethook_trampoline()`, and `rethook_flush_task()`.

Control flow: clients allocate a rethook pool, obtain nodes, install a hook by replacing a return address via architecture preparation, and the trampoline calls the generic handler on function return. Nodes are recycled to the pool. Stop/free uses RCU/object-pool lifetime rules; task exit flushes pending nodes when enabled.

State and persistence: rethook state persists across active hooked calls; nodes are shadow-stack entries linked from task state and hold original return address/frame. Handler pointer is RCU-protected for safe stop/free.

Dependencies and integration points: depends on objpool, kallsyms symbol descriptors, lockless lists, RCU, `pt_regs`, and architecture-specific trampoline/return-address manipulation. It integrates with kretprobes/fprobe-style return instrumentation.

Risks: architecture implementations must preserve calling convention and frame/return-address correctness. Pool exhaustion can drop hooks. Incorrect RCU/free sequencing can call stale handlers. Test signals include kretprobe/fprobe return-hook tests, nested returns, task exit flush, trampoline address detection, pool exhaustion, and architecture unwinder correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rethook.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rfkill.h -->
# sources/distributed-fs/ceph-client/include/linux/rfkill.h

Purpose: this header declares the in-kernel rfkill API used by radio/transmitter drivers to expose and control software and hardware block state.

Important APIs/types/functions: it remaps UAPI rfkill states to kernel-only `enum rfkill_user_states` and undefines direct UAPI state names to prevent kernel misuse. `struct rfkill_ops` provides `poll`, `query`, and mandatory `set_block` callbacks. APIs include `rfkill_alloc()`, `rfkill_register()`, polling pause/resume, unregister/destroy, hardware/software state setters, persistent software-state initialization, combined state setting, block-state queries, `rfkill_find_type()`, and optional LED trigger helpers.

Control flow: a driver allocates an rfkill object, initializes software/hardware state if needed, registers after it can service callbacks, then the core invokes `set_block()` for user or policy changes. Hardware events call `rfkill_set_hw_state()` or `_reason()`, soft-state events call `rfkill_set_sw_state()`, and polling/query callbacks synchronize state. Unregister waits until callbacks are no longer in flight, after which destroy releases the object.

State and persistence: the opaque rfkill object stores block state, persistent flag, polling, callbacks, userspace device state, and optional LED trigger. Persistent devices may preserve software block state across power transitions.

Dependencies and integration points: depends on UAPI rfkill definitions, device model, LEDs, mutex/list infrastructure, and network/wireless/Bluetooth/platform radio drivers.

Risks: drivers must ignore unblock requests when hard-blocked, handle callback reentry from state setters, and distinguish hard from soft state. Disabled-config stubs return `ERR_PTR(-ENODEV)` from alloc but register treats that sentinel as success. Test signals include soft/hard block transitions, rfkill userspace events, polling pause/resume, suspend/resume state retention, LED trigger behavior, and builds with rfkill disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rfkill.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rhashtable-types.h -->
# sources/distributed-fs/ceph-client/include/linux/rhashtable-types.h

Purpose: this header provides the foundational type definitions for Linux's resizable concurrent hash table without pulling in the full inline implementation.

Important APIs/types/functions: it defines `struct rhash_head`, `struct rhlist_head`, `struct rhashtable_compare_arg`, callback typedefs `rht_hashfn_t`, `rht_obj_hashfn_t`, and `rht_obj_cmpfn_t`, construction parameters `struct rhashtable_params`, table handles `struct rhashtable` and `struct rhltable`, walker state `struct rhashtable_walker`, iterator state `struct rhashtable_iter`, and init APIs `rhashtable_init()`/`rhltable_init()` wrapping `_noprof` with allocation profiling hooks.

Control flow: users embed `rhash_head` or `rhlist_head` in objects, fill params describing key/head offsets and hash/compare functions, initialize a table, then use full `rhashtable.h` helpers for lookup/mutation/walk. `rhltable` supports duplicate-key lists.

State and persistence: `struct rhashtable` persists current bucket table pointer, key length, maximum elements, params, duplicate-list mode, deferred resize work, IRQ work, mutex, walker lock, element count, and optional allocation tag. Iterators persist traversal position and walker registration.

Dependencies and integration points: depends on atomics, workqueue/irq-work types, mutexes, allocation profiling, and the full rhashtable implementation. It is included by structures that need to embed hash heads without all helpers.

Risks: offsets and key lengths must match object layout exactly. Iterator state has RCU/walker lifetime constraints enforced by full APIs. Test signals include init parameter validation, duplicate-key rhltable behavior, allocation profiling builds, and compile coverage for headers embedding `rhash_head`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rhashtable-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rhashtable.h -->
# sources/distributed-fs/ceph-client/include/linux/rhashtable.h

Purpose: this header provides the main inline implementation and API for Linux's resizable, scalable, RCU-friendly concurrent hash table and duplicate-key hash-list table.

Important APIs/types/functions: key internals include `struct bucket_table`, nulls markers, hash helpers (`rht_key_get_hash`, `rht_key_hashfn`, `rht_head_hashfn`), growth/shrink predicates, bucket lock helpers, traversal macros, lookup helpers, insertion helpers, removal/replacement helpers, walkers, and destroy APIs. Public operations include `rhashtable_lookup()`, `rhashtable_lookup_fast()`, `rhashtable_insert_fast()`, lookup-and-insert variants, `rhashtable_remove_fast()`, `rhashtable_replace_fast()`, `rhltable_lookup/insert/remove`, walker enter/start/next/stop/exit, and free/destroy.

Control flow: lookups RCU-dereference the current bucket table, compute a bucket, walk nulls-terminated chains, and restart on `future_tbl` during resize. Inserts take a per-bucket bit spinlock, check duplicate keys unless plain insert without key, insert at head, increment element count, and queue deferred resize if load exceeds thresholds; high chain elasticity or active resize falls back to slow path. Removal locks the old and possibly future table buckets until the object is found, unlinks it, decrements count, and schedules shrink if allowed. Replacement verifies old/new hash equality before swapping under bucket lock.

State and persistence: bucket tables persist size, hash seed, walker list, future table pointer, lockdep map, and bucket pointers whose low bit is used as lock state. Table state persists through `struct rhashtable` from `rhashtable-types.h`, including deferred work and atomic element count. Object lifetime remains caller-owned and RCU-sensitive.

Dependencies and integration points: depends on RCU, workqueues, irq_work, jhash, list_nulls, bit spinlocks, lockdep, and allocation hooks. It is widely used by networking, filesystems, and kernel lookup caches requiring concurrent resize.

Risks: callers must honor RCU/object lifetime rules, supply correct params, and avoid using fast lookup when objects can disappear after RCU unlock. Elasticity protects against hash-flood attacks unless disabled. The bucket pointer lock-bit trick is subtle and relies on pointer alignment. Test signals include rhashtable selftests, concurrent insert/remove/lookup under KCSAN/lockdep, resize growth/shrink, duplicate-key rhltable tests, hash collision/elasticity tests, and RCU stall/leak detection during destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rhashtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ring_buffer.h -->
# sources/distributed-fs/ceph-client/include/linux/ring_buffer.h

Purpose: this header declares the generic tracing ring buffer API used by ftrace and related tracing code for per-CPU event storage, reading, polling, mmap, and remote-buffer support.

Important APIs/types/functions: `struct ring_buffer_event` encodes `type_len` and 27-bit time delta. `enum ring_buffer_type` defines padding, time-extend, absolute timestamp, and data event encodings. APIs cover event length/data/timestamp, discard/commit, allocation and range/remote allocation, wait/poll/wakeup, resize, overwrite mode, reserve/commit/write, nesting guards, peek/consume, iterator reads, size/statistics, reset, optional CPU swap, record enable/disable, timestamp clock control, dirty page counts, read-page operations, print helpers, sub-buffer order/size, mmap/unmap, descriptor walking, and remote callbacks.

Control flow: writers reserve an event, fill its payload, and commit, or use `ring_buffer_write()`. Readers peek/consume directly, use iterators, read pages, poll for availability, or mmap buffers. Timestamp records encode short deltas inline and use extension records when needed. Recording can be disabled globally or per CPU; overwrite mode changes producer behavior when buffers fill.

State and persistence: opaque `trace_buffer` owns per-CPU buffers, timestamps, counters, clock callback, overwrite/recording flags, page lists, mmap state, and reader pages. Event headers persist in buffer pages until consumed or overwritten.

Dependencies and integration points: depends on MM, seq_file, poll, trace mmap UAPI, lock class keys, guard macros, tracing `trace_seq`, and CPU hotplug preparation through `trace_rb_cpu_prepare`.

Risks: commit/discard ordering is strict; discarded events must not be committed. Timestamp encoding depends on 27-bit deltas and architecture alignment. mmap descriptor sizing must match page counts. Test signals include tracing ring-buffer selftests, concurrent producer/consumer stress, timestamp normalization, overwrite/non-overwrite behavior, mmap readers, CPU hotplug, nested write guard usage, and remote buffer callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ring_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ring_buffer_types.h -->
# sources/distributed-fs/ceph-client/include/linux/ring_buffer_types.h

Purpose: this companion header defines low-level ring-buffer layout constants shared by tracing ring-buffer internals and headers that need page/event sizing.

Important APIs/types/functions: timestamp constants are `TS_SHIFT`, `TS_MASK`, and `TS_DELTA_TEST`; `test_time_stamp()` checks whether a delta exceeds inline capacity. Layout macros include `BUF_PAGE_HDR_SIZE`, `RB_EVNT_HDR_SIZE`, `RB_ALIGNMENT`, `RB_MAX_SMALL_DATA`, `RB_EVNT_MIN_SIZE`, alignment choices, and `RB_ALIGN_DATA`. `struct buffer_data_page` contains a page timestamp, local commit index, and aligned flexible data area.

Control flow: ring-buffer code uses `test_time_stamp()` to decide whether to emit time-extension records. Page and event header size macros drive allocation, event packing, and read-page formatting.

State and persistence: `buffer_data_page` is the persistent in-memory format for ring-buffer pages: page timestamp, commit offset, and event data. The header itself stores no global state.

Dependencies and integration points: depends on `asm/local.h`, `offsetof`, ring-buffer event type length constants from `ring_buffer.h`, and architecture 64-bit alignment capability.

Risks: layout macros are ABI-like for tracing buffer interpretation; alignment changes can break readers or corrupt event parsing. `test_time_stamp()` must agree with event timestamp encoding. Test signals include ring-buffer page format tests, 32-bit and 64-bit alignment builds, timestamp extension boundary tests, and mmap/read-page compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ring_buffer_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rio.h -->
# sources/distributed-fs/ceph-client/include/linux/rio.h

Purpose: this is the core RapidIO interconnect service header. It defines device, master port, network, switch, mailbox, doorbell, DMA, scan, and driver model structures plus low-level operation callbacks.

Important APIs/types/functions: major types are `struct rio_switch`, `struct rio_switch_ops`, `enum rio_device_state`, `struct rio_dev`, `struct rio_msg`, `struct rio_dbell`, `struct rio_mport`, `struct rio_net`, link speed/width enums, `enum rio_mport_flags`, `struct rio_mport_attr`, `struct rio_ops`, `struct rio_driver`, `union rio_pw_msg`, optional DMA transfer types, `struct rio_scan`, and `struct rio_scan_node`. APIs include mport initialization/registration, mailbox open/close, and mport query helpers.

Control flow: mport drivers provide `rio_ops` for local and remote config-space access, doorbells, mailboxes, inbound/outbound mappings, and capability query. Enumeration/discovery populates `rio_net`, `rio_dev`, and switch route state. Device drivers bind through `rio_driver` and operate on resources, messages, doorbells, and mappings. Optional DMA support embeds a DMA device in the mport and describes RapidIO-specific transfer addressing.

State and persistence: `rio_dev` persists identity, capabilities, resources, destination/hop routing, state, and optional switch data. `rio_mport` persists resource ranges, mailbox callbacks, ops, IDs, sys size, physical feature pointers, device object, scan ops, state, and port-write reference count. `rio_net` persists fabric membership lists and primary port.

Dependencies and integration points: depends on device model, resources, `rio_regs.h`, mod_devicetable, optional DMA engine, and RapidIO fabric enumeration.

Risks: hardware callback contracts are broad and must handle config-space size, route tables, mailbox lifetimes, and error management. Atomic state gates running/gone/shutdown behavior. Test signals include mport registration, fabric enumeration/discovery, config reads/writes, mailbox and doorbell loopback, route programming, DMA transfers, port-write error handling, and driver bind/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rio_drv.h -->
# sources/distributed-fs/ceph-client/include/linux/rio_drv.h

Purpose: this header exposes RapidIO driver-service helpers for config-space access, doorbells, mailbox management, resource claiming, memory mapping, port-write handlers, driver registration, DMA, and driver data access.

Important APIs/types/functions: inline local config helpers wrap `__rio_local_read/write_config_{8,16,32}`. Device config helpers call `rio_mport_read/write_config_*` through `rdev->net->hport`, `destid`, and `hopcount`. Other helpers include `rio_send_doorbell()`, `rio_init_mbox_res()`, `rio_init_dbell_res()`, `RIO_DEVICE()`, message enqueue/dequeue helpers, resource request/release, inbound/outbound mapping, port-write registration, driver register/unregister, device get/put, optional DMA APIs, `rio_name()`, `rio_get_drvdata()`, `rio_set_drvdata()`, local device ID accessors, and `rio_init_mports()`.

Control flow: RapidIO drivers use inline helpers for config I/O and service requests. Resource helpers reserve mailbox/doorbell/memory ranges before use. Mailbox helpers request queues, enqueue outbound buffers or add inbound buffers, and retrieve completions through callbacks. Mapping helpers map RapidIO address windows. Driver registration connects `rio_driver` probe/remove with the bus.

State and persistence: the header manipulates state owned by `rio_dev`, `rio_mport`, resources, mailbox descriptors, and device-model driver data. It does not own independent state.

Dependencies and integration points: includes `rio.h`, resources, string helpers, and optional DMA engine. It is the main convenience API for RapidIO client drivers.

Risks: inline config helpers assume `rdev->net->hport` is valid and running. Resource initialization zeroes structures and sets flags; callers must still request/claim before use. Test signals include config access of all widths, mailbox/doorbell request-release cycles, memory map/unmap, driver bind/unbind, DMA prep, and missing/failed mport ops paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rio_drv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rio_ids.h -->
# sources/distributed-fs/ceph-client/include/linux/rio_ids.h

Purpose: this header provides RapidIO vendor and device ID constants, currently for IDT RapidIO switches/devices.

Important APIs/types/functions: constants include `RIO_VID_IDT` and `RIO_DID_IDT70K200`, `RIO_DID_IDTCPS8/12/16/6Q/10Q/1848/1432/1616`, `RIO_DID_IDTVPS1616`, `RIO_DID_IDTSPS1616`, and `RIO_DID_IDTRXS1632/2448`. There are no functions or structs.

Control flow: RapidIO drivers and ID tables use these constants with `RIO_DEVICE()` or `struct rio_device_id` matching to bind supported hardware.

State and persistence: no state. The constants are stable hardware identifiers.

Dependencies and integration points: integrates with RapidIO driver ID tables, module autoloading, and device enumeration that reads RapidIO identity CARs.

Risks: wrong IDs prevent driver binding or bind a driver to unsupported silicon. Test signals include modalias/module autoload matching, enumeration of IDT devices, and driver ID table coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rio_ids.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rio_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/rio_regs.h

Purpose: this header defines RapidIO configuration-space, extended feature, LP-Serial, error management, and switch routing table register offsets and bit masks.

Important APIs/types/functions: it defines the 16 MiB maintenance space size, standard CAR/CSR offsets for identity, assembly, processing element features, switch port info, source/destination ops, route limit, mailboxes, doorbells/write-port, logical-layer control, base address, device ID, host lock, component tag, and standard route config. Helper macros parse extended feature block headers and calculate per-port register offsets from port number and register map type. It also defines error management registers and switch routing table register fields.

Control flow: RapidIO enumeration and drivers read identity/capability registers, walk the extended feature list using `RIO_GET_BLOCK_PTR()`/`RIO_GET_BLOCK_ID()`, configure ports through LP-Serial registers, detect link/error state, enable error notifications, and program switch route tables.

State and persistence: no kernel state is stored. The constants describe persistent hardware register state in RapidIO devices and switches.

Dependencies and integration points: included by `rio.h` and RapidIO core/driver implementations. It integrates with maintenance transaction accessors from `rio_drv.h` and hardware-specific mport ops.

Risks: register offsets are specification ABI; mistakes can corrupt routing, error handling, or device enumeration. Some definitions are version-specific and register-map-type dependent. Test signals include config-space decode tests, EFB walking on devices with multiple blocks, port status/error management handling, switch route programming, and cross-checking route table size for 8-bit versus 16-bit dest IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/rio_regs.h -->
