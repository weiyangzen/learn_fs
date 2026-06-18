# sources/distributed-fs/ceph-client/scripts/gcc-plugins/stackleak_plugin.c

Purpose: GCC plugin that tracks deepest kernel stack usage by inserting calls to `__sanitizer_cov_stack_depth()` after dynamic stack allocation and in functions with sufficiently large final stack frames.

Important APIs/functions: `stackleak_start_unit()` declares the tracking function. `stackleak_instrument_execute()` inserts GIMPLE calls or asm calls after `alloca()` and at function entry. `add_stack_tracking_gcall()` updates cgraph edges; `add_stack_tracking_gasm()` uses x86 `current_stack_pointer` and asm when `no_caller_saved_registers` is available. `stackleak_cleanup_execute()` removes unnecessary instrumentation in late RTL for functions without alloca and below `track-min-size`. Gate and plugin init functions parse `track-min-size`, `arch`, `disable`, and `verbose`.

Control flow: An early GIMPLE pass instruments broadly before tree-to-RTL expansion. Later, an RTL pass runs when frame size is known, keeps instrumentation for `cfun->calls_alloca` or large frames, and deletes inserted calls/asm otherwise. Section gating skips init, noinstr, entry, head, and related sections.

State/persistence: Global plugin arguments, x86 flag, verbose/disable flags, and GGC-rooted `track_function_decl`. It mutates GIMPLE, cgraph, and RTL in the compiler process.

Dependencies/integration: GCC plugin internals, generated GIMPLE and RTL pass headers, architecture-provided `current_stack_pointer` for optimized x86 asm path, kernel runtime implementation of `__sanitizer_cov_stack_depth()`.

Risks: Two-pass design is sensitive to pass order. Incorrect removal can leave overhead or remove needed tracking. x86 asm path depends on attributes and symbol availability. Leaf inline/paravirt special cases avoid ABI clobber issues but may need updates.

Test signals: Functions with alloca, large/small static frames, leaf inline special cases, paravirt functions, excluded sections, x86 asm path, non-x86 gcall path, disabled/verbose args, and RTL dumps proving cleanup.
