# sources/distributed-fs/ceph-client/drivers/acpi/acpica/dswload.c

## Purpose
Implements first-pass ACPICA namespace loading callbacks. Pass 1 discovers named AML objects, creates or validates namespace nodes, opens and closes scopes, creates early method objects, and handles disassembler-only external/create-field cases before full object attachment in pass 2.

## Important APIs, Types, And Functions
- `acpi_ds_init_callbacks` configures walk-state parse flags and callbacks for parse-only, load pass 1, load pass 2, and execution pass.
- `acpi_ds_load1_begin_op` is the descending pass-1 callback that handles named op lookup/creation, Scope target validation, external declarations, namespace override behavior, and new parse op allocation for stream parsing.
- `acpi_ds_load1_end_op` is the ascending pass-1 callback that initializes field declarations, creates early operation regions/data regions, sets `Name` node types from their initializer object type, creates method objects, and pops scope frames.

## Control Flow
Pass 1 ignores opcodes without associated names. For `Scope`, it looks up the target in execute mode and verifies that the target can open a scope, allowing compatibility type override for integer/string/buffer targets and a module-level root-method exception. Other named opcodes create namespace nodes with no upsearch and optional error/override-if-found semantics, unless a deferred node or method execution context says the node already exists or must wait until execution. On ascent, field objects are initialized outside method execution, region shells are created from saved AML address/length data, method nodes get attached method objects as soon as possible so later method invocations know argument counts, and scope-opening opcodes pop the scope stack.

## State And Persistence
Persistent state is the namespace tree and parse op `common.node`/`named.name` fields. Walk-state flags capture pass semantics, `deferred_node`, `namespace_override`, `method_node`, and scope stack state. Method creation attaches runtime objects to namespace nodes during pass 1; field and region creation may attach partial objects used later by pass 2 or execution.

## Dependencies And Integration Points
Uses parser namestring extraction/allocation, namespace lookup, scope-stack helpers, region and field creation helpers, method creation, ASL compiler/disassembler external handling, and opcode metadata. It is initialized by walk-state setup and feeds load pass 2 and method execution.

## Risks And Edge Cases
Scope target type compatibility is intentionally permissive for firmware quirks, but method targets remain invalid except module-level root handling. Deferred op parsing must not duplicate namespace nodes. External declarations in disassembler mode must be retyped and tracked without opening scopes incorrectly. Method execution must avoid pass-1 namespace creation because execution-time temporary nodes are owned by pass 2/execution.

## Test Signals
Tests should cover Scope on existing devices and invalid targets, duplicate names with and without override, deferred region/buffer/package loading, method objects callable after pass 1, disassembler external op handling, and correct scope-depth balancing after nested devices/power resources/processors/thermal zones.
