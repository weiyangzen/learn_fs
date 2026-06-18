# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_cfg_special_regs.h

Purpose: generated special access-control/security register map for `DCORE0_TPC0_CFG_SPECIAL`. It exports 81 `mmDCORE0_TPC0_CFG_SPECIAL_*` constants from `0x400BE80` to `0x400BFFC`.

Important APIs/types/functions: macro-only API. The file defines global privilege registers `GLBL_PRIV_0..31`, global non-secure registers `GLBL_NON_SEC_0..15`, and global secure registers `GLBL_SEC_0..31` for the TPC CFG special window.

Control flow: none. External security initialization or debug code programs/reads these policy registers to control access attributes for TPC CFG register regions.

State and persistence behavior: names persistent hardware policy state controlling privilege/security metadata. Changes may affect which agents can access TPC CFG resources until reset or reconfiguration.

Dependencies and integration points: included by `gaudi2_regs.h` and aligned with block-base definitions in `gaudi2_blocks_linux_driver.h`. It complements the main TPC CFG and AXUSER maps and is relevant to `gaudi2_security.c` access-region configuration.

Risks: security register maps are high impact. Incorrect generation or programming can expose privileged TPC registers, block legitimate driver access, or create mismatched secure/non-secure views.

Test signals: generated map validation, security-table tests, privilege boundary tests, boot-time access checks under secure/non-secure modes, and review that special register windows remain restricted.
