# sources/distributed-fs/ceph-client/arch/arm64/lib/kasan_sw_tags.S

Purpose: implements the low-level SW tag KASAN mismatch thunk that adapts the compiler's non-AAPCS call frame into a normal call to `kasan_tag_mismatch`.

Important APIs/types/functions: `__hwasan_tag_mismatch`, `bti c`, register save/restore block, call to `kasan_tag_mismatch`, and exported symbol.

Control flow: the compiler-generated thunk enters with a 256-byte stack object and nonstandard preserved registers. The routine creates a frame record, saves x2-x15 and optionally x18, passes x0/x1 plus the call site in x2 to `kasan_tag_mismatch`, restores all expected registers and frame values, drops the 256-byte object, and returns.

State and persistence: mutates only the temporary trap stack frame and calls KASAN reporting. No persistent state except whatever the KASAN report path records.

Dependencies/integration: built with `CONFIG_KASAN_SW_TAGS`; depends on compiler HWASAN ABI expectations, shadow call stack configuration, BTI, and KASAN runtime.

Risks: register or stack layout mismatch corrupts the interrupted function. Shadow call stack handling of x18 must remain consistent with config. The calling convention is compiler-specific and fragile.

Test signals: SW-tag KASAN mismatch tests, stack unwinding through the thunk, shadow-call-stack config builds, BTI-enabled execution, and register preservation checks.
