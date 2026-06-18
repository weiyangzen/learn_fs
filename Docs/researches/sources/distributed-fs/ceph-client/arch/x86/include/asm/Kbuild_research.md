## `sources/distributed-fs/ceph-client/arch/x86/include/asm/Kbuild`

Purpose: declares generated x86 UAPI/internal headers and generic asm header fallbacks for kbuild.

Important build rules: generated headers include ORC hash, syscall tables for 32/64/x32, IA32/x32 unistd compatibility, Xen hypercalls, and CPU feature masks. Generic fallbacks include `early_ioremap.h`, `fprobe.h`, `mcs_spinlock.h`, and `mmzone.h`.

Control flow: build-time only; kbuild uses these lists to generate or export headers.

State and persistence: generated headers are build artifacts.

Dependencies and integration points: syscall generation, ORC unwinder tooling, Xen, CPU feature mask generation, and generic asm-generic headers.

Risks: omitting a generated header breaks include dependencies; wrongly using a generic fallback may hide missing x86-specific behavior.

Test signals: clean allmodconfig/defconfig builds, header install checks, syscall table generation, and ORC tooling builds.
