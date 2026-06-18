# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_ccsr.c

Purpose: DPAA1 BMan CCSR hardware initialization and error interrupt handling. It maps the global BMan block, detects revision, configures private FBPR memory, seeds BPID allocation, and exposes probe/cleanup status to portal code.

Important APIs and functions: global `bman_ip_rev` is exported. `fsl_bman_probe()` is the built-in platform probe. `bm_set_memory()` programs FBPR base/size or detects preconfigured memory after kexec. `bman_isr()` reports hardware errors and disables one-shot low-watermark interrupts. `bman_is_probed()`, `bman_requires_cleanup()`, and `bman_done_cleanup()` coordinate portal probing and kexec cleanup.

Control flow: probe maps CCSR, reads IP revision, initializes reserved private memory through `qbman_init_private_mem()`, writes FBPR registers, installs shared error IRQ, disables BSCN error interrupt, clears stale errors, enables error interrupts, creates `bm_bpalloc`, seeds BPID range, and marks BMan probed.

State and persistence: persistent globals include `bm_ccsr_start`, `bman_ip_rev`, probe and cleanup flags, `fbpr_a/fbpr_sz`, and `bm_bpalloc`. Hardware FBPR register contents can persist across kexec and are treated specially.

Dependencies and integration: depends on OF platform resources, reserved memory helper in `dpaa_sys.c`, genalloc, BMan portal cleanup in `bman_portal.c`, and `bman.c` BPID allocation.

Risks and test signals: risks include inability to change FBPR base after prior firmware/kernel setup, revision table gaps, error IRQ flood except disabled FLWI, and private memory without `struct page` DMA mapping. Test signals are BMan probe success, BPID pool size matching revision, error interrupt logs, kexec cleanup path, and `bman_is_probed()` unblocking portals.
