# sources/distributed-fs/ceph-client/arch/powerpc/boot/dts/Makefile

Purpose: declares the PowerPC boot device-tree source inventory for the kernel build system.

Important APIs/types/functions: build variables/targets `subdir-y`, `dtb-$(CONFIG_OF_ALL_DTBS)`. Source size is 5 lines / 139 bytes.

Control flow is build-time rather than runtime: make, sed, shell, or helper tools transform source artifacts into DTBs, wrapper objects, linked zImages, or installable files.

State and persistence: State is filesystem output and build variables: generated DTBs, temporary objects, compressed kernels, linked images, or installed files. It does not persist runtime kernel state.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are Kbuild, dtc, objcopy, ld, nm, mkuboot.sh, file-size.sh, installkernel, and platform-specific post-processing tools.

Risks and test signals: Risks include host-tool incompatibility, quoting/path problems, stale cached compressed payloads, wrong link address, or generated image formats that firmware rejects. Test signals are `make zImage` variants, dtc compile coverage, objdump/nm section checks, and boot smoke tests on each image class.
