# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acopcode.h

Purpose: defines AML opcode metadata macros for parser-time arguments (`ARGP_*`) and interpreter-time arguments (`ARGI_*`), feeding ACPICA's master opcode table.

Important APIs/macros: defines extended/internal opcode bounds, sentinel opcode classes for unknown/name/prefix handling, parse argument lists for AML opcodes, and runtime operand requirements for executable opcodes. Declaration-only opcodes are marked invalid for runtime operand preparation.

Control flow: parser code uses `ARGP_*` lists to consume AML byte streams and construct parse objects. Interpreter operand-preparation code uses `ARGI_*` lists to resolve and type-check operands before executor functions run.

State and persistence: no runtime state is owned. The persistent effect is compile-time opcode metadata in `psopcode.c`.

Dependencies and integration: depends on argument token constants and list macros from other ACPICA headers. Used by parser, interpreter operand-resolution code, and ASL compiler validation.

Risks: one wrong argument list can desynchronize parsing or cause runtime type errors. Parse-time and runtime forms differ for declarations, targets, references, method calls, packages, and fields. The bare `MAX_INTERNAL_OPCODE` define reflects upstream table conventions and must be tolerated by consumers.

Test signals: AML parser suites covering every opcode, malformed AML fuzzing, runtime operand validation, ASL compiler opcode validation, and comparisons to known ACPICA opcode tables.
