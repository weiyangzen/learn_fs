
# sources/distributed-fs/ceph-client/lib/tests/ffs_kunit.c

## Purpose
`ffs_kunit.c` tests the find-first/find-last bit helper family: `ffs()`, `fls()`, `__ffs()`, `__fls()`, `fls64()`, `__ffs64()`, and `ffz()`. It also verifies that selected functions retain `__attribute_const__` behavior useful for compile-time optimization.

## Important APIs, types, and functions
The suite defines structured fixtures for 32-bit/unsigned-long and 64-bit values. Validators check exact outputs, mathematical relationships between 1-based and 0-based APIs, range bounds, and zero-input special cases. `CREATE_WRAPPER()` emits noinline functions with `BUILD_BUG_ON()` and `barrier_data()` to confirm static initializer behavior after function calls.

## Control flow
Tests run fixture tables for basic `ffs/fls`, 64-bit cases, relationship checks, edge patterns, `ffz()` exact cases, `ffz()` relationship patterns, and attribute-const wrappers. Undefined cases are deliberately skipped or only invoked for completion: `__ffs*()`/`__fls()` on zero are not asserted, and `ffz(~0UL)` is treated as implementation-defined.

## State and persistence
There is no persistent state. All fixtures are static constants and all validation state is local to test functions.

## Dependencies and integration points
It depends on `<linux/bitops.h>` and KUnit and is selected by `CONFIG_FFS_KUNIT_TEST`.

## Risks and edge cases
Many constants are 32-bit shaped but stored in `unsigned long`; behavior on 64-bit remains valid but does not exhaust all high unsigned-long positions outside explicit 64-bit tests. The attribute-const regression is compiler-sensitive by design.

## Test signals
Assertion messages include function name, hexadecimal input, description, expected value, and actual value for most correctness checks. Pass means exact and relational semantics hold for the covered patterns.
