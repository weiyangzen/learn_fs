# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn314.c

Purpose: instantiates the DCN 3.1.4 DMUB register table using DCN 3.1 common register/field macros with the `dcn_3_1_4_offset.h` and `dcn_3_1_4_sh_mask.h` generated register definitions. It also provides the DCN314-specific PSR-SU firmware capability check.

Important APIs and control flow: `dmub_srv_dcn314_regs` expands `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN31_FIELDS()` into concrete offsets, masks, and shifts using fixed segment base constants. `dmub_dcn314_is_psrsu_supported()` returns true only when `dmub->fw_version >= DMUB_FW_VERSION(8, 0, 16)`.

State and persistence behavior: no mutable software state is stored here. The exported const table is shared by all DCN314 DMUB service instances, while PSR-SU support is derived from the service object's firmware version.

Dependencies and integration points: used by `dmub_srv_hw_setup()` for `DMUB_ASIC_DCN314`, where `dmub->regs_dcn31` is set to `dmub_srv_dcn314_regs` and `is_psrsu_supported` is set to the local function. It depends on the DCN314 generated register headers matching the DCN31 common macro list.

Risks and test signals: risks include incorrect hard-coded segment bases, generated header field renames, and firmware-version policy becoming stale relative to DMUB firmware. Test signals are clean compile for DCN314, correct register offsets in register traces, PSR-SU disabled below 8.0.16 and enabled at or above it, and normal DCN31 reset/mailbox paths working with this table.
