## sources/distributed-fs/ceph-client/lib/tests/randstruct_kunit.c

### Purpose
This KUnit suite verifies `CONFIG_RANDSTRUCT` layout randomization and initializer correctness. It compares randomized and non-randomized struct layouts for ordinary members, function-pointer-only structs, mixed-type structs, nested randomized members, and named/compound initializers.

### Important APIs, types, and functions
`DO_MANY_MEMBERS()` generates eight member names consistently for enums, unsigned long fields, function pointer fields, offset-check functions, and initializers. The file defines untouched and shuffled variants: `struct randstruct_untouched`, `struct randstruct_shuffled __randomize_layout`, `struct randstruct_funcs_untouched __no_randomize_layout`, implicit `struct randstruct_funcs_shuffled`, mixed structs, and containers. `check_pair()` counts offset mismatches and expects either equality or greater-than-zero differences. Initializer helpers compare values or function pointers between untouched and shuffled forms.

### Control flow
Suite init `randstruct_test_init()` skips all tests unless `CONFIG_RANDSTRUCT` is enabled. Layout cases compare same-type controls, explicitly randomized structs, implicit all-function-pointer randomization, and nested function-pointer randomization. The deep nested function-pointer case skips under Clang due to a documented compiler issue. `randstruct_initializers()` builds named and unnamed instances, nested compound literals, full struct-copy initializers, mixed structs, and function pointer initializers, then verifies member values survive randomization.

### State and persistence
All test state is stack-local. No runtime layout changes occur; randomization is a compile-time layout property. Generated `func_a` through `func_h` return untouched offsets and serve as stable function pointer values for initializer tests.

### Dependencies and integration points
The suite depends on KUnit, randstruct compiler plugin/attribute support, `__randomize_layout`, `__no_randomize_layout`, `offsetof`, and `CONFIG_RANDSTRUCT`. It integrates under suite name `randstruct`.

### Risks and edge cases
Randomization can theoretically produce the same layout, so mismatch expectations may fail with an “unlucky or broken” message if all members land at matching offsets. The test mitigates this by using eight members but cannot eliminate probability. Compiler differences are explicit: Clang skips deep inner function pointer randomization due to known behavior. Offset comparison across different types relies on parallel member names and compatible member sets.

### Test signals
Signals include offset mismatch counts logged for each compared pair, skips when randstruct is absent or Clang cannot cover a case, and initializer value/function-pointer equality across randomized layouts.
