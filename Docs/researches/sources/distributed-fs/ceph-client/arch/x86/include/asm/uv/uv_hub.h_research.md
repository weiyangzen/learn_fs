# sources/distributed-fs/ceph-client/arch/x86/include/asm/uv/uv_hub.h

Purpose: SGI/HPE UV hub architecture definitions for global physical addressing, NASID/GNODE/PNODE conversion, GAM ranges, MMR access, blade/node/cpu mapping, TSC/NMI hub flags, and per-CPU/per-hub metadata.

Important APIs/types/functions: `struct uv_gam_range_s`, `struct uv_hub_info_s`, `struct uv_cpu_info_s`, per-CPU `__uv_cpu_info`, `uv_hub_info_list()`, `uv_hub_info`, hub type predicates (`is_uv2_hub()` etc.), `UV_NASID_TO_PNODE()`, `UV_PNODE_TO_GNODE()`, MMR base/size macros, GPA conversion helpers (`uv_gpa_shift()`, `uv_gam_range()`, `uv_soc_phys_ram_to_gpa()`, `uv_gpa_to_soc_phys_ram()`, `uv_gpa_to_gnode()`, `uv_gpa_to_pnode()`, `uv_gpa_to_offset()`), socket/pnode/node conversion helpers, MMR read/write helpers, blade CPU/node helpers, `uv_possible_blades`, NMI structs, and UV NMI state constants.

Control flow: most routines are inline transforms over boot-populated `uv_hub_info`. Address conversion handles UV4+/GAM table formats, low-memory remap, m/n bit layouts, pnode/socket translation tables, and MMIO address construction. MMR helpers create local/global virtual addresses and issue `readq/writeq/readb/writeb`. Blade helpers map CPUs, nodes, sockets, pnodes, and memory NIDs. `uv_gam_range()` scans the GAM range table and `BUG()`s if no range matches.

State/persistence: long-lived state is per-hub and per-CPU: hub type/revision, MMR/GRU base/shift values, masks, translation tables, GAM ranges, pnode/socket/node IDs, memory node, possible/online CPU counts, NMI hub state, and global `uv_possible_blades`. This metadata is established during UV platform initialization and then treated mostly read-only.

Dependencies/integration: only active for `CONFIG_X86_64`; depends on NUMA, per-CPU, timers, I/O accessors, topology, UV BIOS/MMR definitions, IRQ vectors, and IO-APIC. Integrated with UV memory addressing, GRU, NMI, IRQ routing, CPU/node topology, firmware tables, and platform diagnostics.

Risks/test signals: address translation and MMR access are platform-critical. Wrong masks/shifts/tables can corrupt memory, hit wrong MMRs, or panic via `BUG()`. Test on UV2/UV3/UV4/UV4A/UV5 and hubless variants, GAM table edge ranges, lowmem remap, pnode/socket/node mapping with sub-NUMA clustering, local/global MMR reads, blade CPU counts during hotplug, NMI MMR handling, and non-UV build exclusion.
