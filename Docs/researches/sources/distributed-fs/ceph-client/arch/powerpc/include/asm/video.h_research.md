<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/video.h

Purpose: Supplies PowerPC framebuffer page-protection selection before falling back to generic video helpers.

Important APIs/types/functions: `pgprot_framebuffer()` and `#define pgprot_framebuffer pgprot_framebuffer`.

Control flow: Framebuffer mmap code calls `pgprot_framebuffer()`, which delegates to `__phys_mem_access_prot()` using the physical PFN and mapping length.

State and persistence: No persistent state. It computes page protections for user mappings of framebuffer memory.

Dependencies and integration points: Depends on `asm/page.h` and generic video header; integrated by framebuffer and DRM mmap paths.

Risks: Incorrect cacheability/guarded attributes can produce stale display contents or unsafe MMIO caching.

Test signals: Framebuffer mmap tests, display driver smoke tests, and build coverage across PowerPC memory-management configurations.

Source read size: 17 lines, 431 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/video.h -->
