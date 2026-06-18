# sources/distributed-fs/ceph-client/tools/perf/util/annotate.h

## Purpose
Defines the public data structures and APIs for perf annotation. It is the contract between sample accounting, disassembly, UI rendering, branch/cycle analysis, data-type attribution, and architecture-specific instruction parsing.

## Important APIs, Types, and Functions
`struct annotation_options` stores display/config behavior such as source visibility, offsets, jump arrows, line counts, disassembler preference, percent type, and type display.
`struct annotation_line` represents either a source line or disassembly line with offsets, rendered text, source path, cycles, branch counters, event data, indices, and jump-source counts.
`struct disasm_line` embeds `struct annotation_line` and adds instruction metadata, operands, and raw instruction bytes.
`struct annotated_source` stores all lines and histograms for a symbol.
`struct annotated_branch` stores cycle/IPC/coverage and branch-counter data.
`struct annotation` hangs annotation state off `struct symbol`.
The header declares lifecycle, locking, sample/cycle accounting, disassembly, printing, config, operand-location, data-type lookup, branch-counter formatting, basic-block discovery, and debuginfo cache APIs.

## Control Flow
Callers account samples into symbol histograms, request disassembly through `symbol__annotate()` or `symbol__annotate2()`, calculate/render line data through the declared UI functions, and optionally resolve data types through `hist_entry__get_data_type()`. Architecture-specific parsers fill `ins_operands`; `annotate_get_insn_location()` normalizes operands into register/offset fields for data typing.

## State and Persistence
All structures are process-local and generally attached to symbols for the duration of an annotate operation. Histograms, source lists, cycles, and branch counters are allocated dynamically and released by `annotation__exit()` or purged after TTY annotation. Options are global in `annotate_opts`.

## Dependencies and Integration Points
Includes symbol config, mutexes, sparkline support, hashmap, disassembly, branch, and evsel declarations. It is included by architecture adapters, `annotate.c`, `annotate-data.c`, UI code, and code that accounts perf samples.

## Risks
The flexible array `annotation_line.data[]` requires correct allocation sizing. Histogram keys reserve 16 bits for evsel index in implementation, which assumes event indices fit that packing. Public structs expose many fields, so changes can affect UI, disassembly, and data-type code simultaneously.

## Test Signals
Compile-time tests should cover builds with different optional UI/DWARF features. Runtime tests should validate lifecycle cleanup, locking, histogram indexing, branch counter formatting, offset/full-address rendering, and operand-location extraction across architectures.
