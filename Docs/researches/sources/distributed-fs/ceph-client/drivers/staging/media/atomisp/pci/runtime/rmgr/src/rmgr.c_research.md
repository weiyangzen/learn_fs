# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/src/rmgr.c

Purpose: top-level resource-manager lifecycle wrapper.

Important functions: `ia_css_rmgr_init` initializes `vbuf_ref`, then `vbuf_write`, then `hmm_buffer_pool`; on any failure it calls `ia_css_rmgr_uninit`. `ia_css_rmgr_uninit` uninitializes pools in reverse order: HMM buffer, write vbuf, ref vbuf.

Control flow/state: state lives inside the global pools declared in `ia_css_rmgr_vbuf.h`. This file only sequences lifecycle calls and performs rollback.

Dependencies/integration: depends on vbuf pool functions from the resource-manager implementation. Higher-level CSS initialization should call this before using vbuf resources.

Risks: no null checks for global pool pointers are visible here; the pool implementation must tolerate them or callers must initialize globals first. Partial init rollback depends on uninit being safe for not-yet-initialized pools.

Test signals: successful init/uninit ordering, failure injection at each pool init step, idempotent uninit behavior, and resource leak checks after rollback.
