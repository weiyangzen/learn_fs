# sources/distributed-fs/ceph-client/arch/x86/lib/copy_mc.c

Purpose: implements C dispatch for machine-check-tolerant memory copy operations, choosing fragile byte/word-safe copying, enhanced fast-string copying, or ordinary copy depending on platform capability and MCE quirks.

Important APIs/functions: `enable_copy_mc_fragile()` enables a static key under `CONFIG_X86_MCE`. `copy_mc_fragile_handle_tail()` probes byte-by-byte after write faults. `copy_mc_to_kernel()` and `copy_mc_to_user()` are the main exported/called APIs. Assembly backends `copy_mc_fragile` and `copy_mc_enhanced_fast_string` are declared here.

Control flow: if fragile mode is enabled, copies are instrumented and routed through `copy_mc_fragile`. Otherwise ERMS-capable CPUs use `copy_mc_enhanced_fast_string`. Kernel destination fallback is plain `memcpy`; user destination fallback is `copy_user_generic`. User copies bracket machine-check copy with `__uaccess_begin/end`.

State and persistence behavior: only static key state persists after `enable_copy_mc_fragile`. Copies modify destination memory and return remaining byte count on exception. Instrumentation hooks notify sanitizers/tracing about copy ranges.

Dependencies/integration points: depends on MCE support, x86 feature detection, uaccess, instrumentation hooks, and assembly routines in `copy_mc_64.S`. Used by memory error recovery, persistent memory, and usercopy paths that may encounter poisoned memory.

Risks: choosing fast-string on CPUs that cannot recover from machine checks could be fatal; platform quirks must call `enable_copy_mc_fragile()`. User access windows must be balanced. Return values must be honored by callers to avoid treating partial copies as complete.

Test signals: MCE/poison injection tests, ERMS and non-ERMS CPU coverage, fragile static-key path tests, usercopy fault injection, and sanitizer instrumentation checks.
