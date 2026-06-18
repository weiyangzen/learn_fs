<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/fwsec.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/fwsec.c

## Purpose
Builds, patches, boots, and verifies FWSEC Falcon microcode used for secure boot and FRTS setup before or during GSP operation.

## Important APIs, Types, And Functions
Defines firmware interface descriptor unions, DMEM mapper structures, `nvfw_fwsec_frts_cmd`, `nvkm_gsp_fwsec_patch`, `nvkm_gsp_fwsec_v2`, `nvkm_gsp_fwsec_v3`, `nvkm_gsp_fwsec_init`, `nvkm_gsp_fwsec_boot`, `nvkm_gsp_fwsec_sb`, `nvkm_gsp_fwsec_sb_init`, and `nvkm_gsp_fwsec_frts`.

## Control Flow
The init path searches VBIOS PMU entries for FWSEC ucode type `0x85`, reads descriptor version, constructs Falcon firmware from embedded VBIOS data, patches bootloader/signature data depending on descriptor version, sets the DMEM mapper command, and writes read-VBIOS/FRTS command data. Boot calls `nvkm_falcon_fw_boot`; secure-boot and FRTS variants then check mailbox/error registers and log WPR2 ranges for FRTS.

## State And Persistence
It populates temporary or persistent `struct nvkm_falcon_fw` objects, patches firmware image memory, reads BIOS data, and uses GSP `fb.wpr2.frts` state. The FRTS temporary firmware is destroyed after use.

## Dependencies And Integration Points
Depends on VBIOS PMU parsing, `nvfw` blob helpers, Falcon firmware constructors/signing/boot, BIOS signature lookup, and GSP function-table FWSEC hooks.

## Risks And Edge Cases
Descriptor version mismatch, absent DMEM mapper app interface, signature selection failure, or FWSEC mailbox error aborts boot. The code uses `WARN_ON` for malformed firmware structures.

## Test Signals
Successful `fwsec-sb` and `fwsec-frts` boot, zero error mailboxes, and debug output for WPR2 FRTS range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/gsp/fwsec.c -->
