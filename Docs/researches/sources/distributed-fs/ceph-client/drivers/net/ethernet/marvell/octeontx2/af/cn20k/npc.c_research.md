# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npc.c

## Purpose
Implements CN20K-specific NPC support for the Marvell RVU Admin Function driver. It programs parser/KPM and MCAM key-extraction profiles, manages CN20K's split MCAM subbank allocator for X2/X4/DYN key widths, translates virtual MCAM indexes used by defragmentable allocations, services CN20K NPC mailbox handlers, installs and frees default steering rules, and initializes/deinitializes global CN20K NPC state.

## Important APIs, Types, and Functions
External entry points include `npc_cn20k_init`, `npc_cn20k_deinit`, `npc_cn20k_parser_profile_init`, `npc_cn20k_load_mkex_profile`, `npc_cn20k_apply_custom_kpu`, `npc_cn20k_ref_idx_alloc`, `npc_cn20k_idx_free`, `npc_cn20k_config_mcam_entry`, `npc_cn20k_enable_mcam_entry`, `npc_cn20k_read_mcam_entry`, `npc_cn20k_copy_mcam_entry`, `npc_cn20k_clear_mcam_entry`, `npc_mcam_idx_2_key_type`, `npc_cn20k_defrag`, `npc_cn20k_dft_rules_alloc`, `npc_cn20k_dft_rules_free`, and `npc_cn20k_subbank_calc_free`. Mailbox-facing handlers cover CN20K MCAM write/read/alloc-and-write, base steering rule read, free count, KEX config, default rule index, profile info, number-of-keywords, and defrag.

The static `npc_priv` owns subbanks, free/used xarrays, PF/function maps, default-rule maps, MCAM-index to virtual-index maps, the defrag show list, and initialization metadata read from hardware. The built-in `npc_mkex_extr_default` profile describes RX/TX key extraction for channel, ltypes, flags, DMAC, VLAN, IP, TOS, TCP, and UDP fields.

## Control Flow
`npc_cn20k_init` calls `npc_priv_init`, reads MCAM/subbank shape from hardware, initializes xarrays/subbanks, builds the pcifunc map, programs all MCAM sections as X2, and marks init complete. Parser setup disables KPM entries and KPUs, loads KPU profile data, programs PKIND and KPM CAM/action entries, enables valid entries, and enables KPUs.

MKEX loading chooses a custom, firmware-database, or default profile, then writes KEX CFG, extractor LID, extractor/ltype, and hash config registers. MCAM writes disable and clear the entry, program CAM0/CAM1 words for X2 or X4 layouts, write action/action2/vtag action and hardware priority, then re-enable if requested. Allocation flows through subbank search helpers; successful allocations update PF ownership maps and optionally allocate stable VIDX handles. Defrag locks MCAM/subbanks, moves VIDX-backed entries into freer subbanks, copies hardware state and hit stats, updates maps and `mcam_rules`, and records old/new/virtual mappings.

## State and Persistence Behavior
Persistent hardware state lives in NPC KPM, PKIND, KEX, MCAM CAM/action/stat/config, and MCAM section-type CSRs. Runtime state persists in global xarrays and subbank bitmaps. Virtual indexes are stable API objects while physical MCAM indexes may change during defrag. Default rule mappings persist per `pcifunc` until freed.

## Dependencies and Integration Points
Depends on xarray, bitmap, mutex, list, field/bit helpers, RVU register I/O, `rvu.h`, `rvu_npc.h`, `rvu_npc_fs.h`, `rvu_npc_hash.h`, `npc_profile.h`, `mbox.h`, `cn20k/npc.h`, and `cn20k/reg.h`. It integrates with common NPC allocation/verification helpers, NIX interface discovery, PF/VF helpers, firmware profile mapping, and mailbox ABI structs.

## Risks
Hardware CSR layout, MCAM key width, allocator metadata, and software maps must stay synchronized. Defrag does not attempt rollback after algorithmic failures. It also does not preserve MCAM counters when moving virtual entries. Xarray rollback paths can leave inconsistent state if rollback fails. Default-rule allocation has TODOs around PF/VF ordering when VF setup precedes PF default rules.

## Test Signals
CN20K probe/init/deinit, default/custom KPU and MKEX loading, invalid profile handling, KEX dumps, X2/X4 MCAM write/read/copy/clear/enable, physical and virtual allocation/free, priority allocation, restricted subbank allocation, VIDX stability through defrag, default PF/VF/LBK rules, invalid mailbox requests, hit-stat preservation across defrag, and concurrency under `mcam->lock`.
