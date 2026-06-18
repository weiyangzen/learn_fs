<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/sparc/kernel/vmlinux.lds.S

## Purpose
Defines the SPARC kernel linker script for both 32-bit and 64-bit builds, controlling image format, entry point, fixed virtual/physical start addresses, section layout, patch-section collection, percpu layout, BSS, debug metadata, and discarded sections.

## Important APIs, Types, And Functions
Key linker symbols and sections include `_text`, `_etext`, `_sdata`, `_edata`, `__init_begin`, `__init_text_end`, `__init_end`, `_end`, `swapper_pg_dir`, `jiffies`, `.fixup`, exception table, TSB patch sections, Sun4v/LEON/POPC/PAUSE/M7/get_tick/pud/fast-window patch sections, `PERCPU_SECTION`, `BSS_SECTION`, `STABS_DEBUG`, `DWARF_DEBUG`, `MODINFO`, `ELF_DETAILS`, and `DISCARDS`.

## Control Flow
The linker, not runtime code, evaluates this file. It selects ELF32 or ELF64 output based on configuration, places head text and normal text at architecture-specific addresses, aligns read-only/data/init/percpu areas, emits start/end symbols for runtime patch iterators, and asserts that early SPARC64 assembler has not moved `swapper_tsb` away from its expected address.

## State And Persistence
The script determines persistent kernel image layout and the runtime symbol addresses consumed by boot, trap, patching, exception-table, init, module, percpu, and debug code.

## Dependencies And Integration Points
Depends on generic Linux linker-script macros, SPARC page/thread constants, early head assembly, patch emitters throughout SPARC assembly files, exception tables from faultable assembly, and runtime patching code that walks the emitted start/end symbols.

## Risks And Edge Cases
Small alignment or address changes can break early boot, MMU setup, trap-table location, or patch iteration. The SPARC64 `swapper_tsb` assertion protects a hard-coded early assembler dependency. Missing patch sections would leave platform-specific instructions unpatched.

## Test Signals
Signals include successful SPARC32/SPARC64 link, `vmlinux` symbol inspection, early boot through MMU setup, runtime patch application, exception-table fixups, module metadata presence, and failure of the explicit `swapper_tsb` assertion if early text grows too large.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/kernel/vmlinux.lds.S -->
