# sources/distributed-fs/ceph-client/lib/clz_ctz.c

## Purpose

`sources/distributed-fs/ceph-client/lib/clz_ctz.c` supplies weak libgcc-compatible count-leading-zero and count-trailing-zero helpers required by compiler builtins on architectures that do not provide optimized versions.

## Important APIs, Types, and Functions

Exported weak functions are `__ctzsi2`, `__clzsi2`, `__clzdi2`, and `__ctzdi2`. They use `__ffs`, `fls`, `fls64`, and `__ffs64`.

## Control Flow

Each helper maps directly to a kernel bit operation: trailing-zero helpers return first-set-bit index, and leading-zero helpers subtract the last-set-bit position from the operand width.

## State and Persistence Behavior

No state is stored. The functions are pure for valid nonzero inputs.

## Dependencies and Integration Points

The functions integrate with compiler-generated calls from `__builtin_ctz*` and `__builtin_clz*`, and can be overridden by arch-specific strong definitions.

## Risks and Edge Cases

Compiler builtin semantics usually leave zero input undefined, and these helpers inherit that risk through `__ffs`/`fls` behavior. Weak symbol ordering must allow arch overrides.

## Test Signals

Signals include link coverage on architectures needing libgcc helpers, known values for 32-bit and 64-bit operands, zero-input caller avoidance, exported symbol checks, and arch override builds.

## Read Coverage

Source read size: 43 lines, 979 bytes.
