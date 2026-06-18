# sources/distributed-fs/ceph-client/drivers/acpi/acpica/amlcode.h

## Purpose
Defines AML opcode numbers, parser argument encodings, interpreter resolved argument types, opcode metadata flags/types/classes, package-length markers, match operators, field flags, access/update/lock rules, access attributes, and method flag bit masks directly derived from the ACPI specification.

## Important APIs, Types, And Constants
Primary opcodes cover literals, names, method/scope/package/buffer creation, locals/args, arithmetic/logical operations, type conversions, control flow, and return/break operations. Extended opcodes use the `0x5B` prefix and include mutex/event, field, load/stall/sleep, acquire/release, region/device/processor/power/thermal, and data-region definitions. Internal parser opcodes represent synthetic nodes such as name paths, named fields, byte lists, method calls, return values, and connection/ext-access fields. `ARGP_*` values describe parser grammar arguments, `ARGI_*` values describe interpreter operand requirements, `AML_FLAGS_*` and `AML_TYPE_*` drive opcode dispatch, and field/method enums decode AML flag bytes.

## Control Flow, State, And Persistence
This file is declarative, but its numeric constants drive parser decoding and interpreter dispatch. Parser code reads AML bytes, maps opcodes to `acpi_opcode_info`, interprets `ARGP_*` grammar encodings, resolves operands to `ARGI_*` types, and dispatches by `AML_TYPE_*`. Field-creation paths decode access, lock, update, and attribute bits from AML field flags. There is no owned mutable state.

## Dependencies And Integration Points
Used by parser, interpreter, disassembler, compiler, dispatcher, debugger displays, and field handling. Numeric values must stay aligned with the ACPI specification and opcode info tables compiled elsewhere. Internal opcode values deliberately avoid valid ACPI ASCII values to prevent conflicts.

## Risks And Test Signals
Changing an opcode value or dispatch type is catastrophic because it alters AML bytecode semantics. Risks include parser/interpreter table mismatch, invalid operand resolution, incorrect field access/update behavior, and broken disassembly output. Test signals include AML parser/compiler round trips, method execution tests for each opcode class, field access tests, disassembler output comparison, and boots with diverse firmware AML.
