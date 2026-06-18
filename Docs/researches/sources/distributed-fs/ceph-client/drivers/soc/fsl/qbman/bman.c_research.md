# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman.c

Purpose: DPAA1 BMan high-level portal and buffer-pool API. It implements per-CPU affine portals, release command ring handling, management-command acquire/query mechanics, portal IRQ handling, BPID allocation, and exported pool acquire/release functions.

Important APIs and functions: exported APIs include `bman_create_affine_portal()`, `bman_p_irqsource_add()`, `bm_shutdown_pool()`, `bman_new_pool()`, `bman_free_pool()`, `bman_get_bpid()`, `bman_release()`, `bman_acquire()`, and `bman_get_bm_portal_config()`. Internal subsystems include RCR helpers (`bm_rcr_init()`, `bm_rcr_start()`, `bm_rcr_pvb_commit()`), management command helpers (`bm_mc_start()`, `bm_mc_commit()`, `bm_mc_result_timeout()`), and portal setup `bman_create_portal()`.

Control flow: portal creation maps config addresses into `bm_portal`, initializes RCR and management command state, disables BSCN interrupts, clears stale interrupts, requests IRQ, sets affinity, verifies the RCR is clean, and enables interrupts. `bman_release()` waits for an RCR entry, fills buffers and BPID, commits with valid bit, and uses the affine portal for the current CPU. `bman_acquire()` issues an MC acquire command and copies returned buffers.

State and persistence: per-CPU `bman_affine_portal`, `affine_mask`, portal RCR/MC rings, IRQ source masks, and global `bm_bpalloc` persist. Hardware portal rings and BMan pools carry persistent buffer state.

Dependencies and integration: depends on `bman_priv.h`, `dpaa_sys.h`, DPAA cache helpers, genalloc BPID pool from `bman_ccsr.c`, and portal configs from `bman_portal.c`.

Risks and test signals: risks include CPU-affine assumptions, local IRQ/preemption interactions around `get_cpu_var()`, RCR timeout under pressure, copying `num` buffers instead of returned count in acquire callers, and cleanup loops on kexec. Test signals are BMan self-test pass, buffer pool leak cleanup, IRQ affinity behavior, and stress release/acquire across CPUs.
