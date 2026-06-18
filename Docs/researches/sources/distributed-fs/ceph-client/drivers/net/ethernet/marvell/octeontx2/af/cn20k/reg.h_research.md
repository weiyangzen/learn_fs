# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/cn20k/reg.h

## Purpose
Defines CN20K-specific RVU mailbox and NPC register offsets used by AF, PF, VF, and NPC programming paths.

## Important APIs, Types, and Functions
This macro-only header defines RVUM discovery CSRs, AF/PF/VF mailbox address/config/trigger/interrupt registers, BAR2 selection registers, NIX interrupt helper offsets, CN20K mailbox interrupt bits, NPC extractor/KPM/KPU offsets, MCAM section config, CN20K extended MCAM CAM word/action/config/stat offsets, and miss-action offsets. Key macro families are `RVU_MBOX_AF_*`, `RVU_MBOX_PF_*`, `RVU_MBOX_VF_*`, `NPC_AF_INTFX_EXTRACTORX_CFG`, `NPC_AF_INTFX_EXTRACTORX_LTX_CFG`, `NPC_AF_KPMX_ENTRYX_*`, `NPC_AF_MCAM_SECTIONX_CFG_EXT`, and `NPC_AF_CN20K_MCAMEX_BANKX_*_EXT`.

## Control Flow
No runtime flow is present. These offsets drive `mbox.c` direction-specific doorbells and `npc.c` parser, MCAM, action, priority, and statistic register access.

## State and Persistence Behavior
Each macro addresses persistent hardware state. Mailbox offsets control shared-memory doorbells and interrupt state. NPC offsets address parser and MCAM tables that remain until reset or reprogramming.

## Dependencies and Integration Points
Includes `../rvu.h` and `../rvu_reg.h`. It integrates with `rvu_read64`, `rvu_write64`, `readq`, `writeq`, CN20K mailbox setup, and CN20K MCAM X2/X4 bank layout code.

## Risks
Register arithmetic errors compile cleanly but write the wrong hardware location. The header contains a duplicate `RVU_MBOX_AF_VFAF_INT_ENA_W1C` macro and likely typo-named `RVU_MBOX_AF_VFAF1_IN_ENA_*` macros. Statement-expression macros are kernel/GNU C specific, and callers should pass side-effect-free arguments.

## Test Signals
CN20K probe, AF/PF/VF down and up mailbox traffic, mailbox interrupts, NPC parser programming, MCAM write/read/copy/stat, default rule install, FLR interrupt handling, and register dump comparison against hardware documentation.
