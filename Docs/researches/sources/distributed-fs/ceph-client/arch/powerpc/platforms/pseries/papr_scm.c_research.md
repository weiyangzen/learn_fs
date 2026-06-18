# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/papr_scm.c

Purpose: Implements the PAPR Storage Class Memory platform driver, registering `ibm,pmemory` devices as libnvdimm DIMMs/regions with metadata, health, performance, flush, badblock, and PDSM support.

Important APIs/types/functions: Central type is `struct papr_scm_priv`. Key functions include bind/unbind/query helpers, `papr_scm_pmem_flush()`, `drc_pmem_query_stats()`, PMU callbacks, health query/cache helpers, metadata get/set, PDSM validators/services, `papr_scm_ndctl()`, sysfs attributes, `papr_scm_nvdimm_init()`, MCE notifier `handle_mce_ue()`, and platform driver probe/remove.

Control flow: Probe reads required OF properties, updates NUMA distances, binds the DRC memory through `H_SCM_BIND_MEM`, builds the memory resource, discovers perf-stat buffer size, registers an nvdimm bus, DIMM, and pmem/volatile region, and optionally registers a PMU. ndctl commands dispatch metadata reads/writes or PAPR PDSM packages. Health and perf sysfs files query hypervisor data on demand. Machine-check UE notifications inside a registered SCM region add nvdimm bad ranges.

State and persistence: Per-device state tracks DRC index, block geometry, bound physical address, libnvdimm objects, dirty shutdown counter, cached health bitmap and timestamp, injection mask, stat buffer length, resource, and list membership under `papr_ndr_lock`. Firmware persists SCM contents and metadata.

Dependencies and integration points: Integrates with PAPR SCM hcalls, platform devices from `pmem.c`, libnvdimm/ndctl/PDSM UAPI, perf PMU support, machine-check notifier chains, NUMA mapping, and nvdimm poison notification.

Risks: Long-running hcall retry loops must not abort partial bind/unbind operations. Metadata byte-width endian conversions, PDSM size validation, health-cache locking, resource overflow (`blocks * block_size` comment), and PMU lifetime via `pdev->archdata.priv` are notable risk areas. `pdsm_cmd_desc()` uses `if (cmd >= 0 || cmd < ARRAY_SIZE(...))`, which is logically permissive and should be scrutinized.

Test signals: Hot-add/remove pmem devices, ndctl get/set config, PAPR health and smart-inject PDSMs, hcall busy/partial/error paths, perf stat reads, MCE UE badblock insertion, volatile and persistent regions, module unload, and KASAN/lockdep fault injection around probe cleanup.

Source read size: 1542 lines, 42875 bytes.
