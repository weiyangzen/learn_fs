# sources/distributed-fs/ceph-client/include/linux/delayed_call.h

Purpose: Provides a tiny closure-like helper for storing a callback and argument to execute later.

Important APIs, types, and functions: Defines `struct delayed_call`, `DEFINE_DELAYED_CALL(name)`, `set_delayed_call()`, `do_delayed_call()`, and `clear_delayed_call()`.

Control flow: A caller initializes or defines a `delayed_call`, stores a function and argument with `set_delayed_call()`, and later invokes it with `do_delayed_call()` if a function is present. `clear_delayed_call()` disables future invocation without touching the argument.

State and persistence: State is just the callback pointer and opaque argument stored in caller-owned memory. There is no synchronization or ownership management.

Dependencies and integration points: Used by VFS-style interfaces that need to return cleanup actions or deferred release functions without a full object. It has no external dependencies beyond basic C types.

Risks and test signals: Risks include dangling arguments, double invocation when callers forget to clear, lack of type checking for the `void *` argument, and missing locking if shared across threads. Test paths that set and execute cleanup callbacks, no-callback cases, and error paths that clear or transfer ownership.
