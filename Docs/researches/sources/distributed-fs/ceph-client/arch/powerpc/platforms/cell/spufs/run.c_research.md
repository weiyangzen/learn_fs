# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/run.c

Purpose: implements the `spu_run` execution loop and interrupt-level stop callback. It starts a context, waits for stop/fault/syscall events, processes recoverable conditions, and returns updated NPC/status/event data to userspace.

Important functions: `spufs_stop_callback`, `spu_stopped`, `spu_setup_isolated`, `spu_run_init`, `spu_process_callback`, `spu_handle_restartsys`, `spu_run_fini`, and exported `spufs_run_spu`.

Control flow: `spufs_run_spu()` serializes with `run_mutex`, acquires the context, enables the SPU, updates scheduler info, initializes run-control, then waits on `stop_wq` until `spu_stopped()` detects halt/stop/single-step/class events. Stop code `0x2104` triggers a syscall callback from SPU local store. Class 1 and class 0 handlers are invoked before deciding whether to continue. Finalization removes from the runqueue, reads status/NPC, clears run flags, logs exit, releases the context, and maps status/signal cases into return values.

State and dependencies: isolated-mode setup loads a device-tree-provided loader through signal registers and temporarily drops problem state. Syscall callbacks depend on `spu_sys_callback`. Risks include subtle restart semantics, signal interruption while needing `state_mutex`, isolated loader timeouts, and local-store pointer validation. Test signals include normal stop/halt returns, SPU syscall restart cases, single-step trap behavior, class fault recovery, and isolate success/failure paths.
