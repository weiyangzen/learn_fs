# sources/distributed-fs/ceph-client/include/linux/mmdebug.h

## Purpose
`mmdebug.h` defines MM-specific debug dump declarations and assertion/warning macros. It gives memory-management code contextual BUG/WARN helpers for pages, folios, VMAs, mm structs, VMA merge state, virtual address checks, IRQ state checks, and page-flag checks.

## Important APIs, Types, And Functions
Declared dump helpers are `dump_page()`, `dump_vma()`, `dump_mm()`, `dump_vmg()`, and `vma_iter_dump_tree()`. Under `CONFIG_DEBUG_VM`, macros include `VM_BUG_ON*`, `VM_WARN_ON*`, folio/page/VMA/MM/VMG variants, once variants, formatted `VM_WARN()`/`VM_WARN_ONCE()`, `VM_WARN_ON_IRQS_ENABLED()`, `VIRTUAL_BUG_ON()`, and `VM_BUG_ON_PGFLAGS()`. Without debug configs, most macros compile expressions through `BUILD_BUG_ON_INVALID()` or become no-ops.

## Control Flow And State
Debug builds evaluate conditions, dump the relevant object, and call `BUG()` or `WARN_ON()` when violated. Once variants keep static `__warned` state in `.data..once`. Non-debug builds preserve compile-time checking of expression validity without runtime cost. IRQ, virtual, and page-flag checks are controlled by separate debug configs.

## Dependencies And Integration Points
Dependencies include `bug.h` and `stringify.h`, plus forward declarations for MM types. Integration points include page/folio/VMA/mm invariant checks across the MM subsystem, lock and refcount assertions, VMA merge diagnostics, virtual address debug instrumentation, and page flag debug code.

## Risks And Test Signals
Risks include side effects in conditions that disappear in non-debug builds, crashes from BUG assertions in recoverable paths, missing object dump context, and false positives when invariants differ by config. Test signals include debug-VM builds, intentional invariant violation tests, object dump readability, once-warning behavior, IRQ-off assertions, and allconfig build coverage.
