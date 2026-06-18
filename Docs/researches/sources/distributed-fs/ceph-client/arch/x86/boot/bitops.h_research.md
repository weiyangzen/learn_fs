## sources/distributed-fs/ceph-client/arch/x86/boot/bitops.h

### Purpose
`bitops.h` provides a tiny boot-environment replacement for generic Linux bit operations without pulling in the full kernel `linux/bitops.h`.

### Important APIs, Types, And Functions
It defines `_LINUX_BITOPS_H` to inhibit generic inclusion, provides `constant_test_bit()`, `variable_test_bit()`, the `test_bit()` macro, and `set_bit()`.

### Control Flow
`test_bit()` chooses a pure C indexed test when the bit number is compile-time constant and an x86 `btl` instruction when variable. `set_bit()` uses `btsl` on a 32-bit word.

### State, Persistence, And Dependencies
The state is the caller-provided bitmap memory. It depends on x86 inline assembly constraints, `u32`, `bool`, and boot code's limited header environment.

### Integration Points
Included from `boot.h`, it supports boot CPU flag and setup bitmap checks before the full kernel bitops API is available.

### Risks
Operations are not atomic beyond the instruction semantics used and are intended for single-threaded boot code. The implementation assumes little-endian 32-bit word indexing and x86 assembly.

### Test Signals
Compile real-mode setup code, test constant and variable bit positions across word boundaries, and verify generated assembly accepts both immediate and register bit operands.
