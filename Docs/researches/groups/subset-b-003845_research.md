# subset-b-003845 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-etr.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-etr.c

## Purpose

`coresight-tmc-etr.c` implements the Embedded Trace Router sink side of the Arm CoreSight TMC driver. It allocates trace buffers, programs ETR hardware for circular capture, exposes sysfs and perf sink operations, supports flat, TMC scatter-gather, CATU, and reserved-memory buffer modes, and persists crash trace metadata when reserved crash buffers are configured.

## Important APIs, Types, and Functions

Important internal types are `etr_flat_buf`, `etr_sg_table`, `etr_perf_buffer`, and `etr_buf_hw`. Exported helpers include `tmc_alloc_sg_table`, `tmc_free_sg_table`, `tmc_sg_table_sync_*`, `tmc_sg_table_get_data`, `tmc_etr_get_catu_device`, CATU ops setters, and `tmc_etr_get_buffer`. The central buffer path is `tmc_alloc_etr_buf`, which selects `ETR_MODE_FLAT`, `ETR_MODE_ETR_SG`, `ETR_MODE_CATU`, or `ETR_MODE_RESRV`; each mode supplies `etr_buf_operations` for allocation, sync, data access, and free. Hardware programming is split between `tmc_etr_enable_hw`, `__tmc_etr_enable_hw`, `__tmc_etr_disable_hw`, and `tmc_etr_disable_hw`. User-visible operations are in `tmc_etr_sink_ops`, `tmc_etr_sync_ops`, `tmc_read_prepare_etr`, `tmc_read_unprepare_etr`, and the ETR attribute group.

## Control Flow

Sysfs enable obtains or allocates a persistent `sysfs_buf`, rejects concurrent perf mode, enables hardware, and sets CoreSight mode to `CS_MODE_SYSFS`. Sysfs read preparation stops a running sysfs session, syncs buffer offsets and lengths from RRP/RWP/STS, then marks `reading`; unprepare either restarts tracing or frees the buffer after consumption. Perf allocation creates an `etr_perf_buffer`; CPU-wide sessions share one `etr_buf` through `drvdata->idr` keyed by owner pid, while per-thread sessions allocate independently. Perf enable claims the sink for the pid, enables hardware, and stores `perf_buf`. Perf update flushes/stops the ETR, syncs trace data, trims to AUX space when needed, inserts a CoreSight barrier packet on overflow, copies into perf pages, and may re-enable hardware for active events.

## State and Persistence Behavior

Persistent state lives in `tmc_drvdata`: preferred mode, current hardware `etr_buf`, sysfs/perf buffers, owner pid, IDR, reserved buffer, crash metadata, and mode/refcount state in `csdev`. `etr_buf` carries mode, full flag, hardware address, offset, length, private backend state, and refcount. Reserved mode maps a pre-reserved physical buffer and can survive crashes; `tmc_panic_sync_etr` writes register snapshots, trace address, valid flag, and CRCs into crash metadata.

## Dependencies and Integration Points

The file depends on CoreSight core registration, TMC common helpers from `coresight-tmc.h`, CATU helper ops, perf AUX buffer APIs, DMA/IOMMU APIs, vmalloc page mapping, IDR/mutex/refcount, and crash-data helpers. It integrates with `coresight-tmc-core.c` for common TMC probe data and with CATU through exported operation registration.

## Risks and Edge Cases

Risk concentrates in DMA ownership, circular offset math, and concurrent sysfs/perf transitions. Flat and SG sync paths must map hardware RRP/RWP addresses back to buffer offsets correctly. Perf CPU-wide sharing relies on pid-keyed IDR and refcounts. `tmc_panic_sync_etr` must not claim crash metadata unless reserved mode and metadata buffers are valid. `tmc_update_etr_buffer` re-enables hardware after AUX pause while event state can change.

## Test Signals

