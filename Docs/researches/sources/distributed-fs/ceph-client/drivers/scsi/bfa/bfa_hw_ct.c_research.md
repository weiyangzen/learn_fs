# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_hw_ct.c

## Purpose

`bfa_hw_ct.c` supplies Catapult and Catapult2 ASIC-specific IOCFC interrupt register setup, queue acknowledgement, and MSI-X handler installation. It is the CT/CT2 counterpart to the Crossbow hardware dispatch file and is selected by `bfa_core.c` through `bfa->iocfc.hwif`.

## Important APIs, Types, and Functions

The public hooks are `bfa_hwct_reginit()`, `bfa_hwct2_reginit()`, `bfa_hwct_reqq_ack()`, `bfa_hwct_rspq_ack()`, `bfa_hwct2_rspq_ack()`, `bfa_hwct_msix_getvecs()`, `bfa_hwct_msix_init()`, `bfa_hwct_msix_ctrl_install()`, `bfa_hwct_msix_queue_install()`, `bfa_hwct_msix_uninstall()`, `bfa_hwct_isr_mode_set()`, and `bfa_hwct_msix_get_rme_range()`. The private dummy handler catches spurious or uninstalled MSI-X vectors.

## Control Flow

For CT, register init chooses function-specific `HOSTFN0_*` or `HOSTFN1_*` interrupt registers. For CT2, register init uses `CT2_HOSTFN_INT_STATUS` and `CT2_HOSTFN_INTR_MASK`. CT request queues are acknowledged by read/write of `cpe_q_ctrl`; CT response queues by read/write of `rme_q_ctrl` followed by CI write; CT2 response queues by CI write only.

MSI-X vector discovery reports a contiguous CT vector bitmap and `BFI_MSIX_CT_MAX` vectors. Init accepts one-vector or full-vector mode, stores `nvecs`, and uninstalls handlers. Control install assigns the LPU/error vector to `bfa_msix_all` or `bfa_msix_lpu_err`. Queue install assigns all queue vectors to `bfa_msix_all` in one-vector mode, or splits CPE to `bfa_msix_reqq` and RME to `bfa_msix_rspq` in full-vector mode. ISR mode setting delegates to IOC-level hardware programming.

## State and Persistence Behavior

No persistent storage is used. Runtime state includes interrupt MMIO pointer caches, queue control/CI MMIO writes, cached response queue CI values, MSI-X vector count and handler table, and IOC interrupt mode state.

## Dependencies and Integration Points

The file depends on CT/CT2 register constants, MSI-X vector constants, BFA queue macros, common MSI-X handlers, and `bfa_ioc_isr_mode_set()`. It integrates with `bfa_core.c`, which selects these hooks and overrides some CT behavior for CT2.

## Risks and Edge Cases

CT and CT2 acknowledgement semantics are different; using the wrong hook can lose or repeat interrupts. Invalid vector counts only warn. The vector bitmap assumes `BFI_MSIX_CT_MAX` fits in a 32-bit shift. Handler ranges must match hardware constants. CT2 may have no `hw_isr_mode_set` hook, so callers must tolerate a null callback through the wrapper.

## Test Signals

Validate CT function 0/1 and CT2 register mapping, INTx queue acknowledgement, CT2 CI-only response progress, one-vector and full-vector MSI-X modes, separate request/response/error handlers, uninstall behavior, RME range reporting, and reset/reinit cycles without stale handlers or missed queue interrupts.
