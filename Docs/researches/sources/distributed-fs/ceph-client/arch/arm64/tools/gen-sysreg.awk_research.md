# sources/distributed-fs/ceph-client/arch/arm64/tools/gen-sysreg.awk

## Purpose

parses the arm64 sysreg description DSL and emits C preprocessor definitions for registers, fields,
field masks, and RES0/RES1/unknown bit metadata

## Important APIs, Types, and Functions

Source read size: 411 lines, 8629 bytes. Functions: `block_current`, `fatal`, `block_push`,
`block_pop`, `expect_fields`, `define`, `define_reg`, `define_field`, `define_field_sign`,
`define_resx_unkn`, `parse_bitdef`.

## Control Flow and Behavior

important routines include block_push/pop, define_reg, define_field, define_resx_unkn, parse_bitdef,
and fatal; the parser tracks nested register/field blocks and validates field counts and bit ranges

## State and Persistence

state is in AWK block stacks, current register names, and emitted definition ordering during header
generation only

## Dependencies and Integration Points

integrates with Kbuild-generated arm64 sysreg headers and many low-level cpufeature, system-
register, and trap handlers

## Risks and Test Signals

malformed descriptors can silently misdescribe architectural registers if validation is weakened;
build-time generation and compile users of generated macros are the primary tests
