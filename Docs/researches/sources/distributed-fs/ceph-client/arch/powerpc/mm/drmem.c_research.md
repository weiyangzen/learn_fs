# sources/distributed-fs/ceph-client/arch/powerpc/mm/drmem.c

Purpose: parses, tracks, walks, and updates pseries dynamic-reconfiguration memory LMB metadata from device-tree properties.

Important APIs and control flow: `walk_drmem_lmbs_early()` and `walk_drmem_lmbs()` decode v1 `ibm,dynamic-memory` and v2 `ibm,dynamic-memory-v2` formats, passing synthesized `drmem_lmb` records to callbacks. `drmem_init()` builds the global `drmem_info` LMB array at late init. `drmem_update_dt()` clones and rewrites dynamic-memory properties from in-kernel LMB state. `drmem_update_lmbs()` handles hypervisor/device-tree property updates while avoiding feedback from self-generated updates.

State and dependencies: persistent state includes `drmem_info`, LMB size/count/array, root cell sizes, and `in_drmem_update`. It depends on OF flat/live tree APIs, endian conversion, memblock, pseries hotplug conventions, and optional usable-memory properties for kdump. Risks are v1/v2 format drift, incorrect sequence compression, LMB flag leakage from internal reserved bits, missing allocation cleanup, and races with device-tree notifiers. Test signals include pseries memory hotplug, kdump usable-memory parsing, live DT property updates, and LMB size edge cases.
