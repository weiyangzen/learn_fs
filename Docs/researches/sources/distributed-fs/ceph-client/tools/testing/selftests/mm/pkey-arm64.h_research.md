# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey-arm64.h

Purpose: supplies arm64-specific protection-key definitions for the generic pkey selftests, mapping Linux pkey operations onto Permission Overlay Extension state in `POR_EL0`.

Important APIs and types: defines syscall numbers, `NR_PKEYS`, `PKEY_MASK`, POE permission encodings, `PKEY_REG_ALLOW_ALL/NONE`, page/hugepage sizing, `__read_pkey_reg()`, `__write_pkey_reg()`, `pkey_bit_position()`, arm64-specific `set_pkey_bits()` and `get_pkey_bits()`, and `aarch64_write_signal_pkey()`.

Control flow and state: included by `pkey-helpers.h` on `__aarch64__`; generic tests call these inline helpers for register access, permission encoding, and signal-context repair. It has no standalone state but mutates per-thread `POR_EL0` and optional signal-frame POE context.

Dependencies and risks: depends on `vm_util.h`, arm64 signal test context helpers, `NT_ARM_POE` ptrace support, and kernel POE support. Risks include mismatched POE encodings, signal-frame layout changes, and `cpu_has_pkeys()` returning true before kernel support is verified.
