# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/interface/ia_css_rmgr_vbuf.h

Purpose: declares virtual-buffer resource handles, pools, global pools, and refcounted acquire/release APIs.

Important types/APIs: `ia_css_rmgr_vbuf_handle` with HMM pointer, refcount, and size; `ia_css_rmgr_vbuf_pool` with copy-on-write/recycle flags, size/index, and handle table; global pools `vbuf_ref`, `vbuf_write`, and `hmm_buffer_pool`; pool init/uninit/acq/rel and refcount retain/release functions.

Control flow/state: implementation is elsewhere, but the model supports reusable vbuf handles with reference counts and pool-level policies.

Dependencies/integration: included by top-level `ia_css_rmgr.h`, depends on CSS types and `ia_css_ptr`. `rmgr.c` initializes/uninitializes all three global pools.

Risks: `u8 count` can overflow if retain/release discipline breaks. Global pool pointers must be initialized before `ia_css_rmgr_init` and remain valid through uninit.

Test signals: pool init/uninit, acquire/release recycle behavior, refcount retain/release including final free, copy-on-write policy, and error handling for null handles.
