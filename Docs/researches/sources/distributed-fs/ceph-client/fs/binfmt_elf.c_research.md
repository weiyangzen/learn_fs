# sources/distributed-fs/ceph-client/fs/binfmt_elf.c

Purpose: implements Linux ELF executable loading and, when enabled, ELF core dump generation.

Important APIs/types/functions: `elf_format`, `load_elf_binary`, `create_elf_tables`, `elf_map`, `elf_load`, `load_elf_phdrs`, `load_elf_interp`, GNU property parsing, `make_prot`, coredump note helpers, `fill_note_info`, `write_note_info`, `elf_core_dump`, and binfmt init/exit registration.

Control flow: exec validates ELF magic/type/arch/mmapability, loads program headers, opens and validates a `PT_INTERP` interpreter if present, processes stack/property/arch headers, starts a new exec, sets personality and ASLR, maps `PT_LOAD` segments with correct load bias and BSS zeroing, maps the interpreter, builds auxv/argv/envp stack tables, sets mm code/data/brk/stack fields, runs arch setup, finalizes exec, and starts the thread at the resolved entry. Coredump first builds ELF/note metadata and offsets, then writes headers, note segments, VMA program headers, notes, dumped memory ranges, arch extras, and extended numbering if needed.

State and persistence: mutates the current process `mm_struct`, credentials-related auxv values, personality/randomization flags, brk, VMA layout, saved ELF flags, and register state at exec. Core dump output persists process metadata, mapped file notes, thread regsets, auxv, signal info, and selected VMA contents.

Dependencies and integration: central binfmt integration with `register_binfmt`, exec credential/security flow, mmap/brk APIs, arch ELF hooks, randomization, GNU property parsing, user regsets, coredump infrastructure, LSM checks through exec/mmap paths, and optional KUnit test include.

Risks: this is a high-risk security boundary. Segment size/address overflow, `MAP_FIXED_NOREPLACE`, BSS zeroing, interpreter permissions, executable stack policy, auxv correctness, and property parsing must be precise. Core notes must respect size limits and avoid leaking unintended data.

Test signals: ELF KUnit when enabled; LTP/binfmt exec tests; PIE/static PIE/interpreter ASLR cases; malformed phdr/property/interpreter files; executable-stack binaries; core dump validation with many VMAs/threads/mapped files; architecture-specific regset and auxv checks.
