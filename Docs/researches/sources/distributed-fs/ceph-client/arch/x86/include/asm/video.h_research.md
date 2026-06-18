# sources/distributed-fs/ceph-client/arch/x86/include/asm/video.h

Purpose: Provides x86 architecture hooks for framebuffer page protections and primary video-device detection.

Important APIs/types/functions: `pgprot_framebuffer(pgprot_t prot, unsigned long vm_start, unsigned long vm_end, unsigned long offset)` adjusts mmap protections for framebuffer memory and is exported via a macro of the same name. Under `CONFIG_VIDEO`, `video_is_primary_device(struct device *dev)` is declared and similarly advertised. The header then includes `asm-generic/video.h` for fallback/default behavior.

Control flow: Driver or generic video code calls the architecture hook to choose page attributes for framebuffer mappings and optionally to identify the primary display device.

State and persistence: No local state. The hooks affect VMA/page-protection decisions and device selection state elsewhere.

Dependencies and integration points: Depends on `linux/types.h`, `asm/page.h`, `struct device`, and generic video hooks. It integrates with DRM/fbdev/video driver mmap paths.

Risks: Wrong framebuffer cache/encryption attributes can cause display corruption, performance issues, or unsafe MMIO caching. Primary-device logic affects console handoff.

Test signals: Framebuffer mmap tests, boot console handoff, DRM/fbdev primary device detection, and builds with/without `CONFIG_VIDEO`.
