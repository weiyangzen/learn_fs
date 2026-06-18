## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hwcap.h

Purpose: defines arm64 HWCAP bit positions and compatibility HWCAP exposure.

Important APIs/types/functions: declares compat HWCAP/HWCAP2 bits, kernel HWCAP mapping macros for HWCAP/HWCAP2/HWCAP3, includes generated `kernel-hwcap.h`, defines `ELF_HWCAP*`, compat HWCAP globals, and enumerates internal hardware capability indices.

Control flow: cpufeature code sets HWCAP bits; ELF/auxv code reads them through macros.

State and persistence: global compat HWCAP variables and kernel capability bitmaps persist; user processes see values in auxv.

Dependencies and integration: integrates cpufeature, ELF loader, `/proc/cpuinfo`, compat AArch32 ABI, and userspace feature discovery.

Risks: changing bit positions breaks userspace ABI. Test signals are auxv HWCAP tests, glibc/hwcap probing, compat program startup, and feature-specific selftests.
