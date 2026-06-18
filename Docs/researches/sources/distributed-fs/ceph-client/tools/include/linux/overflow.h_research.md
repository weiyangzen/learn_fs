<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/overflow.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/overflow.h

## Purpose
This header centralizes checked arithmetic and saturated size calculations for allocation and structure sizing.

## APIs And Flow
It exports type-limit helpers `is_signed_type`, `type_min`, `type_max`, overflow wrappers `check_add_overflow`, `check_sub_overflow`, `check_mul_overflow`, and size helpers `size_mul()`, `array_size()`, `array3_size()`, `__ab_c_size()`, and `struct_size()`. Flow delegates arithmetic checks to compiler builtins after enforcing matching operand and destination types.

## State, Dependencies, Risks, Tests
There is no state. Dependencies are `linux/compiler.h`, `SIZE_MAX`, `typeof`, and compiler overflow builtins. Risks include unsupported compilers, accidental type mismatches, `_Bool` arithmetic edge cases, and callers ignoring `SIZE_MAX` saturation before allocation. Tests should cover signed and unsigned limits, add/sub/mul overflow and non-overflow, flexible array sizing, and compile-time type mismatch detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/overflow.h -->
