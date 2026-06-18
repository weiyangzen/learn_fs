# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exdump.c

## Purpose
`exdump.c` provides debug-only object and namespace dump routines for the ACPICA executor and debugger.

## Important APIs, Types, And Functions
Compiled under `ACPI_DEBUG_OUTPUT` or `ACPI_DEBUGGER`, it exposes `acpi_ex_dump_operand`, `acpi_ex_dump_operands`, `acpi_ex_dump_namespace_node`, and `acpi_ex_dump_object_descriptor`. Private helpers include `acpi_ex_dump_object`, `acpi_ex_dump_reference_obj`, `acpi_ex_dump_package_obj`, `acpi_ex_out_string`, and `acpi_ex_out_pointer`. Large `struct acpi_exdump_info` tables describe fields for each object type.

## Control Flow
Dump descriptor tables map object types to offsets and display opcodes. `acpi_ex_dump_object` walks a table and prints scalar fields, pointers, strings, buffers, package contents, handler lists, region lists, nodes, and reference details. `acpi_ex_dump_operand` is the concise operand dump path gated by execution debug level; it validates descriptor type and switches over common ACPI object types. `acpi_ex_dump_operands` iterates opcode operands. `acpi_ex_dump_object_descriptor` can force display, dumps namespace nodes first when given a node, validates object type, dumps common fields, then object-specific fields and region secondary objects.

## State And Persistence
No runtime state is changed. The routines read live object graphs and print diagnostic information. They include circular-list detection for object, handler, and region chains to avoid infinite dumps.

## Dependencies And Integration Points
The file depends on ACPICA descriptor layout, namespace names, debug level checks, debugger builds, and dump/print helpers. It is an observability tool for executor objects created by files such as `excreate.c`, `evxface.c`, and `evxfregn.c`.

## Risks
Because it reads internal structures by offsets, descriptor layout changes require table updates. Debug output may reveal pointers and firmware contents. Recursive package dumps and large buffers can create substantial logs, although some paths cap buffer display. Debug-only compilation means production issues may not exercise this code.

## Test Signals
Tests should compile debug and non-debug configurations, dump each supported object type, validate circular-list detection, verify namespace node plus attached object output, exercise package recursion and reference path conversion, and confirm debug-level gating.
