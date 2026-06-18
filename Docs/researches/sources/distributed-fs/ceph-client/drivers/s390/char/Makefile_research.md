# sources/distributed-fs/ceph-client/drivers/s390/char/Makefile

Purpose: maps s390 character-driver Kconfig symbols to Kbuild objects and applies sanitizer/tracing exclusions for early SCLP code.

Important APIs/types/functions: always-built objects include `ctrlchar.o`, `keyboard.o`, `defkeymap.o`, and core SCLP objects. Conditional entries build 3270/3215 tty/fullscreen, SCLP terminal variants, tape composite `tape_s390.o`, VM and monitor drivers, crash dump helpers, UV device, and the composite `hmcdrv.o`.

Control flow: no runtime behavior. Kbuild evaluates `obj-*`, composite object lists, and per-object flags. `hmcdrv-objs` links module core, misc device, FTP parser/cache, DIAG backend, and SCLP backend.

State and persistence behavior: build graph only; no runtime state.

Dependencies and integration points: ties Kconfig selections to source files. Early SCLP core disables ftrace, gcov, kcov, UBSAN, KASAN, fortify, and expoline flags where needed for boot constraints.

Risks and test signals: object-list drift breaks link-time symbol resolution, especially composite `hmcdrv` and `tape_s390`. Test built-in and modular combinations for terminal, HMC, tape, and crash-dump configs.