Useful signals include sysfs/perf mutual exclusion, all buffer-mode selection paths, fallback from failed large perf buffers to smaller buffers, SG wrap reads, overflow barrier insertion, AUX truncation flags, reserved-mode crash metadata CRC validity, CATU registration/unregistration, and lockdep coverage around `spinlock` plus `idr_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc-etr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc.h

## Purpose

`coresight-tmc.h` is the shared register, type, capability, and helper interface for CoreSight TMC variants: ETB, ETF, and ETR. It defines the hardware register map, bit fields, buffer modes, crash metadata layout, driver state, SG table abstractions, and cross-file function prototypes used by the TMC core and variant implementations.

## Important APIs, Types, and Functions

Key enums are `tmc_config_type`, `tmc_mode`, `tmc_mem_intf_width`, and `etr_mode`. `struct tmc_crash_metadata` records ETR/ETF crash trace register state, data physical address, validity, version, and CRCs. `struct etr_buf`, `tmc_resrv_buf`, `tmc_drvdata`, `etr_buf_operations`, `tmc_pages`, and `tmc_sg_table` define all runtime buffer and device state. The header declares common TMC hardware helpers, ETB/ETF and ETR read paths, ETR sink ops, SG allocation/sync/data APIs, CATU integration hooks, and `coresight_etr_group`.

## Control Flow

TMC core code probes hardware and fills `tmc_drvdata`; variant files use the declared helpers according to `config_type`. ETB/ETF paths use `buf` and `len`, while ETR paths use `etr_buf`, `sysfs_buf`, `perf_buf`, and optional reserved/crash buffers. Register-pair helpers generated by `TMC_REG_PAIR` provide 64-bit accessors for RRP, RWP, and DBA through CoreSight accessors.

## State and Persistence Behavior

`tmc_drvdata` persists for the device lifetime and holds clock handles, MMIO base, CoreSight and misc devices, locks, owner pid, read state, mode-specific buffers, size/capability fields, IDR state, and reserved crash buffers. Crash metadata and reserved trace buffers persist beyond normal tracing when configured. Inline helpers validate reserved buffer presence, mark crash metadata invalid, and compute CRCs.

## Dependencies and Integration Points

The header depends on Linux DMA mapping, IDR, miscdevice, mutex, refcount, and CRC helpers. It bridges TMC core, ETB/ETF, ETR, CATU, CoreSight sysfs/perf, and crashdump-facing misc devices. Its capability flags include advertised SG and inferred SoC-600 save/restore and ARCACHE behavior.

## Risks and Edge Cases

Because it centralizes shared mutable state, layout changes can affect all TMC variants. CRC helpers assume `crash_mdata.vaddr` and `resrv_buf.vaddr` are valid before callers dereference metadata. `find_crash_tracedata_crc` hashes the configured RAM size rather than the consumed trace length. Capability bits include unadvertised hardware behavior, so PID-based setup outside this header must stay accurate.

## Test Signals

Build coverage should compile ETB/ETF/ETR/CATU combinations. Runtime tests should validate RRP/RWP/DBA pair access, reserved-buffer detection, crash invalidation, CRC generation, SG table sizing, and mode-specific buffer fields under sysfs and perf sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tnoc.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tnoc.c

## Purpose

`coresight-tnoc.c` implements a Trace NoC CoreSight link/merger. It programs a trace network-on-chip block to emit ATB traffic, optionally allocates a system trace ID for AMBA-discovered instances, and supports both AMBA and platform/DT instantiation.

## Important APIs, Types, and Functions

`struct trace_noc_drvdata` stores MMIO base, device, CoreSight device, optional APB clock, spinlock, and ATID. `trace_noc_enable_hw` writes ATID, sync interval, packet type bits, and port enable. `trace_noc_enable`, `trace_noc_disable`, and `trace_noc_id` implement CoreSight link ops and trace-id reporting. `_tnoc_probe` is the common probe path; `trace_noc_probe/remove` cover AMBA, while `itnoc_probe/remove` cover platform devices. `traceid` sysfs is hidden when no ATID is available.

## Control Flow

Probe allocates a device name, gets platform data, enables clocks, maps registers, initializes the lock, chooses default ATID behavior, and registers a CoreSight link of subtype `LINK_MERG`. AMBA devices allocate a system trace ID through `coresight_trace_id_get_system_id`; platform ITNoC devices set `atid` to `-EOPNOTSUPP` and simply enable the block without programming ATID. Enable is refcounted under the spinlock and only touches hardware on the first user. Disable decrements the CoreSight refcount and clears `TRACE_NOC_CTRL` on final user.

## State and Persistence Behavior

The allocated ATID persists until AMBA remove, where it is released. Runtime state is limited to `csdev->refcnt`, the spinlock-protected enable state, and runtime PM clock state for platform devices. The hardware control register is not shadowed beyond drvdata fields.

## Dependencies and Integration Points

The driver depends on AMBA, platform devices, OF matching (`qcom,coresight-itnoc`), runtime PM, CoreSight platform data, CoreSight driver init helpers, clock helpers, and the shared trace ID allocator. It integrates as an intermediate link in CoreSight paths.

## Risks and Edge Cases

Platform remove unregisters CoreSight but does not release an ATID, which is correct only because platform probe never allocates one. AMBA remove unconditionally calls `coresight_trace_id_put_system_id(drvdata->atid)`; this path expects positive ATIDs. Refcount underflow would disable the block incorrectly if CoreSight core calls are unbalanced.

## Test Signals

Test AMBA and platform probe/remove, traceid visibility for AMBA versus platform, runtime PM clock suspend/resume, first-enable and final-disable register writes, and trace ID release on AMBA unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tnoc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpda.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpda.c

## Purpose

`coresight-tpda.c` implements the Qualcomm Trace, Profiling and Diagnostic Aggregator as a CoreSight link merger. It aggregates TPDM sources, programs per-port element sizes, packetization controls, synchronization counts, flush requests, and a shared system ATID.

## Important APIs, Types, and Functions

Core functions include `tpda_get_element_size`, `tpda_enable_pre_port`, `tpda_enable_port`, `tpda_enable`, `tpda_disable`, and `tpda_trace_id`. Sysfs handlers manage cross-trigger booleans, `global_flush_req`, `syncr_mode`, `syncr_count`, and `port_flush_req`. `tpda_init_default_data` allocates the shared ATID and defaults FREQ timestamping on. `tpda_probe/remove` register the AMBA CoreSight link.

## Control Flow

On enable, the driver locks `spinlock`, programs global TPDA control only for the first active port, then enables the requested input port. Per-port setup walks incoming CoreSight connections, follows filter sources and recursive links, finds exactly one TPDM behind the port, reads `qcom,dsb-element-bits` and/or `qcom,cmb-element-bits`, encodes element size into `TPDA_Pn_CR`, and sets the port enable bit. Disable clears the per-port enable bit when that input's destination refcount reaches zero and decrements the aggregate refcount.

## State and Persistence Behavior

`tpda_drvdata` persists MMIO, CoreSight device, ATID, element-size scratch fields, cross-trigger settings, CMB channel mode, and SYNCR settings. Sysfs stores update shadow fields before the next enable, while flush show/store accesses live registers and requires the device to be enabled. ATID persists from probe to remove.

## Dependencies and Integration Points

The file depends on CoreSight connection topology, TPDM drvdata and helper predicates from `coresight-tpdm.h`, trace ID allocation, AMBA probing, DT firmware properties, and CoreSight lock/unlock access. It is tightly coupled to TPDM element-size properties and path topology.

## Risks and Edge Cases

The recursive element-size search rejects multiple TPDMs on one TPDA port with `-EEXIST`, and warns if no TPDM property is found. Flush sysfs operations fail when disabled and can only set, not clear, request bits. Settings are shadowed without checking whether hardware is currently enabled, so changes may not take effect until the next first-port enable.

## Test Signals

Exercise topology walks with direct TPDM, filtered source, recursive link, missing source, missing element properties, and multiple TPDMs. Verify sysfs validation, enabled-only flush operations, per-port refcount behavior, ATID release, and register programming for 8/32/64-bit CMB/DSB element sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpda.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpda.h

## Purpose

`coresight-tpda.h` defines the TPDA register map, bit fields, maximum port count, driver state, and sysfs attribute wrapper used by the TPDA CoreSight aggregator driver.

## Important APIs, Types, and Functions

Definitions cover `TPDA_CR`, per-port control registers, FPID, SYNCR, and flush control. Bit fields describe global flush, FREQ timestamping and request interfaces, FLAG and async trigger interfaces, ATID encoding, CMB channel mode, port enable, and DSB/CMB element sizes. `struct tpda_drvdata` stores MMIO base, device handles, lock, ATID, element sizes, cross-trigger booleans, CMB channel mode, SYNCR mode, and count. `enum tpda_cr_mem` and `struct tpda_trig_sysfs_attribute` drive generic sysfs show/store for boolean control fields.

## Control Flow

The C file uses these definitions to assemble global TPDA control before enabling any port, configure per-port element sizes, and expose boolean controls through `tpda_trig_sysfs_rw`. `TPDA_MAX_INPORTS` bounds the architectural port model used by the device.

## State and Persistence Behavior

The header defines the persistent TPDA shadow state. Most booleans are stored in `tpda_drvdata` and only become hardware state when enable paths write `TPDA_CR`. Element-size fields are scratch values discovered from connected TPDM devices during per-port enable and cleared before each lookup.

## Dependencies and Integration Points

It depends on common kernel bit macros and CoreSight types included by the C file. It integrates directly with `coresight-tpda.c` and indirectly with TPDM because element-size fields encode TPDM dataset output widths.

## Risks and Edge Cases

Field definitions must match hardware, especially `TPDA_CR_ATID` and element-size bit encodings. The anonymous compound-literal macro for sysfs attributes relies on static storage behavior through the containing attribute list usage pattern; future refactors should preserve lifetime assumptions.

## Test Signals

Build tests should catch macro and enum drift. Runtime signals include correct sysfs attribute names, accurate ATID bit placement, SYNCR mask behavior, and per-port size programming for supported element widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpda.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpdm.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpdm.c

## Purpose

`coresight-tpdm.c` implements Qualcomm Trace, Profiling and Diagnostic Monitor devices as CoreSight sources. It discovers DSB, CMB, and MCMB datasets, exposes a large sysfs configuration surface, programs dataset registers on enable, and supports dynamic AMBA TPDM plus static platform TPDM nodes.

## Important APIs, Types, and Functions

Dataset helpers include `tpdm_has_*_dataset`, `tpdm_datasets_setup`, `static_tpdm_datasets_setup`, and `tpdm_reset_datasets`. Register programming is handled by `tpdm_enable_dsb`, `tpdm_enable_cmb`, `tpdm_disable_dsb`, and `tpdm_disable_cmb`. CoreSight source ops are `tpdm_enable` and `tpdm_disable`. Sysfs handlers manage DSB mode, edge control index/value/mask, pattern and trigger arrays, MSRs, timestamp booleans, CMB/MCMB modes, trace ID, dataset reset, and integration test writes. Probe paths are `dynamic_tpdm_probe` for AMBA and `tpdm_platform_probe` for static DT nodes.

## Control Flow

Dynamic probe maps registers, reads `CORESIGHT_PERIPHIDR0` to identify datasets, allocates `dsb_dataset` and/or `cmb_dataset`, reads optional MSR counts from DT, and registers a CoreSight TPDM source with full sysfs groups. Static probe has no MMIO resource and only registers traceid visibility, allocating dataset structs from firmware properties. Enable takes a CoreSight mode, programs DSB/CMB registers under lock unless static, records `path->trace_id`, and marks enabled. Disable clears dataset enable bits and returns the CoreSight device to disabled mode.

## State and Persistence Behavior

`tpdm_drvdata` persists dataset presence bits, allocated DSB/CMB config structs, MSR counts, enable flag, and last trace ID. Sysfs writes modify shadow dataset structures; hardware is programmed from those shadows on enable. Reset clears dataset state and restores DSB default trigger timestamp true and trigger type false. Static TPDM has no register programming but still participates as a CoreSight source for topology purposes.

## Dependencies and Integration Points

The driver depends on CoreSight source APIs, CoreSight PMU path trace IDs, AMBA/platform driver helpers, DT properties, bitfield helpers, and register constants from `coresight-tpdm.h`. TPDA consumes TPDM drvdata and firmware element-size properties to configure aggregation ports.

## Risks and Edge Cases

The sysfs surface is large and mostly writes shadow state even while enabled; changes during active tracing may not affect hardware until re-enable. Many show/store paths assume the relevant dataset pointer exists and rely on attribute visibility to prevent invalid access. MSR visibility depends on DT-provided counts. Static TPDM cannot run `integration_test` and does not expose configuration groups. Traceid reads fail until a path has enabled the source.

## Test Signals

Exercise dynamic and static probe, dataset detection for DSB/CMB/MCMB combinations, attribute visibility, MSR count limits, invalid sysfs values, reset defaults, integration test requiring enabled state, traceid after path enable, and register writes for DSB/CMB programming. Lockdep and race tests should cover sysfs writes versus enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpdm.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpdm.h

## Purpose

`coresight-tpdm.h` defines the TPDM dataset register map, bit fields, dataset storage structures, sysfs attribute macros, and helper predicates used by the TPDM driver and by TPDA integration.

## Important APIs, Types, and Functions

The header covers CMB/MCMB registers, DSB registers, integration-test registers, PIDR0 dataset presence bits, maximum pattern/MSR/edge-control dimensions, and packing helpers for edge-control arrays. `struct dsb_dataset` stores DSB mode, edge controls, patterns, trigger patterns, MSRs, and timestamp/trigger flags. `struct cmb_dataset` stores trace mode, patterns, MSRs, timestamp flags, and MCMB lane settings. `struct tpdm_drvdata` is the persistent TPDM device state. `enum dataset_mem` and `struct tpdm_dataset_attribute` route generic sysfs handlers. Inline helpers identify TPDM CoreSight devices and static TPDM devices.

## Control Flow

The C driver uses macro-generated attributes to avoid hand-writing dozens of DSB/CMB sysfs entries. On enable, shadow structures defined here are translated into hardware register writes. TPDA uses `coresight_device_is_tpdm` when walking upstream topology and `coresight_is_static_tpdm` helps TPDM skip MMIO programming for static sources.

## State and Persistence Behavior

Dataset structures persist for the device lifetime and are reset, modified via sysfs, and consumed on enable. Array dimensions define the maximum persistent configuration exposed to userspace. The `traceid` field persists the last CoreSight path trace ID while enabled.

## Dependencies and Integration Points

The header integrates with CoreSight source subtype definitions, Linux bit macros, and TPDA. It encodes Qualcomm-specific firmware properties and hardware register layouts.

## Risks and Edge Cases

Macro-generated sysfs attributes make index correctness critical. Attribute visibility must stay aligned with dataset pointer allocation, otherwise show/store functions can dereference NULL dataset structs. Max constants and bit masks must match hardware; expanding hardware support requires careful ABI handling for existing sysfs names.

## Test Signals

Compile coverage should verify all generated attributes. Runtime tests should validate edge-control packing, CMB/MCMB lane masks, DSB mode masks, MSR visibility limits, static TPDM predicate behavior, and TPDA recognition of TPDM devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpiu.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpiu.c

## Purpose

`coresight-tpiu.c` implements the Arm CoreSight Trace Port Interface Unit as an output sink. It registers AMBA and platform/ACPI TPIU devices, manages optional clocks and runtime PM, and provides enable/disable sink operations.

## Important APIs, Types, and Functions

`struct tpiu_drvdata` stores MMIO base, optional ATCLK/PCLK, CoreSight device, and spinlock. `tpiu_enable_hw` currently only unlocks and locks the device around a TODO. `tpiu_disable_hw` programs formatter stop-on-flush, triggers manual flush, waits for flush completion and formatter stopped, then relocks. CoreSight sink ops are `tpiu_enable` and `tpiu_disable`. Common probe/remove logic is in `__tpiu_probe` and `__tpiu_remove`, with AMBA and platform wrappers.

## Control Flow

Probe allocates a CoreSight name, drvdata, clocks, maps registers, disables the TPIU for older devices, gets platform data, and registers a CoreSight sink of subtype `SINK_PORT`. Enable locks, calls the mostly-empty hardware enable hook, increments refcount, and returns success. Disable decrements refcount and only flushes/stops hardware on the final user; otherwise it returns `-EBUSY`.

## State and Persistence Behavior

Persistent state is drvdata plus CoreSight refcount. Runtime PM suspend disables ATCLK and PCLK, and resume re-enables PCLK then ATCLK with rollback on failure. No trace data is buffered in this driver.

## Dependencies and Integration Points

The driver depends on AMBA IDs, platform ACPI match `ARMHC979`, CoreSight core registration, clock helpers, runtime PM, and CoreSight timeout helpers. It integrates as a port sink at the end of CoreSight paths.

## Risks and Edge Cases

The enable path has no hardware programming beyond unlock/lock, so correctness depends on external/default TPIU configuration. Disable returns `-EBUSY` after decrementing when other users remain, matching sink conventions but requiring callers to tolerate that code. Timeout return values in `tpiu_disable_hw` are ignored.

## Test Signals

Probe should be tested for AMBA and platform/ACPI, clock failure rollback, initial disable programming, final-disable flush behavior, runtime PM suspend/resume, and CoreSight refcount behavior across multiple users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-tpiu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trace-id.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trace-id.c

## Purpose

`coresight-trace-id.c` implements the CoreSight trace ID allocator. It assigns architecturally valid trace IDs to CPUs and system trace sources, preserves CPU IDs across overlapping perf sessions, supports static requested IDs, and exports map-based variants for non-default sink maps.

## Important APIs, Types, and Functions

The default state is `id_map_default`, backed by per-CPU atomic IDs and a raw spinlock. Internal helpers include `_coresight_trace_id_read_cpu_id`, `coresight_trace_id_find_odd_id`, `coresight_trace_id_alloc_new_id`, `coresight_trace_id_free`, `coresight_trace_id_release_all`, and map-specific CPU/system get/put helpers. Exported APIs include CPU get/read/put, map variants, system get/static-get/put, and perf session start/stop notifications.

## Control Flow

CPU allocation first returns an existing per-CPU ID if present. Otherwise it tries the legacy CPU trace ID, then any available valid ID. System allocation prefers odd IDs to reduce collision with legacy CPU values. Static system allocation requires the requested valid ID to be free. Perf start increments `perf_cs_etm_session_active`; perf stop decrements it and releases all IDs only when the last session stops, preserving stable CPU-to-ID mapping across concurrent perf events.

## State and Persistence Behavior

The allocator persists a bitmap of used IDs and per-CPU atomic assignments. IDs are reserved between `get` and `put`, while perf sessions intentionally defer CPU ID release until all sessions complete. `coresight_trace_id_release_all` clears both bitmap and CPU atomics under lock.

## Dependencies and Integration Points

The file depends on CoreSight PMU trace ID map definitions, CPU masks, atomics, bitmaps, and raw spinlocks. It is consumed by ETM/ETE CPU sources, TPDA, Trace NoC, dummy/static sources, and any system component requiring a CoreSight trace ID.

## Risks and Edge Cases

`coresight_trace_id_read_cpu_id*` is intentionally lockless for perf contexts, so callers must use it only when IDs are known stable. Put operations warn on invalid or unused IDs. Static allocation returns `-EBUSY` for valid but occupied IDs and `-EINVAL` for invalid requested IDs. A missing perf stop would retain IDs indefinitely.

## Test Signals

Tests should cover legacy CPU preference, odd system allocation, exhaustion, static ID conflicts, invalid puts, perf start/stop release semantics, lockless reads during active sessions, and map-specific isolation from the default allocator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trace-id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trace-id.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trace-id.h

## Purpose

`coresight-trace-id.h` declares the public CoreSight trace ID allocation API and documents the allocator contract for CPU and system trace sources.

## Important APIs, Types, and Functions

The header defines reserved ID boundaries with `CORESIGHT_TRACE_ID_RES_0`, `CORESIGHT_TRACE_ID_RES_TOP`, and `IS_VALID_CS_TRACE_ID`. It declares CPU allocation/read/release APIs, map-specific variants, system and static system allocation APIs, system release, and perf session start/stop notifications.

## Control Flow

Callers obtain a CPU ID with `coresight_trace_id_get_cpu_id*`, emit or program it, and release it with `put` unless perf session semantics defer release. Fast readers use `coresight_trace_id_read_cpu_id*` when allocation cannot change. System sources call `coresight_trace_id_get_system_id` or request a static ID, then later release it.

## State and Persistence Behavior

State is owned by the implementation file and by optional `coresight_trace_id_map` instances supplied by callers. The API contract states that perf sessions retain CPU mappings until the final session stops.

## Dependencies and Integration Points

The header depends on bitops/types and `struct coresight_trace_id_map` from CoreSight public headers. It is included by CoreSight sources, links needing ATIDs, and perf ETM code.

## Risks and Edge Cases

Callers must not program ID 0 or IDs at/above `0x70`. Lockless reads are only safe under the documented perf stability condition. Every successful system allocation needs a matching put.

## Test Signals

Compile users against all declared APIs, and runtime-check invalid ID rejection, map-specific behavior, static allocation, and perf session lifetime semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trace-id.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trbe.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trbe.c

## Purpose

`coresight-trbe.c` implements Arm Trace Buffer Extension as a per-CPU CoreSight system-memory sink for ETE/ETM trace capture through perf AUX buffers. It configures TRBE system registers, handles per-CPU maintenance interrupts, applies CPU erratum workarounds, and registers one percpu sink per supported CPU.

## Important APIs, Types, and Functions

`struct trbe_buf` maps perf AUX pages into a contiguous virtual TRBE buffer and tracks base, hardware base, limit, write pointer, pages, snapshot mode, and CPU data. `struct trbe_cpudata` stores per-CPU alignment, flags, mode, current buffer, and errata bitmap. `struct trbe_drvdata` stores percpu data, percpu perf handles, hotplug node, IRQ, supported CPUs, and platform device. Core paths include `arm_trbe_alloc_buffer`, `arm_trbe_enable`, `arm_trbe_update_buffer`, `arm_trbe_disable`, `arm_trbe_irq_handler`, CPU probe/register helpers, IRQ setup, and hotplug setup.

## Control Flow

Probe rejects KPTI-style unmapped kernel-at-EL0 systems, allocates drvdata, obtains a percpu PPI IRQ and affinity mask, allocates per-CPU handles, probes each supported CPU via SMP calls, registers a CoreSight percpu sink, enables its IRQ, and registers CPU hotplug callbacks. Enable computes a writable AUX range from perf head/tail/wakeup, aligns/pads with ETE ignore packets, applies erratum-specific base/limit adjustments, stores the current handle, and programs TRBBASER/TRBPTR/TRBLIMITR. IRQ handling prohibits tracing, drains and disables TRBE, classifies status as wrap/spurious/fatal, updates perf AUX output and re-enables if possible, or truncates on fatal/no-space cases.

## State and Persistence Behavior

Per-CPU CoreSight devices and `trbe_cpudata` persist while the platform device is bound. Current perf handles are stored percpu during active sessions. TRBE hardware state is reset on CPU enable/disable and remove. Errata bits are cached per CPU after probing. Perf snapshot mode advances head directly; normal mode uses `perf_aux_output_skip/end/begin` to manage consumed space.

## Dependencies and Integration Points

The driver depends on arm64 TRBE/ETE system registers, CPU feature detection, KVM TRBE enable/disable hooks, CoreSight percpu sink APIs, perf AUX APIs, CPU hotplug, percpu IRQ affinity, vmalloc page mapping, and erratum cpucaps. It is matched by OF `arm,trace-buffer-extension` and ACPI platform ID `ARMV8_TRBE_PDEV_NAME`.

## Risks and Edge Cases

The buffer limit calculation is complex and must avoid overwriting unconsumed perf data. Errata can require PAGE alignment, skipped bytes, an extra guard page, additional barriers, or disabling broken CPUs. IRQ and update paths race with event stop, so local IRQ masking and handle clearing are critical. `arm_trbe_irq_handler` obtains the buffer before checking for a NULL handle, so the percpu handle must only be NULL when no IRQ is pending.

## Test Signals

Test minimum page rejection, normal versus snapshot AUX behavior, wakeup/tail alignment padding, wrap IRQ restart, spurious IRQ re-enable, fatal abort truncation, CPU hotplug register/unregister, per-CPU IRQ affinity, KPTI rejection, and each erratum path including overwrite-fill, out-of-range, drain-after-disable, context-sync-after-enable, and broken-CPU disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trbe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trbe.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trbe.h

## Purpose

`coresight-trbe.h` provides TRBE hardware helper routines for feature detection, status decoding, register access, pointer programming, and include dependencies used by the TRBE driver.

## Important APIs, Types, and Functions

Helpers include `is_trbe_available`, `is_trbe_enabled`, `get_trbe_ec`, `get_trbe_bsc`, IRQ/status predicates, flag/programming/alignment readers, write/base/limit pointer accessors, and TRBE register setters. Constants define TRBE exception classes and buffer status codes.

## Control Flow

The C driver calls these helpers while probing CPU capability, clearing status, setting base/write/limit registers, detecting wrap/fatal/spurious events, and enforcing alignment. Setters warn if programming is attempted while TRBE is enabled or with misaligned pointers.

## State and Persistence Behavior

The header has no persistent C state; it directly reads and writes per-CPU system registers. Hardware register contents persist until reset, disable, CPU power events, or explicit driver writes.

## Dependencies and Integration Points

It includes ACPI, CoreSight, IRQ, OF, platform, SMP, Arm PMU/perf, and `coresight-etm-perf.h`, making it the hardware-facing companion to `coresight-trbe.c`. It depends on arm64 system register definitions.

## Risks and Edge Cases

Inline register helpers assume execution on the target CPU. Misuse from the wrong CPU or while enabled can corrupt active capture, guarded only by `WARN_ON`. Alignment fields from hardware must be interpreted correctly because downstream limit calculation depends on them.

## Test Signals

Probe tests should validate feature detection and alignment extraction. Runtime tests should assert warning-free base/write/limit programming, status predicate correctness, IRQ clearing, and behavior when helpers are called with TRBE disabled versus enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-trbe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/ultrasoc-smb.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/ultrasoc-smb.c

## Purpose

`ultrasoc-smb.c` implements the Siemens/UltraSoc System Memory Buffer as a CoreSight sink. It configures the hardware logical buffer, exposes a miscdevice for sysfs-style reads, supports perf AUX copying, and uses ACPI DSM calls to enable or disable upstream UltraSoc hardware.

## Important APIs, Types, and Functions

Buffer helpers are `smb_buffer_not_empty`, `smb_update_data_size`, `smb_update_read_ptr`, and `smb_reset_buffer`. File operations are `smb_open`, `smb_read`, and `smb_release`. CoreSight sink operations are `smb_enable`, `smb_disable`, `smb_alloc_buffer`, `smb_free_buffer`, and `smb_update_buffer`. Probe helpers include `smb_init_data_buffer`, `smb_init_hw`, `smb_register_sink`, and `smb_config_inport`.

## Control Flow

Probe maps register space, initializes hardware defaults, maps the data buffer resource with write-back memory, enables upstream hardware with ACPI DSM, resets the buffer, initializes locking and pid state, registers a CoreSight buffer sink, and registers a miscdevice. Sysfs/misc reads are mutually exclusive with active CoreSight capture. Perf enable associates the sink with the event owner pid and enables hardware. Perf update disables hardware, calculates available circular data, trims to perf AUX size if needed, copies into perf pages, resets the SMB, and reports truncation when not in snapshot mode.

## State and Persistence Behavior

`smb_drv_data` persists MMIO base, CoreSight device, buffer mapping, miscdevice, raw spinlock, reading flag, and owner pid. `smb_data_buffer` tracks hardware base, CPU mapping, total size, data size, and read pointer. Hardware read pointer is updated after every copied or discarded segment.

## Dependencies and Integration Points

The driver depends on platform ACPI matching (`HISI03A1`), CoreSight sink APIs, perf AUX `cs_buffers`, circular buffer macros, miscdevice, memremap, and ACPI DSM UUID `82ae1283-7f6a-4cbe-aa06-53e8fb24db18`.

## Risks and Edge Cases

The driver assumes a 32-bit buffer hardware base. It serializes reads and tracing with `raw_spinlock`, but copy-to-user occurs outside that lock in `smb_read` after open-time exclusion. Perf copying must handle circular wrap correctly and advances the hardware read pointer destructively. ACPI DSM failure prevents probe.

## Test Signals

Test probe resource validation, DSM enable/disable, misc open rejection during capture, duplicate open rejection, circular read wrap, buffer-full detection, perf truncation, snapshot behavior, register sysfs reads, and remove cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/ultrasoc-smb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/ultrasoc-smb.h -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/ultrasoc-smb.h

## Purpose

`ultrasoc-smb.h` defines the register offsets, bit fields, default register values, resource indices, and driver data structures for the UltraSoc/Siemens SMB CoreSight sink.

## Important APIs, Types, and Functions

The header maps global config/enable/interrupt registers, logical buffer config/status/read/write/purge registers, default configuration values, interrupt bits, resource indices, and buffer base masks. `struct smb_data_buffer` stores mapped buffer address, hardware base, size, available data, and read pointer. `struct smb_drv_data` stores MMIO base, CoreSight device, buffer state, miscdevice, lock, reading flag, and owner pid.

## Control Flow

The C file uses these constants to initialize SMB hardware, detect non-empty/full state, update read pointers, reset/purge buffers, expose management registers, and map platform resources.

## State and Persistence Behavior

The structures define persistent device state. `buf_rdptr` and `data_size` are mutable software mirrors of hardware circular-buffer state; `pid` and `reading` serialize ownership between perf and miscdevice users.

## Dependencies and Integration Points

It depends on bitfield helpers, miscdevice, and spinlock definitions. It is private to `ultrasoc-smb.c` and its CoreSight sink integration.

## Risks and Edge Cases

Default bitfield values must match hardware expectations. The low 32-bit hardware base mask encodes an architectural limitation that may not work for buffers above 4 GiB. Software and hardware read pointers must remain synchronized.

## Test Signals

Validate register default encodings, resource index use, buffer size/resource parsing, read/write pointer arithmetic, purge/reset status bits, and owner-state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/ultrasoc-smb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/Kconfig

## Purpose

`intel_th/Kconfig` defines configuration symbols for the Intel Trace Hub controller, platform glue, subdevices, output devices, and optional debugging support.

## Important APIs, Types, and Functions

The main symbol is `INTEL_TH`, a tristate depending on `HAS_DMA` and `HAS_IOMEM`. Child symbols include `INTEL_TH_PCI`, `INTEL_TH_ACPI`, `INTEL_TH_GTH`, `INTEL_TH_STH`, `INTEL_TH_MSU`, `INTEL_TH_PTI`, and `INTEL_TH_DEBUG`. Dependencies include `PCI`, `ACPI`, `STM`, `MMU`, and `DEBUG_FS` as appropriate.

## Control Flow

When `INTEL_TH` is enabled, the nested menu exposes transport glue and subdevice choices. PCI and ACPI instantiate controllers; GTH is the central switch; STH integrates software sources through STM; MSU stores traces in memory; PTI emits trace through a parallel port; DEBUG adds debugfs support.

## State and Persistence Behavior

Kconfig state controls which objects are built into the kernel or as modules. It does not define runtime state, but selected symbols determine available device probing and user-visible trace functionality.

## Dependencies and Integration Points

The file integrates with the `intel_th/Makefile` object rules and the Linux hwtracing menu hierarchy. It gates ACPI, PCI, STM, memory storage, and debugfs code.

## Risks and Edge Cases

Misconfigured dependencies can produce unbuildable combinations or missing subdevices. Enabling ACPI indicates host-debugger mode where target controls may not be available, which can surprise users expecting local capture control.

## Test Signals

Run build matrix coverage for built-in and module variants, including `INTEL_TH` alone, PCI, ACPI, GTH, STH with STM, MSU with MMU, PTI, and DEBUG with DEBUG_FS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/Makefile

## Purpose

`intel_th/Makefile` maps Intel Trace Hub Kconfig symbols to kernel objects and composite module contents.

## Important APIs, Types, and Functions

It builds `intel_th.o` from `core.o` plus optional `debug.o`. It builds glue modules `intel_th_pci.o` and `intel_th_acpi.o`, subdevice modules `intel_th_gth.o`, `intel_th_sth.o`, `intel_th_msu.o`, `intel_th_pti.o`, and `intel_th_msu_sink.o` from their corresponding source files.

## Control Flow

Kbuild includes each object according to `CONFIG_INTEL_TH*` symbols. Composite `*-y` assignments define which source files are linked into each module or built-in object.

## State and Persistence Behavior

There is no runtime state. Build state persists in generated objects according to Kconfig selections.

## Dependencies and Integration Points

This file integrates directly with `intel_th/Kconfig` and the Linux Kbuild system. `intel_th_msu_sink.o` is gated by `CONFIG_INTEL_TH_MSU`, so memory-storage sink support builds with MSU.

## Risks and Edge Cases

Object rules must stay synchronized with source filenames and Kconfig symbols. If a symbol is renamed or a source is moved, stale rules cause missing drivers or build failures.

## Test Signals

Build with each Intel TH config as built-in and module. Confirm optional debug object appears only with `CONFIG_INTEL_TH_DEBUG` and that MSU sink links when MSU is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/acpi.c -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/acpi.c

## Purpose

`intel_th/acpi.c` is the ACPI platform glue driver for Intel Trace Hub controllers. It matches ACPI IDs, collects memory and IRQ resources, allocates the shared Intel TH core object, and frees it on removal.

## Important APIs, Types, and Functions

Static `intel_th_drvdata` instances for PCH and uncore set `host_mode_only = 1`. `intel_th_acpi_ids` matches `INTC1000` and `INTC1001`. `intel_th_acpi_probe` filters platform resources into a fixed `TH_MMIO_END` array and calls `intel_th_alloc`. `intel_th_acpi_remove` calls `intel_th_free`. `module_platform_driver` registers `intel_th_acpi_driver`.

## Control Flow

Probe obtains the ACPI companion and matching ID, copies IRQ and memory resources up to the core limit, allocates the Intel TH core with ID-specific drvdata, and stores the returned pointer in `adev->driver_data`. Remove gets the platform drvdata and frees the core.

## State and Persistence Behavior

The Intel TH core object persists after successful probe until remove. The drvdata marks ACPI devices as host-mode-only, reflecting externally controlled trace capture. No sysfs state is created directly by this glue file.

## Dependencies and Integration Points

The file depends on Linux ACPI/platform APIs, module infrastructure, resource flags, and `intel_th.h` core allocation/free routines. It is built by `CONFIG_INTEL_TH_ACPI`.

## Risks and Edge Cases

Probe stores `adev->driver_data = th`, while remove uses `platform_get_drvdata(pdev)`; correctness depends on `intel_th_alloc` or platform/ACPI glue setting platform drvdata consistently. Resource filtering preserves only IRQ and memory resources and stops at `TH_MMIO_END`, so unexpected resource ordering or extra resources are ignored.

## Test Signals

Test matching for `INTC1000` and `INTC1001`, no-match `-ENODEV`, resource filtering limits, `intel_th_alloc` error propagation, remove-time free, and host-mode-only behavior in the core driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/acpi.c -->
