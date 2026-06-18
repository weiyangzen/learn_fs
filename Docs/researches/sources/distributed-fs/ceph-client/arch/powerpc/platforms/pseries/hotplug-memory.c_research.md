# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/hotplug-memory.c

Purpose: Implements pseries memory hotplug and DLPAR memory add/remove for dynamic reconfiguration memory. It updates LMB associativity, adds/removes Linux memory blocks, onlines/offlines memory devices, updates DRMEM state, and handles OF reconfiguration.

Important APIs/types/functions: Defines property clone/free helpers, `find_aa_index()`, `update_lmb_associativity_index()`, `lmb_to_memblock()`, `get_lmb_range()`, `dlpar_change_lmb_state()`, hot-remove helpers under `CONFIG_MEMORY_HOTREMOVE`, `dlpar_add_lmb()`, `dlpar_memory_add_by_count/index/ic()`, `dlpar_memory_remove_by_count/index/ic()`, `dlpar_memory()`, `pseries_add_mem_node()`, memory OF notifier, and `pseries_memory_hotplug_init()`.

Control flow: Add paths validate target LMBs, acquire DRCs, configure connector data to derive associativity, update lookup arrays when needed, call `__add_memory()`, online memory blocks, mark LMBs assigned, and roll back added LMBs if a count/range add is incomplete. Remove paths validate removability, offline memory blocks, call `__remove_memory()`, update memblock and associativity, clear assignment, release DRCs, and roll back removed LMBs on partial failure. Successful DLPAR operations refresh the DRMEM device-tree property.

State and persistence: Persistent state includes `drmem_info` LMB flags, DRC state, LMB associativity indexes, `/ibm,dynamic-reconfiguration-memory` properties, Linux memory block online/offline state, memblock regions, NUMA distance data, and dynamic OF memory node changes.

Dependencies and integration points: Depends on pseries DLPAR common helpers, DRMEM infrastructure, memory hotplug core, memblock, NUMA associativity lookup arrays, fadump reservations, dynamic OF reconfig notifiers, and firmware LMB/DRC conventions.

Risks: Partial add/remove rollback is complex and must not leak DRCs or leave LMB flags inconsistent. Fadump and reserved LMBs must not be removed. Associativity lookup array updates allocate and replace OF properties dynamically. `pseries_remove_memblock()` updates `base` during removal before `memblock_remove()`, which is a sensitive path to audit.

Test signals: Memory DLPAR add/remove by count, index, and indexed-count; rollback injection; DRMEM property refresh; NUMA associativity changes; fadump reserved-memory protection; memory block online/offline sysfs state; and builds without `CONFIG_MEMORY_HOTREMOVE` are key.

Source read size: 929 lines, 20632 bytes.
