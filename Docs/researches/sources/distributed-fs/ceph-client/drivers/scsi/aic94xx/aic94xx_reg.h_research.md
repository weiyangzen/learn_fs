# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg.h

Purpose: register-access contract and inline helpers for AIC94xx internal memory, PCI BAR sliding windows, DDB/SCB context sites, atomic DDB updates, context sizing, interrupt enable/disable, and DMA address writes.

Important APIs/types/functions: defines internal base addresses, BAR sizes, PCI config offsets, `OCM_BASE_ADDR`, and access prototypes. Macro-generated helpers implement OCM, DDB site, and SCB site byte/word/dword reads/writes. `asd_ddbsite_update_word()` and `_byte()` perform atomic compare/update via hardware atomic registers. `asd_write_reg_addr()` writes 64-bit DMA addresses. `asd_get_cmdctx_size()` and `asd_get_devctx_size()` derive context-memory sizes. `asd_disable_ints()` and `asd_enable_ints()` control interrupt masks.

Control flow: site helpers program `ALTCIOADR` plus `ADDBPTR` or `ASCBPTR`, then access `CTXACCESS`. Byte writes read/modify/write enclosing words. Atomic updates first verify old value, program old/new registers, poll `ATOMICSTATCTL`, and return success, parity error, or retry.

State and persistence: no standalone state, but helpers mutate hardware windows, context memory, interrupt masks, and DDB/SCB sites. `MBAR0_SWB_SIZE` is external state initialized during hardware setup.

Dependencies and integration: includes Linux IO, `aic94xx_hwi.h`, and generated `aic94xx_reg_def.h`. Used across device management, SCB/task/TMF, sequencer setup, interrupt handling, and debug dumps.

Risks and test signals: site access is non-atomic unless callers serialize correctly; byte helpers can race with other word updates. Atomic update polling has no timeout. Interrupt enablement must match ISR expectations. Tests should cover DDB/SCB field access, atomic-update conflict and parity cases, context-size detection, interrupt mask programming, and 32-bit/64-bit DMA address writes.
