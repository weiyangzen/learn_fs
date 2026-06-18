# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/backing_ops.c

Purpose: implements `spu_backing_ops`, the `spu_context_ops` table used while a context is saved and not bound to physical SPU hardware. It makes the saved context save area (`ctx->csa`) behave like SPU problem/privileged registers for filesystem users and scheduler code.

Important functions include mailbox accessors (`spu_backing_mbox_read`, `spu_backing_ibox_read`, `spu_backing_wbox_write`), signal channel accessors, NPC/status/run-control handlers, MFC query helpers, and `spu_backing_restart_dma`. `gen_spu_event()` updates channel event data and count state when mailbox or signal operations create SPU-visible events.

Control flow: operations take `ctx->csa.register_lock`, inspect or mutate collapsed problem-state fields, update mailbox counts, and return byte-count style results matching the hardware ops. `runcntl_write` simulates running/stopped bits in saved status. State is persistent in the allocated CSA and later consumed by `spu_restore()`.

Dependencies: relies on `spu_context_ops` from `spufs.h`, SPU CSA layouts from `asm/spu_csa.h`, and event constants from SPU headers. Risks are semantic mismatch with real hardware, incomplete MFC command support (`send_mfc_command` always reports unavailable), and concurrency around saved register fields. Test signals include mailbox/stat read-write behavior on saved contexts, signal type OR-vs-overwrite semantics, and run-control state transitions before restore.
