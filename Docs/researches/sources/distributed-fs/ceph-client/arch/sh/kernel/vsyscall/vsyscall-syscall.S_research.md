# sources/distributed-fs/ceph-client/arch/sh/kernel/vsyscall/vsyscall-syscall.S

Purpose: embeds the linked vDSO syscall/trapa blob into the kernel image as a binary payload.

Important symbols: `vsyscall_trapa_start`, `vsyscall_trapa_end`, and `.incbin "arch/sh/kernel/vsyscall/vsyscall.so"`.

Control flow: no executable logic in this wrapper; it marks the byte range copied by `vsyscall_init` into a page used for process vDSO mappings.

State and persistence: build-time binary inclusion becomes read-only kernel image data and is copied once into `syscall_pages[0]`.

Dependencies and integration: depends on the generated `vsyscall.so` artifact and `vsyscall.c` extern symbols.

Risks: missing or incorrectly linked `vsyscall.so` makes the kernel fail to build or maps invalid vDSO code.

Test signals: successful build, correct symbol bounds, and a non-empty copied vDSO page at boot.
