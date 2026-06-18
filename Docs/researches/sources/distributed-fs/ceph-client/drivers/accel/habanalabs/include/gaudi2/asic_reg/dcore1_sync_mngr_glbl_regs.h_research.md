# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore1_sync_mngr_glbl_regs.h

Purpose: generated global sync-manager register map for DCORE1 using the SOB_GLBL prototype. It exports 590 `mmDCORE1_SYNC_MNGR_GLBL_*` constants from `0x431E000` to `0x431E94C`.

Important APIs/types/functions: macro-only API for sync-manager interrupt mask/cause, local-to-host completion masks, ASID security/privilege controls, LBW delay, PI size/mode, SOB-only and CQ interrupt controls, 64 completion queue base address low/high entries, 64 CQ size-log2 entries, 64 CQ producer indices, 64 CQ security entries, 64 CQ privilege entries, 64 CQ ASID entries, 64 CQ message address/data entries, CQ increment modes, and related per-CQ global configuration.

Control flow: none in this header. Runtime synchronization code configures completion queues, security/ASID policy, producer indices, message targets, and interrupt controls for sync objects and completions.

State and persistence behavior: maps persistent global synchronization state for DCORE1. CQ base/size/PI/security/ASID/message registers define how hardware completions are written and how sync-manager events are delivered. State persists until reset or reconfiguration.

Dependencies and integration points: included by `gaudi2_regs.h`; base/section metadata in `gaudi2_blocks_linux_driver.h`. It integrates with queue managers, sync-object programming, host completion mechanisms, and security policy around ASID/privileged access.

Risks: large repeated CQ arrays are vulnerable to index/address drift. Misprogrammed completion queues can write to wrong host/device memory, violate security, or deadlock waits. ASID/security/privilege fields are isolation-critical.

Test signals: completion queue setup tests for low and high indices, sync-object completion tests, ASID/privilege negative tests, interrupt cause/mask tests, generated array stride validation, and hardware readback of representative CQ entries.
