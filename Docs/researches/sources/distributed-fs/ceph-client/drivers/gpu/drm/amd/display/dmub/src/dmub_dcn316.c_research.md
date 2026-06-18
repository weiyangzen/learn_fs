# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn316.c

Purpose: instantiates the DCN 3.1.6 DMUB register table by combining DCN31 common register/field macros with DCN316 generated offsets and masks.

Important APIs and control flow: `dmub_srv_dcn316_regs` expands `DMUB_DCN31_REGS()`, `DMCUB_INTERNAL_REGS()`, and `DMUB_DCN31_FIELDS()` using fixed DCN316 segment bases. There are no local hardware callbacks; DCN316 uses the common DCN31 vtable.

State and persistence behavior: no mutable state. The const table persists for the kernel lifetime and supplies register metadata to `dmub_reg.h` macros through `dmub->regs_dcn31`.

Dependencies and integration points: depends on `dcn_3_1_6_offset.h`, `dcn_3_1_6_sh_mask.h`, and the DCN31 common register definition. `dmub_srv_hw_setup()` selects the table for `DMUB_ASIC_DCN316`.

Risks and test signals: risks include generated-register drift, hard-coded segment bases not matching the IP block, and DCN316 later requiring behavior not covered by DCN31 callbacks. Test signals include successful DMUB boot, mailbox and GPINT operation, and diagnostic register reads on DCN316 systems.
