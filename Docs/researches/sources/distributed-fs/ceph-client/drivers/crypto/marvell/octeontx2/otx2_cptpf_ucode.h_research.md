# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx2/otx2_cptpf_ucode.h

## Purpose
This header defines the firmware, engine, engine-group, bitmap, and mirroring data structures used by the CPT PF microcode manager. It also publishes the PF APIs used by probe, mailbox handlers, devlink, and VF capability services.

## Important APIs and types
Important constants include `OTX2_CPT_MAX_ETYPES_PER_GRP`, `OTX2_CPT_UCODE_SIGN_LEN`, `OTX2_CPT_UCODE_VER_STR_SZ`, `OTX2_CPT_MAX_ENGINES`, and `OTX2_CPT_UCODE_SZ`. Key types are `enum otx2_cpt_ucode_type`, `struct otx2_cpt_bitmap`, `struct otx2_cpt_engines`, `struct otx2_cpt_ucode_hdr`, `struct otx2_cpt_ucode`, `struct otx2_cpt_uc_info_t`, `struct otx2_cpt_engs_available`, `struct otx2_cpt_engs_rsvd`, `struct otx2_cpt_mirror_info`, `struct otx2_cpt_eng_grp_info`, and `struct otx2_cpt_eng_grps`. Public functions include group init/cleanup/create, all-core disable, group lookup, capability discovery, devlink custom create/delete, and engine lookup by type.

## Control flow
There is no executable code, but the structures encode the microcode lifecycle: firmware header parsing feeds `otx2_cpt_ucode`, groups own up to two engine-type reservations and up to two microcodes, groups can mirror another group to reuse microcode, and `otx2_cpt_eng_grps` tracks global availability and reference counts.

## State and persistence
The header models runtime state only. Firmware metadata includes filenames, version strings, DMA addresses, virtual addresses, sizes, and types. Engine reservations persist while the PF is loaded and groups are enabled. Firmware files are external dependencies, not persisted or modified by the driver.

## Dependencies and integration points
It depends on Linux PCI/module/types, hardware type constants, and common CPT definitions. PF main initializes these structures, PF mailbox answers VF group/capability requests from them, and devlink callbacks create/delete groups through the exposed APIs.

## Risks and edge cases
The maximum engine count and bitmap sizing must match hardware limits. `OTX2_CPT_MAX_ETYPES_PER_GRP` allows only two engine types, matching current SE+IE support; adding other combinations requires structural review. Mirroring refcounts must prevent deletion of groups still referenced by other groups.

## Test signals
Compile-time coverage should catch structure/API drift. Runtime signals include successful initialization for discovered engine counts, default group creation, custom devlink group parsing, group deletion with mirror refcount protection, and valid responses to VF engine-group queries.
