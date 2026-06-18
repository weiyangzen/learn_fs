# sources/distributed-fs/ceph-client/fs/compat_binfmt_elf.c

Purpose: builds 32-bit ELF executable and core-dump support for a 64-bit kernel by macro-renaming ABI types, hooks, and local symbols before including the native `binfmt_elf.c` implementation.

Important APIs/macros: defines `ELF_COMPAT`, sets `ELF_CLASS` to `ELFCLASS32`, maps ELF header/program/note/address types to `elf32_*`, maps signal/core-note types to compat forms, maps timeval conversion to `ns_to_old_timeval32`, and requires `compat_elf_check_arch`. Optional `COMPAT_ELF_*`, `COMPAT_ARCH_*`, and `COMPAT_START_THREAD` macros override platform notes, hwcaps, ET_DYN base, personality setup, auxiliary vectors, additional pages, and start-thread behavior. Local symbols such as `elf_format` are renamed to `compat_elf_format`.

Control flow: there is no runtime logic in this file before inclusion. Preprocessor definitions specialize the shared `binfmt_elf.c` code, which then compiles a second binfmt instance for compat ELF.

State and persistence: state is the binfmt registration and core-dump behavior created by the included file. This wrapper itself stores no data.

Dependencies/integration: depends on architecture-provided compat ELF definitions in `asm/elf.h`, `linux/elfcore-compat.h`, compat signal/time types, and the native ELF loader source.

Risks: macro drift between native and compat builds can silently break 32-bit exec or core notes. Architectures must provide correct compat hooks, especially for thread start, auxv, hwcaps, and core register sets. Including a C file makes symbol-renaming completeness important.

Test signals: run 32-bit ELF binaries on supported 64-bit kernels, validate 32-bit core files and notes with debuggers, check compat auxv/hwcaps, run binfmt ELF KUnit/selftests if enabled, and compile architectures with and without optional `COMPAT_*` overrides.
