# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vmlinux.lds.S

## Purpose
Defines the PowerPC kernel linker script, controlling section ordering, load addresses, program headers, special fixup tables, init/runtime boundaries, per-CPU layout, and discarded sections.

## Important APIs, Types, And Functions
Defines `ENTRY(_stext)`, PHDRS for text and note, architecture output, `jiffies` aliasing, macros `SOFT_MASK_TABLE` and `RESTART_TABLE`, strict RWX boundary symbols, feature-fixup sections, exception/bug/percpu/init/data/BSS sections, and exported boundary symbols such as `_stext`, `_etext`, `__init_begin`, `__init_end`, `_sdata`, `_edata`, and `_end`.

## Control Flow
At link time, fixed head text is placed first so exception vectors and trampolines remain at required offsets. Main text, read-only data, GOT/TOC/OPD, fixup tables, init text/data, runtime data, aligned data, bug tables, and BSS are then laid out with physical load addresses adjusted by `LOAD_OFFSET`. Relocatable builds keep dynamic symbol and relocation sections. Discards remove unsupported or unsafe sections.

## State And Persistence
This file shapes the kernel image rather than runtime logic. The resulting symbols drive boot, memory reservation, kexec, module/runtime patching, and init memory freeing.

## Dependencies And Integration Points
Depends on generic linker macros, PowerPC head/exception code, feature patching, speculative barrier fixups, percpu setup, init task layout, ftrace trampolines, sanitizers, relocatable-kernel support, and kexec exports such as `_end`.

## Risks And Edge Cases
Section placement is boot-critical. Head text must not receive random linker stubs. `CONFIG_DATA_SHIFT` must be at least page shift. Fixup table boundaries must align with runtime patching code. Discarding relocations or unwind data differs for relocatable and non-relocatable builds.

## Test Signals
Full kernel link success across 32/64-bit, Book3S/BookE, relocatable, sanitizer, and mitigation configs; `readelf`/`objdump` section checks; boot tests; feature-patching tests; and kexec tests that rely on `_end` and fixed head placement are primary signals.
