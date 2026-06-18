# sources/distributed-fs/ceph-client/lib/codetag.c

## Purpose

`sources/distributed-fs/ceph-client/lib/codetag.c` manages typed code-tag sections for built-in code and modules. It lets subsystems register a tag type, discover linker/module section ranges, iterate tags, and invoke type-specific load/unload callbacks.

## Important APIs, Types, and Functions

Important types are `struct codetag_type`, `struct codetag_range`, and `struct codetag_module`. Public functions include `codetag_lock_module_list`, `codetag_trylock_module_list`, `codetag_get_ct_iter`, `codetag_next_ct`, `codetag_to_text`, `codetag_needs_module_section`, `codetag_load_module`, `codetag_unload_module`, `codetag_register_type`, and `codetag_get_type`. Helpers include `get_symbol`, `get_section_range`, `codetag_module_init`, and `codetag_module_unload`.

## Control Flow

Registering a type allocates and initializes a `codetag_type`, adds it to the global list, and immediately initializes the built-in section range. Module load asks each registered type to locate `__start`/`__stop` symbols for its section and add a `codetag_module` entry to an IDR under the type write lock. Iteration requires the module list read lock, walks IDR entries by module id, detects module sequence changes, and advances by `tag_size` within each range. Module unload removes the IDR entry, calls optional unload callbacks, updates counts, and frees module state.

## State and Persistence Behavior

Global state is `codetag_types` protected by `codetag_lock`. Per type state includes count, module IDR, read/write semaphore, descriptor, and monotonically increasing module sequence. Per-module state persists for module lifetime. Built-in code is represented through a pseudo module name `(built-in)`.

## Dependencies and Integration Points

The file depends on `codetag.h`, IDR, kallsyms lookup, module loader hooks, seq_buf formatting, slab allocation, and linker-generated codetag section symbols. It integrates with optional module section allocation decisions through `needs_section_mem`.

## Risks and Edge Cases

Symbol lookup by constructed section names is fragile if linker naming changes. Iterators must hold the module-list read lock or module unload can invalidate ranges. Type-specific load errors must remove IDR entries and avoid count leaks. Empty ranges are valid and ignored.

## Test Signals

Tests should cover type registration, built-in range discovery, module load/unload, iteration across multiple modules, sequence change handling, empty ranges, load callback failure, text formatting with and without module names, and section memory decision callbacks.

## Read Coverage

Source read size: 405 lines, 9050 bytes.
