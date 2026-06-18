# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pseries_energy.c

Purpose: Exposes pSeries `H_BEST_ENERGY` CPU activation/deactivation hints through CPU sysfs files.

Important APIs/types/functions: Implements `cpu_to_drc_index()`, `drc_index_to_cpu()`, `get_best_energy_list()`, `get_best_energy_data()`, sysfs show wrappers, `pseries_energy_init()`, and cleanup.

Control flow: Init requires `FW_FEATURE_BEST_ENERGY`, creates root CPU hint-list files, and creates per-CPU hint files. Reads convert between logical CPUs and DRC indexes using either `ibm,drc-info` or legacy `ibm,drc-indexes`, call `H_BEST_ENERGY` in list or per-CPU mode, and format online/offline activation or deactivation candidates.

State and persistence: Maintains only `sysfs_entries` to guard cleanup. Hint data comes live from hypervisor.

Dependencies and integration points: Depends on CPU sysfs, OF CPU DRC properties, PAPR hcalls, CPU online state, module init/exit, and firmware feature detection.

Risks: DRC parsing has legacy and modern formats and must handle references correctly. The `ibm,drc-info` loops use early exits on non-CPU DRC types. CPU device pointers are assumed present for possible CPUs during sysfs creation and removal.

Test signals: Systems with both DRC property formats, online/offline CPU hint lists, per-CPU hint values, unsupported hcall, CPU hotplug interactions, module unload cleanup, and malformed OF DRC properties.

Source read size: 368 lines, 8828 bytes.
