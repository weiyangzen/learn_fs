# sources/distributed-fs/ceph-client/arch/powerpc/boot/wrapper

Purpose: is the shell build driver that turns vmlinux plus optional initrd/FDT/ESM blobs into platform-specific PowerPC zImage formats.

Important APIs/types/functions: functions `ld_version`, `addsec`; build variables/targets `kernel`, `ofile`, `platform`, `initrd`, `dtb`, `dts`, `esm_blob`, `cacheit`, `binary`, `compression`, `uboot_comp`, `pie`, and 29 more. Source size is 577 lines / 14058 bytes.

Implementation notes: The script parses platform, compression, object directory, working directory, initrd, dtb/dts, and ESM options; derives the ELF format; selects platform objects/linker scripts; strips/compresses vmlinux; adds payload sections with objcopy; links; then post-processes uboot, cuBoot, treeboot, PS3, pSeries, CHRP, and COFF outputs.

Control flow is build-time rather than runtime: make, sed, shell, or helper tools transform source artifacts into DTBs, wrapper objects, linked zImages, or installable files.

State and persistence: State is filesystem output and build variables: generated DTBs, temporary objects, compressed kernels, linked images, or installed files. It does not persist runtime kernel state.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are Kbuild, dtc, objcopy, ld, nm, mkuboot.sh, file-size.sh, installkernel, and platform-specific post-processing tools.

Risks and test signals: Risks include host-tool incompatibility, quoting/path problems, stale cached compressed payloads, wrong link address, or generated image formats that firmware rejects. Test signals are `make zImage` variants, dtc compile coverage, objdump/nm section checks, and boot smoke tests on each image class.
