<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_special_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_special_masks.h

## Purpose
`pdma0_core_special_masks.h` defines bit shifts and masks for the PDMA0 core special register block, covering privilege, memory gateway, ECC, and global error fields.

## Important APIs, types, and functions
Exports include `PDMA0_CORE_SPECIAL_GLBL_PRIV_*` masks, memory gateway data/request/address/MID/valid/mask fields, memory count/ECC selection/control/error mask/status/address/RM fields, and global error mask/address/cause fields for APB unmapped read/write, privileged write, and secure write violations. It declares no functions or types.

## Control flow
No code executes. Security and diagnostic code uses these masks to program privilege/security policy, perform memory gateway accesses, configure ECC/error reporting, and decode global APB access violations.

## State and persistence
The masks are stateless. The underlying special registers persist access-control policy, gateway state, ECC status, and global error latches until reset or clear.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this header is the bitfield companion to PDMA special registers included elsewhere in the Gaudi2 generated set. It integrates with `gaudi2_security.c`, PDMA RAS handling, and APB protection diagnostics.

## Risks and test signals
Wrong masks can invert security policy or hide APB violations. Test signals include privileged/secure APB write tests, unmapped access error capture, gateway request completion, ECC/error injection where available, and correct clearing/masking of global error bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_special_masks.h -->
