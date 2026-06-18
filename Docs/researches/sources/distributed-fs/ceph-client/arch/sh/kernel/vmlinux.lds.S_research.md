# sources/distributed-fs/ceph-client/arch/sh/kernel/vmlinux.lds.S

Purpose: defines the SuperH kernel linker layout, including physical/virtual start, text/data/init sections, exception tables, unwind data, per-CPU data, BSS, and debug sections.

Important symbols and constructs: `OUTPUT_ARCH(sh)`, `ENTRY(_start)`, `_text`, `_etext`, `_sdata`, `_edata`, `__init_begin`, `__init_end`, `__bss_start`, `_end`, `DWARF_DEBUG`, `PERCPU_SECTION`, `EXCEPTION_TABLE`, and SH-specific sections from `asm/vmlinux.lds.h`.

Control flow: the linker script aligns executable, read-only, data, init, and BSS ranges and exports boundary symbols consumed by boot, memory init, module/debug, and freeing-init-memory paths.

State and persistence: this is build-time layout state that becomes fixed addresses in `vmlinux`; it directly controls runtime section boundaries and memory reservations.

Dependencies and integration: included by the top-level kernel link and depends on thread info, cache, and SH linker macros. Many files in this subset refer to the emitted section symbols.

Risks: alignment or boundary mistakes can break early boot, exception fixups, cacheline-sensitive sections, init memory release, or crash/debug tooling.

Test signals: successful SH kernel link, `readelf` section inspection, boot smoke tests, and section-boundary sanity in early memory initialization.
