# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/npc.h

## Purpose
Declares the CN20K NPC private interface, constants, parser key extraction macros, subbank metadata, custom KPU/MKEX profile formats, and public functions implemented by `cn20k/npc.c`.

## Important APIs, Types, and Functions
Important constants include `MKEX_CN20K_SIGN`, `MAX_NUM_BANKS`, `MAX_NUM_SUB_BANKS`, `MAX_SUBBANK_DEPTH`, `MKEX_END_SIGN`, parse nibble masks, `NPC_CN20K_PARSE_NIBBLE_INTF_RX`, `NPC_CN20K_PARSE_NIBBLE_INTF_TX`, and `NPC_MAX_EXTRACTOR`. Types include `enum npc_subbank_flag`, `enum npc_dft_rule_id`, `struct npc_subbank`, `struct npc_defrag_show_node`, `struct npc_priv_t`, `struct npc_kpm_action0`, `struct npc_mcam_kex_extr`, and `struct npc_cn20k_kpu_profile_fwdata`. Prototypes cover initialization, parser profile programming, custom KPU application, MCAM allocation/free, MCAM entry manipulation, default rules, VIDX translation, defrag, and CGX/LBK eligibility checks.

## Control Flow
The header has no standalone runtime flow. It shapes `npc.c` behavior by defining subbank state flags, default-rule IDs, firmware profile layouts, and the public calls used by generic RVU/NPC code and mailbox handlers.

## State and Persistence Behavior
`struct npc_priv_t` describes long-lived state mirrored from hardware: bank/subbank dimensions, key width, subbank array, PF/function maps, virtual index maps, and defrag list. `struct npc_mcam_kex_extr` and `struct npc_cn20k_kpu_profile_fwdata` are persistent firmware/profile ABI formats with signatures, versions, packed layout, and fixed dimensions.

## Dependencies and Integration Points
Depends on generic RVU/NPC definitions for `struct rvu`, KPU profiles, LTYPE definitions, CN20K MCAM entries, interface IDs, KEX dimensions, and register I/O. It integrates with `cn20k/reg.h` and `mbox.h`.

## Risks
This is hardware and firmware ABI. Changing bitfields, packed profile structs, parse masks, or extractor/subbank limits can silently break parser programming. `CN20K_SET_EXTR_LT` is defined twice with the same body. Several macros assume caller-local names such as `rvu` and `BLKADDR_NPC`.

## Test Signals
CN20K build coverage, profile signature/version validation, KEX dump matching extractor arrays, packed-layout size checks, maximum-depth subbank allocation, default rule ID map round trips, VIDX translation before/after init, and endian/bitfield sanity for `npc_kpm_action0`.
