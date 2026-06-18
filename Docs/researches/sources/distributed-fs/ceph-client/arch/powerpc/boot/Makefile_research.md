# sources/distributed-fs/ceph-client/arch/powerpc/boot/Makefile

## Purpose
Build system for PowerPC boot wrappers and image formats. It compiles the small pre-kernel runtime, copies decompressor/libfdt sources, selects platform wrappers, invokes the `wrapper` script, and installs boot-wrapper utilities.

## Important APIs, Types, And Control Flow
The makefile defines `BOOTCC`, `BOOTAR`, 32/64-bit boot target flags, soft-float/no-vector flags, generated zlib/libfdt source copies, boot wrapper library sources (`src-wlib-*`), platform sources (`src-plat-*`), host utilities (`addnote`, `hack-coff`, `mktree`), wrapper targets, compressor selection, board image lists, initrd variants, and install targets. Pattern rules build `zImage`, `uImage`, `cuImage`, `dtbImage`, `simpleImage`, and `treeImage` variants, optionally embedding DTBs and initrds.

## State, Dependencies, Risks, And Tests
State is generated object/image files under `arch/powerpc/boot`, copied decompressor/libfdt sources, installed wrapper assets, and symlinked `zImage`. Dependencies include kbuild, DTC output, `wrapper`, libfdt, kernel compression selections, board Kconfig symbols, and cross32 tools. Risks include wrong `-m32/-m64` wrapper ABI, missing copied headers, stale clean-files, DTB path ambiguity between `dts/` and `dts/fsl/`, and default image fallback to `vmlinux.strip` when no platform image is selected. Test with representative `zImage`, `uImage`, `cuImage.*`, `dtbImage.*`, initrd, install, and clean targets for ppc32, ppc64, and ppc64 boot-wrapper configs.
