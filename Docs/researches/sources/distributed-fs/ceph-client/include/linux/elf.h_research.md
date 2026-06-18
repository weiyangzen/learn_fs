# sources/distributed-fs/ceph-client/include/linux/elf.h

Purpose: kernel-internal ELF compatibility layer selecting native ELF types, personality hooks, core-note extensions, and GNU property parsing hooks.

Important APIs/types/functions: default `elf_read_implies_exec()`, `SET_PERSONALITY`, `SET_PERSONALITY2`, `START_THREAD`, `ARCH_SETUP_ADDITIONAL_PAGES`, ELF32/ELF64 type aliases (`elfhdr`, `elf_phdr`, `elf_note`, `Elf_Word`), extra coredump note hooks, `struct gnu_property`, `arch_parse_elf_property()`, and `arch_elf_adjust_prot()`.

Control flow: binfmt ELF includes this header to normalize architecture callbacks; loader parses headers/properties, sets personality, maps segments, starts the new thread, and core dumping optionally emits architecture notes.

State/persistence: no own state; affects process personality, memory protections, and ELF core output generated from process state.

Dependencies/integration: `asm/elf.h`, UAPI ELF definitions, binfmt ELF, coredump code, architecture GNU property and protection policies.

Risks/test signals: risks are incorrect ELF class aliasing, defaulting read-implies-exec too broadly/narrowly, ignoring GNU properties that require protection changes, and arch coredump note size/write mismatch. Test ELF32/ELF64 exec, PT_GNU_STACK, GNU property notes, vdso/additional pages, and coredump note validation.
