# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/dal_asic_id.h

Purpose: centralizes AMD display ASIC family, revision, and device ID constants plus revision-classification macros used across the display driver.

Important APIs and control flow: defines internal revision IDs and predicates for SI, CI, KV/Kabini/Bhavani/Godavari, VI/Polaris/Vegam, CZ/Stoney, AI/Vega, Raven/Raven2/Picasso/Renoir, Navi/Green Sardine, Vangogh, Yellow Carp, GC 10.3.x, GC 11.x, DCN36, GC 12/DCN4/DCN401, and selected device IDs. It also defines family IDs such as `FAMILY_SI`, `FAMILY_NV`, `FAMILY_YELLOW_CARP`, and `AMDGPU_FAMILY_GC_*`.

State and persistence behavior: no runtime state. These macros are compile-time classification logic over chip revision/device/family values discovered elsewhere.

Dependencies and integration points: standalone header used by display capability, resource, and ASIC-specific initialization code to select DCN/DCE paths, workarounds, and feature gates.

Risks and test signals: risks include overlapping revision ranges, duplicated constants such as `AI_UNKNOWN`, macros without parentheses around all arguments in older patterns, stale device IDs, and new ASIC revisions falling into broad predicates unintentionally. Test signals include ASIC detection unit checks over boundary revision values, correct resource selection for DCN36/DCN4/DCN401, and boot logs identifying expected family/revision for supported GPUs.
