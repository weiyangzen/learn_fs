## sources/distributed-fs/beegfs/client_module/source/os/OsDeps.c

**Purpose:** Provides debug-only operating-system dependent stack trace helpers for the BeeGFS kernel client.

**Important APIs/types/functions:** Under `BEEGFS_DEBUG`, defines `os_saveStackTrace`, `os_freeStackTrace`, and `os_printStackTrace`. When stacktrace support or compatible architecture support is missing, stubs return NULL or print a support warning.

**Control flow:** On supported debug kernels, `os_saveStackTrace` allocates a `struct stack_trace` plus entries array with `GFP_NOFS`, skips its own frame, and calls `save_stack_trace`. The print helper selects `print_stack_trace` or `stack_trace_print` based on feature macros. Free releases both allocations.

**State and persistence behavior:** Stack traces are transient heap allocations owned by callers. No persistent state is stored.

**Dependencies and integration points:** Used by debug code such as `NoAllocBufferStore` to record which task acquired a buffer and diagnose recursive/deadlocking buffer-store use.

**Risks:** The implementation is disabled for `CONFIG_ARCH_STACKWALK` because newer stack walking APIs differ; debug diagnostics may silently degrade. Allocation failures return NULL and callers must tolerate missing traces. These helpers are debug-only and should not be relied on for production behavior.

**Test signals:** Build debug and non-debug configurations, with and without `CONFIG_STACKTRACE` and `CONFIG_ARCH_STACKWALK`; verify saved traces are printed and freed by buffer-store debug paths.
