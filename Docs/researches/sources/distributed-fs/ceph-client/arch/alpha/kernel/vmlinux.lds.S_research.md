# sources/distributed-fs/ceph-client/arch/alpha/kernel/vmlinux.lds.S

## Purpose
Alpha linker script defining the final kernel image layout, entry point, ELF format, load program headers, section order, and debug/discard handling. The source was read as part of `subset-b-000628` and contains 78 lines.

## Important APIs, Types, and Functions
Sets `OUTPUT_FORMAT("elf64-alpha")`, `OUTPUT_ARCH(alpha)`, `ENTRY(__start)`, `PHDRS`, `jiffies = jiffies_64`, and layout symbols such as `_text`, `_etext`, `__init_begin`, `__init_end`, `_sdata`, `_data`, `_edata`, and `_end`.

## Control Flow
The linker starts the image at either the legacy or normal Alpha kernel virtual address, emits text/fixup/warning sections, places `swapper_pg_dir`, emits read-only data, init text/data, percpu data, aligned RW data, GOT/sdata, BSS, mdebug/note, debug metadata, module info, ELF details, and generic discard rules.

## State and Persistence Behavior
The output is persistent link-time structure in `vmlinux`: symbol addresses, section boundaries, init-memory lifetime, page-directory placement, and debug/note sections. It has no runtime control flow.

## Dependencies
Depends on `asm-generic/vmlinux.lds.h`, Alpha thread/cache/page/setup constants, `CONFIG_ALPHA_LEGACY_START_ADDRESS`, `SWAPPER_PGD`, and section macros emitted by compiler/assembler sources.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
Address or alignment changes can break early boot, PAL expectations, init memory freeing, percpu access, or page-table placement. Missing `.fixup`/exception-related sections can break fault recovery. Program headers must satisfy bootloader expectations.

## Test Signals
Build `vmlinux`, inspect `readelf -lS` and `nm` for expected entry/address symbols, boot both legacy and normal start configurations, and verify init memory is freed without corrupting aligned `init_task`/percpu data.
