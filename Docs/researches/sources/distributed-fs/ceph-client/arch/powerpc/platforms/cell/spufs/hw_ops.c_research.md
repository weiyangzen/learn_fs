# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/hw_ops.c

Purpose: implements `spu_hw_ops`, the `spu_context_ops` table used when a context is bound to physical SPU hardware. It translates spufs file operations into MMIO reads/writes of SPU problem, priv1, and priv2 registers.

Important functions: hardware mailbox read/status/poll and write helpers, signal notify and signal type accessors, NPC/status/local-store getters, run-control and master-control operations, MFC query/tag/free-element access, MFC command issue, and DMA restart.

Control flow: register accesses use big-endian MMIO helpers and often take `spu->register_lock` with interrupts disabled. Poll helpers either return readiness or enable class 2 interrupts and clear stale status. `runcntl_write` enables isolated load requests before setting isolate run-control. `send_mfc_command` writes LSA/EA/size/tag/class/cmd and decodes command status into `0`, `-EAGAIN`, or `-EINVAL`.

State and dependencies: depends on `ctx->spu` being valid and associated by the scheduler; callbacks in `sched.c` bind `ctx->ops` to this table. Risks are missing locking on simple reads, busy-waiting in `runcntl_stop`, interrupt-mask side effects during poll, and exact hardware status decoding. Test signals include mailbox interrupt readiness, MFC queue full behavior, isolate startup, DMA restart suppression during context switch, and parity with `backing_ops` for saved contexts.
