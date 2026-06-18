# sources/distributed-fs/ceph-client/arch/arm64/kernel/machine_kexec_file.c

Purpose: Provides arm64 `kexec_file_load` support for loader registration, DTB/initrd placement, crash ELF headers, and cleanup.

Important APIs and state: `kexec_file_loaders[]` currently exposes `kexec_image_ops`. `arch_kimage_file_post_load_cleanup()` frees `image->arch.dtb` and ELF headers. `load_other_segments()` adds crash headers, optional initrd, and a generated DTB to the kimage.

Control flow: crash loads first prepare an ELF64 core header after excluding crashkernel ranges, add it as a top-down buffer, and optionally load dm-crypt keys. Initrd is placed above the kernel within a 1GB-aligned up-to-32GB window. A new FDT is allocated and packed, then placed top-down with 2MB alignment. On any failure, segment count is restored and temporary DTB memory is freed.

Dependencies and integration: depends on memblock ranges, crash dump helpers, libfdt, Open Firmware FDT setup, kexec buffer placement, vmalloc/kvfree, and `kexec_image.c` for the kernel image segment.

Risks and test signals: risks are segment rollback bugs, DTB/initrd placement outside boot protocol limits, crash memory exclusion mistakes, leaked ELF headers, or missing cleanup. Test `kexec_file_load` with and without initrd, crash kernels, dm-crypt key loading, small memory placement pressure, and cleanup after failed loads.
