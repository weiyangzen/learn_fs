# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-helpers.h

Purpose: generic support header for pkey selftests, providing shared types, debug output, assertion behavior, shadow-register verification, syscall prototypes, alignment helpers, and architecture dispatch.

Important APIs and types: defines `u8/u16/u32/u64`, `PTR_ERR_ENOTSUP`, `sigsafe_printf()`, `dprintf0..4`, `pkey_assert()`, syscall prototypes, `set_pkey_bits()`, `get_pkey_bits()`, `read_pkey_reg()`, `write_pkey_reg()`, `siginfo_get_pkey_ptr()`, `kernel_has_pkeys()`, and `is_pkeys_supported()`.

Control flow and state: architecture headers are included by target. `read_pkey_reg()` asserts hardware state equals external `shadow_pkey_reg`; lower-level `__read_pkey_reg()` is used when signal/ptrace paths intentionally bypass the shadow check.

Dependencies and risks: shared by `protection_keys.c`, `pkey_sighandler_tests.c`, and `pkey_util.c`. The shadow invariant is a high-value signal but can fail if signal handlers or ptrace mutate register state without explicit shadow repair.
