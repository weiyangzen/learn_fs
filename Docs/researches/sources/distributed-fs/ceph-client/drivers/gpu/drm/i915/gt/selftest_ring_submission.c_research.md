# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_ring_submission.c Research

Purpose: this live suite tests legacy ring-submission inter-context workaround batch behavior. It ensures the workaround batch runs when switching between user contexts, but not for kernel context or repeated same-user-context execution.

Important APIs/types/functions: `create_wally()` creates and pins a batch VMA that writes `STACK_MAGIC` near offset 4000 and stores a dummy context in `vma->private`. `context_sync()`, `new_context_sync()`, `mixed_contexts_sync()`, `double_context_sync_00()`, and `kernel_context_sync_00()` create request sequences and inspect the marker. `__live_ctx_switch_wa()` temporarily installs the custom batch at `engine->wa_ctx.vma`.

Control flow: `live_ctx_switch_wa()` runs only for legacy ring submission (`submission_method <= INTEL_SUBMISSION_RING`) and skips engines without store-dword support or Gen4/5 privileged store issues. For each engine it saves and clears the existing WA context VMA, installs the marker batch, synchronizes kernel and user contexts in specific patterns, validates marker writes, then restores the original VMA after flushing.

State and persistence: it temporarily mutates `engine->wa_ctx.vma`, creates user contexts, pins a high user VMA, maps the batch WC, and releases the dummy context plus VMA map during cleanup. The mutation is restored even on the normal error path after `__live_ctx_switch_wa()`.

Dependencies/integration: it depends on legacy ring submission code, context switching, WA batch plumbing, GEM internal objects, VM pinning/sync, engine PM, and `igt_flush_test()`.

Risks and test signals: incorrect WA execution can leak user-visible state or skip required workarounds. Pass signals are zero marker for kernel-context execution, `STACK_MAGIC` after user context switches, zero marker for repeated same context, and clean flush. The test is intentionally not used for execlists/GuC submission.
