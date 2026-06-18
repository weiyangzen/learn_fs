# sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_ucode.h Research

## sources/distributed-fs/ceph-client/drivers/crypto/marvell/octeontx/otx_cptpf_ucode.h

### Purpose
`otx_cptpf_ucode.h` defines the microcode, engine, engine-group, mirroring, and availability data model used by the OcteonTX CPT PF microcode manager.

### Important APIs, Types, And Functions
Important constants include microcode name, tar name, alignment, signature length, version string size, max engines, engine bitmap length, and `OTX_CPT_MAX_ETYPES_PER_GRP`. Important types are `enum otx_cpt_ucode_type`, `struct otx_cpt_bitmap`, `struct otx_cpt_engines`, `struct otx_cpt_ucode_ver_num`, `struct otx_cpt_ucode_hdr`, `struct otx_cpt_ucode`, `struct tar_ucode_info_t`, `struct otx_cpt_engs_available`, `struct otx_cpt_engs_rsvd`, `struct otx_cpt_mirror_info`, `struct otx_cpt_eng_grp_info`, and `struct otx_cpt_eng_grps`. It declares PF-facing lifecycle and query functions.

### Control Flow, State, And Persistence
The structures persist all PF engine-group state across SR-IOV enablement: available SE/AE counts, per-engine reference counts, per-group reserved bitmaps, microcode DMA addresses, sysfs attributes, mirror relationships, lock, read-only flag, and default-creation cursor. `struct otx_cpt_ucode_hdr` mirrors firmware image headers and is used to validate and classify loaded microcode.

### Dependencies, Integration Points, Risks, And Test Signals
The header depends on PCI, module, and OcteonTX hardware type definitions. Risks include fixed limits mismatching hardware capabilities, one-engine-type-per-group assumptions, bitmap sizing, and exposing internal structs to PF code that must respect the mutex. Test signals include compile coverage, default group creation with max engine counts, engine bitmap bounds, firmware header parsing, group info sysfs output, and PF mailbox `otx_cpt_uc_supports_eng_type()` decisions.
