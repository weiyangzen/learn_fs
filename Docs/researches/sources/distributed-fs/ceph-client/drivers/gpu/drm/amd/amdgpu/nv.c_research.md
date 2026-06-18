# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nv.c

## Purpose
`nv.c` is the Navi/common IP block implementation for AMDGPU. It binds ASIC callbacks, video codec capability tables, register-read allowlists, reset method selection, doorbell index assignment, virtualization setup, common early/late/software/hardware init, suspend/resume, clockgating control, and NBIO/HDP/SMUIO integration.

## Important APIs, Types, And Functions
Exports are `nv_common_ip_block`, `nv_grbm_select()`, and `nv_set_virt_ops()`. Important internal surfaces include `nv_query_video_codecs()`, `nv_read_register()`, `nv_asic_reset_method()`, `nv_asic_reset()`, `nv_init_doorbell_index()`, `nv_update_umd_stable_pstate()`, `nv_asic_funcs`, and the `nv_common_ip_funcs` lifecycle table. Codec tables cover Navi, Sienna Cichlid, SR-IOV Sienna Cichlid, Beige Goby, and Yellow Carp.

## Control Flow
`nv_common_early_init()` first calls the already-selected NBIO `set_reg_remap()`, wires indirect PCIe and DIDT register accessors, installs `nv_asic_funcs`, reads revision IDs, and chooses CG/PG flags plus external revision IDs by GC IP version. It initializes SR-IOV settings when needed. Later init gets mailbox IRQs, updates SR-IOV video codec tables, and enables self-ring doorbells. Hardware init applies NBIO workarounds, programs ASPM, initializes NBIO registers, remaps HDP flush registers when allowed, and enables doorbell aperture. Suspend/fini disables doorbell apertures.

## State And Persistence
The file mutates `adev` extensively: ASIC funcs, register accessor tables, revision IDs, CG/PG flags, doorbell indices, virtualization IRQ state, codec tables for SR-IOV, and stable-pstate behavior. All state is runtime kernel/device state.

## Dependencies And Integration Points
It depends on AMDGPU core, atom BIOS, IH, UVD/VCE/VCN/JPEG/GFX/SDMA/HDP/GMC/MMHUB/SMUIO blocks, NBIO version tables, PSP/DPM reset services, PCI reset, SR-IOV mailbox support, and DRM video capability reporting.

## Risks
GC IP switch coverage controls whether the common block probes at all; missing an IP returns `-EINVAL`. Reset method choice depends on MP1 IP and global module parameters. Codec capabilities are table-driven and can diverge between bare metal and SR-IOV. Stable pstate toggles RLC safe mode and ASPM, so ordering matters. The source snapshot shows duplicated code in the SR-IOV codec branch and duplicate MP1 switch case labels, both worth comparing to upstream.

## Test Signals
Signals include successful common IP probe across supported GC IPs, correct external revision IDs, codec query ioctls, reset method logs and recovery, SR-IOV mailbox/video capability updates, KFD/HDP remap, doorbell index correctness, and clockgating flags from NBIO/HDP/SMUIO.
