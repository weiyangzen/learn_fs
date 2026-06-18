# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_vdec0_ctrl_special_regs.h

Purpose: generated special privilege/security register map for the VDEC0 control block. It exports 81 `mmDCORE0_VDEC0_CTRL_SPECIAL_*` constants from `0x41E4E80` to `0x41E4FFC`.

Important APIs/types/functions: macro-only API with `GLBL_PRIV_0..31`, `GLBL_NON_SEC_0..15`, and `GLBL_SEC_0..31` registers for VDEC0 control special access metadata.

Control flow: none. Security initialization and low-level access-control code use these registers to configure privileged, secure, and non-secure views of the VDEC control block.

State and persistence behavior: persistent hardware access policy state. Values remain active until reset/reconfiguration and affect which agents may access VDEC control registers.

Dependencies and integration points: included by `gaudi2_regs.h`; aligned with VDEC bridge control and AXUSER maps. It should correspond to special block ranges in `gaudi2_blocks_linux_driver.h` and access policy code.

Risks: wrong special-register programming can expose protected video decode controls or block legitimate driver access. Generated repetition across special files makes address-base mistakes easy to miss.

Test signals: secure/non-secure access tests, boot-time access policy validation, generated map diff review, and negative tests for forbidden VDEC control writes.
