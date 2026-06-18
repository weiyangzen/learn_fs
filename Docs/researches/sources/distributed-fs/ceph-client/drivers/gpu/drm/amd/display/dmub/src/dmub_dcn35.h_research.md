# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn35.h

Purpose: declares the DCN35 register layout and hardware API. It extends DCN32-style DMUB control with `DMU_CLK_CNTL` and LONO clock-gate-disable fields used during reset release.

Important APIs and control flow: `DMUB_DCN35_REGS()` includes DMCUB control, mailbox, region3/4/5/6, scratch0-21, GPINT, support, FB base/offset, fault, TMR AXI-space, interrupts, and `DMU_CLK_CNTL`. `DMUB_DCN35_FIELDS()` supplies masks/shifts for enable/reset, window top/enable fields, support, FB fields, GPINT interrupt, PWAIT, and the three LONO gate-disable bits. Declared callbacks cover all DCN32-like operations plus `get_fw_boot_option()`, `should_detect()`, `is_hw_powered_up()`, `get_preos_fw_info()`, and register-offset initialization.

State and persistence behavior: no local state; the mutable `struct dmub_srv_dcn35_regs` is filled per ASIC/revision. Runtime state persists in DMCUB registers and DMUB service fields.

Dependencies and integration points: includes `dmub_dcn31.h`; implemented by `dmub_dcn35.c` and reused by DCN351/DCN36 register initializers. `dmub_srv.c` binds this API for DCN35/DCN351/DCN36.

Risks and test signals: risks include field-list drift across DCN35, DCN351, and DCN36 generated headers, scratch count differences from DCN32, and register table initialization ordering. Test signals include compile coverage for all three revisions and boot/reset traces showing `DMU_CLK_CNTL` updates and working region6/pre-OS paths.
