# File Research: sources/cow-pools/bcachefs-tools/include/linux/completion.h

This header declares a small completion primitive compatible with the Linux API. `struct completion` contains a `done` counter and wait queue head.

It provides declaration and initialization macros/functions: `DECLARE_COMPLETION`, `DECLARE_COMPLETION_ONSTACK`, `init_completion()`, and `reinit_completion()`. The actual completion operations are declared externally: `complete()`, `wait_for_completion()`, and `wait_for_completion_timeout()`.

`wait_for_completion_interruptible()` is reduced to a non-interruptible wait followed by success return, reflecting the simplified user-space shim.
