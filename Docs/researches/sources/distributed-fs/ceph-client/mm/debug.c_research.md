# sources/distributed-fs/ceph-client/mm/debug.c

## Purpose
This file provides MM debugging and dump helpers for pages, folios, VMAs, `mm_struct`, and VMA merge state. It also defines trace-print flag name tables and a `vm_debug` boot option for page-struct initialization poisoning.

## Important APIs, Types, And Functions
Exported data includes `migrate_reason_names`, `pageflag_names`, `gfpflag_names`, and `vmaflag_names`. Page type rendering is handled by `page_type_names[]` and `page_type_name()`.

Key dump functions are `dump_page()`, `dump_vma()`, `dump_mm()`, and `dump_vmg()`. Internal helpers `__dump_page()` and `__dump_folio()` snapshot and print folio/page state, including refcount, mapcount, mapping, index, PFN, large-folio details, memcg data, KSM/anon/mapping information, flags, page type, and raw `struct page` bytes.

Debug configuration uses `setup_vm_debug()` through `__setup("vm_debug", ...)`, `page_init_poisoning`, and `page_init_poison()`. `vma_iter_dump_tree()` dumps maple-tree state under `CONFIG_DEBUG_VM_MAPLE_TREE`.

## Control Flow
`dump_page()` detects poisoned pages, otherwise snapshots the page and folio, prints metadata, prints page owner information, and appends a reason string if supplied. `dump_vma()`, `dump_mm()`, and `dump_vmg()` format progressively larger VM state; `dump_vmg()` optionally recurses into `dump_mm()` and `dump_vma()` for related objects and dumps the VMA iterator tree if configured.

The `vm_debug` boot parameter parser treats no argument as enabling supported debug options. With an explicit option string, it currently recognizes `p` for page initialization poisoning; a leading `-` disables all controllable options. Unknown option characters emit errors and are skipped.

## State And Persistence
The only persistent state is the static `page_init_poisoning` flag, initialized true and changed by the early boot option. Dump functions do not mutate inspected objects except for reading snapshots and printing logs. `page_init_poison()` writes `PAGE_POISON_PATTERN` into page structures when enabled.

## Dependencies And Integration Points
The file depends on core MM structures, trace event flag definitions, migration trace metadata, memcg, page owner, maple tree debugging, and architecture/formatting support for `%pGp`, `%pGg`, and `%pGv`-style flag rendering.

The exported dump helpers are used across the MM subsystem for diagnostics, VM assertions, and fault reporting. `dump_page()` is exported for modules.

## Risks And Edge Cases
Dump output intentionally accepts racing state. Comments note pageblock migratetype may change while printing flags. The snapshot path warns if the page snapshot does not match folio state, but still prints available data.

These functions can emit sensitive kernel pointer-like values depending on kernel pointer formatting policy. They are diagnostic tools and may be noisy under repeated failure paths.

`setup_vm_debug()` mutates global behavior early in boot only. New options must preserve backward behavior of no-argument and `-` parsing.

## Test Signals
There is no direct KUnit suite in this file. Runtime test signal comes from build coverage, boot-time `vm_debug` parsing, and downstream users invoking dump helpers during DEBUG_VM assertions or page diagnostics.
