# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_ucode.c

## Purpose
This file manages CPT microcode firmware and engine-group allocation for the PF. It loads firmware, validates revision/type, copies microcode to DMA memory, reserves engine cores, supports mirrored groups, enables/disables cores, discovers hardware capabilities through LOAD_FVC, and implements devlink custom engine-group create/delete operations.

## Important APIs and functions
Public APIs include `otx2_cpt_init_eng_grps()`, `otx2_cpt_cleanup_eng_grps()`, `otx2_cpt_create_eng_grps()`, `otx2_cpt_disable_all_cores()`, `otx2_cpt_get_eng_grp()`, `otx2_cpt_discover_eng_capabilities()`, `otx2_cpt_dl_custom_egrp_create()`, `otx2_cpt_dl_custom_egrp_delete()`, and `find_engines_by_type()`. Internal areas cover firmware load (`load_fw()`, `cpt_ucode_load_fw()`), engine reservation (`reserve_engines()`, `eng_grp_update_masks()`), group lifecycle (`create_engine_group()`, `delete_engine_group()`), mirroring, and core attach/disable paths.

## Control flow
Default group creation loads AE/SE/IE firmware matching `rid`, creates an SE group for symmetric crypto, an SE+IE group for IPsec, and an AE group for asymmetric crypto, then applies CN10K errata and context prefetch/RNM settings. Group creation copies firmware into coherent DMA memory, optionally mirrors an existing group with matching microcode, reserves engine counts, builds bitmaps, writes UCODE_BASE for unused engines, attaches cores to group masks, and enables cores. Deletion disables cores, unloads microcode, clears UCODE_BASE, releases engine counts, and removes mirror references.

## State and persistence
Engine state is held in `struct otx2_cpt_eng_grps`: availability counters, per-group engine reservations, bitmaps, microcode metadata, mirror references, and engine refcounts. Firmware images are requested from `/lib/firmware` through the kernel firmware API and copied into DMA memory for the hardware; no driver-managed disk persistence exists.

## Dependencies and integration points
The file depends on firmware loading, DMA coherent allocation, AF register mailbox helpers, LF init/request submission for capability discovery, RVU registers, and PF device state. VF capability responses and engine group number queries depend on state created here.

## Risks and edge cases
Firmware validation is strict on revision-prefixed version strings and microcode type. Engine refcounts and bitmaps must stay consistent across mirrored groups and dual CPT0/CPT1 programming. Capability discovery temporarily creates groups and an LF, sends LOAD_FVC commands, polls completion, and then deletes groups; failure must clean every resource. Devlink custom group changes are denied while VFs are enabled, reducing live reconfiguration risk.

## Test signals
Signals include firmware load success/failure by missing or mismatched files, default group layout, devlink create/delete parsing and rejection cases, VF capability discovery values, dual-block CPT1 programming, RNM/errata register writes on CN10K, and cleanup with no DMA or bitmap leaks.
