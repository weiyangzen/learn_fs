## `sources/distributed-fs/ceph-client/arch/x86/hyperv/mshv-asm-offsets.c`

Purpose: generates assembly offset definitions for `struct mshv_vtl_cpu_context` fields used by VTL transition assembly.

Important APIs and functions: `common()` emits `OFFSET()` records for general-purpose registers and `cr2` when `CONFIG_HYPERV_VTL_MODE` is enabled. The output is post-processed by kbuild into `mshv-asm-offsets.h`.

Control flow: build-time only; no runtime code is intended. `COMPILE_OFFSETS` selects offset-generation behavior.

State and persistence: generated header is a build artifact; no runtime state.

Dependencies and integration points: `<linux/kbuild.h>`, `asm/mshyperv.h`, the Hyper-V Makefile dependency for `mshv_vtl_asm.o`, and `mshv_vtl_asm.S` symbolic offsets.

Risks: missing a field used in assembly or stale generated headers would corrupt register save/restore during VTL return. The config guard must align with assembly inclusion.

Test signals: rebuild after changing `struct mshv_vtl_cpu_context`, generated header contains all referenced offsets, and VTL transition tests preserve registers.
