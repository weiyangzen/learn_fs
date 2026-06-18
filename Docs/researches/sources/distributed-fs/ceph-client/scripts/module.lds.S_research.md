<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/module.lds.S -->
# sources/distributed-fs/ceph-client/scripts/module.lds.S

## Purpose

`module.lds.S` is the linker script fragment for kernel modules. It arranges module-specific sections, metadata, init/exit areas, alternatives, unwind/orc data, BTF, and architecture-provided sections into a layout expected by the loader.

## Important APIs, Types, and Functions

The file uses linker-script `SECTIONS` syntax and C preprocessor conditionals/macros from kernel linker headers. Important section families include `.text`, `.init`, `.exit`, `.modinfo`, `__versions`, `__patchable_function_entries`, `.orc_*`, `.BTF`, and architecture hook sections.

## Control Flow

The linker consumes the script during module final link. Section patterns collect input sections, preserve required metadata with `KEEP()` where needed, and discard or align sections according to kernel module expectations.

## State and Persistence Behavior

The script persists no state itself, but controls the section layout of every `.ko` linked with it.

## Dependencies and Integration Points

It depends on GNU ld/LLD linker-script compatibility, module loader expectations, modpost-generated sections, objtool ORC data, BTF generation, livepatch metadata, and architecture linker fragments.

## Risks and Edge Cases

Dropping required sections can break module loading, unwinding, tracing, BTF, alternatives, or symbol versioning. Linker differences and new instrumentation sections require careful updates. Alignment and `KEEP()` placement affect garbage collection.

## Test Signals

Build and load modules with modversions, ORC unwind, BTF, ftrace, livepatch, alternatives, and multiple architectures using ld.bfd and LLD. Inspect `readelf -S` and module loader diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/module.lds.S -->
