# sources/distributed-fs/ceph-client/arch/sparc/include/asm/video.h

Purpose: SPARC architecture header `video.h` providing low-level declarations, constants, or inline helpers for kernel subsystems.

Important APIs/types/functions: types `device`; functions/helpers `pgprot_framebuffer`, `video_is_primary_device`, `fb_memcpy_fromio`, `fb_memcpy_toio`, `fb_memset_io`; macros/constants `_SPARC_VIDEO_H_`, `pgprot_framebuffer`, `video_is_primary_device`, `fb_memcpy_fromio`, `fb_memcpy_toio`, `fb_memset`.

Control flow: The file is driven by preprocessor gates such as `_SPARC_VIDEO_H_`, `CONFIG_SPARC32`, `CONFIG_VIDEO`; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: State effects are primarily compile-time definitions and external architectural state accessed by the declared helpers; implementation style is preprocessor/C declarations.

Dependencies and integration points: Includes/dependencies: `linux/io.h`, `linux/types.h`, `asm/page.h`, `asm-generic/video.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Architecture defconfig/allmodconfig builds plus subsystem users of the exported symbols are the main test signals.
