# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/relocate.c

Purpose: this early boot routine applies relative relocations to the kernel image after a runtime offset is chosen. It supports classic RELA relative relocations and compressed RELR relative relocations.

Important APIs and state: `relocate_kernel(u64 offset)` is the single exported entry point. Linker-provided ranges `rela_start`/`rela_end` and `relr_start`/`relr_end` identify relocation tables. A local `place` pointer tracks the current RELR relocation word while decoding bitmap entries.

Control flow: the function first scans every `Elf64_Rela` record and applies only `R_AARCH64_RELATIVE` relocations by writing `r_addend + offset` to `r_offset + offset`. If `CONFIG_RELR` is disabled or `offset` is zero, it returns after RELA. Otherwise it decodes RELR: even entries are base addresses to relocate and advance from; odd entries are bitmaps for up to 63 subsequent machine words, with each set bit adding the offset to the corresponding word.

Dependencies and integration: called by early PI mapping/relocation code declared in `pi.h`, and depends on linker script symbols for relocation table boundaries. It assumes the image is mapped writable at the offset-adjusted addresses and that only relative relocation types need early application.

Risks: RELR decoding is compact but sensitive to `place` sequencing; malformed or unsorted RELR data would relocate wrong addresses. The implementation intentionally ignores non-relative RELA records because other relocation classes are either forbidden by build checks or handled elsewhere. Running with `offset == 0` skips RELR because adding zero is unnecessary.

Test signals: KASLR boot with nonzero offsets, `CONFIG_RELR` builds, and relocation test modules provide coverage. Failures generally appear as early boot crashes, bad global pointers, or corrupted data after relocation.
