# sources/distributed-fs/ceph-client/arch/powerpc/Kbuild

## Purpose
Top-level kbuild directory selection for the PowerPC architecture.

## Important APIs, Types, And Control Flow
The file applies `-Werror`/assembler fatal warnings when `CONFIG_PPC_WERROR` is set, always descends into core directories (`kernel`, `mm`, `lib`, `sysdev`, `platforms`, `math-emu`, `crypto`, `net`), and conditionally descends into `xmon`, `kvm`, `perf`, `kexec`, and `purgatory`. `subdir- += boot tools` ensures cleaning reaches non-recursive utility directories.

## State, Dependencies, Risks, And Tests
State is build graph only. Dependencies are Kconfig symbols and kbuild recursion. Risks include omitted subdirectories causing missing object files, or `CONFIG_PPC_WERROR` making older toolchains fail. Test signals are allnoconfig/defconfig/allmodconfig PowerPC builds, clean targets removing boot/tool artifacts, and toggling optional features.
