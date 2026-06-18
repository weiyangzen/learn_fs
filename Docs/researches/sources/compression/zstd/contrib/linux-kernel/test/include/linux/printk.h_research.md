# sources/compression/zstd/contrib/linux-kernel/test/include/linux/printk.h

Purpose: minimal logging shim for generated kernel-zstd code compiled in user space.

Important behavior: defines `pr_debug(...)` as a no-op.

State, dependencies, and integration: no state and no includes. It satisfies kernel logging calls without producing output during tests.

Risks and test signals: debug messages are suppressed, so diagnostics differ from kernel builds. If generated code requires other printk levels, compilation will fail and prompt shim expansion.
