# sources/distributed-fs/ceph-client/scripts/gen_packed_field_checks.c

## Purpose
`gen_packed_field_checks.c` is a host generator that emits C preprocessor macros for checking packed fields up to `MAX_PACKED_FIELD_SIZE`.

## Important APIs, Types, and Functions
`main()` prints `CHECK_PACKED_FIELDS_1`, recursive `CHECK_PACKED_FIELDS_N` macros for `N=2..50`, and a dispatcher macro `CHECK_PACKED_FIELDS(fields)` using nested `__builtin_choose_expr()` on `ARRAY_SIZE(fields)`.

## Control Flow
The first macro directly checks index zero. Each later macro wraps the previous one in `do { ... } while (0)` and adds the next index. The dispatcher selects the matching macro or emits a `BUILD_BUG_ON_MSG` for arrays larger than the generator supports.

## State and Persistence Behavior
The program writes generated text to stdout and has no persistent state.

## Dependencies and Integration Points
It depends on host C compilation and kernel macros available to the generated output (`ARRAY_SIZE`, `CHECK_PACKED_FIELD`, `BUILD_BUG_ON_MSG`).

## Risks and Test Signals
The maximum size is hard-coded to 50; consumers with larger arrays must regenerate with a higher constant. Test by compiling the generated header, exercising boundary sizes 1, 50, and 51.
