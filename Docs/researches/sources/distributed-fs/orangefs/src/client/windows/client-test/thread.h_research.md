# sources/distributed-fs/orangefs/src/client/windows/client-test/thread.h

Purpose: Declares Win32-only thread wait helpers and constants for the client-test code.

Important APIs/types: Defines `THREAD_WAIT_SIGNALED`, `THREAD_WAIT_TIMEOUT`, and `THREAD_WAIT_INFINITE`, then declares `thread_wait()`, `thread_wait_multiple()`, and `get_thread_exit_code()`. The thread creation prototype is commented out.

Control flow: No implementation, but consumers rely on these constants matching Win32 `WAIT_*` values.

State/persistence: None.

Dependencies/integration: The declarations are guarded by `#ifdef WIN32`; non-Windows consumers see only the include guard. The prototypes use `uintptr_t`, so callers must include a header that defines it before or through this header.

Risks: Missing explicit `<stdint.h>`/`<stdint>` include for `uintptr_t`. The disabled `thread_create()` API means callers must obtain handles by some other means.

Test signals: Compile Windows client tests with strict include ordering to ensure `uintptr_t` is available, and validate constants against Win32 wait return values.
