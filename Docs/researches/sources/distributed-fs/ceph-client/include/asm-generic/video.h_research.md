# sources/distributed-fs/ceph-client/include/asm-generic/video.h

Purpose: generic framebuffer/video I/O helper defaults for architecture `<asm/fb.h>` wrappers.

Important APIs/types/functions: `pgprot_framebuffer`, `video_is_primary_device`, `fb_read{b,w,l,q}`, `fb_write{b,w,l,q}`, `fb_memcpy_fromio`, `fb_memcpy_toio`, and `fb_memset`. The read/write helpers use raw I/O operations rather than ordered endian-swapping accessors.

Control flow: all helpers are inline defaults guarded by `#ifndef`, so architectures can override each function independently.

State and persistence: no owned state. Memory attributes are changed by returning a write-combining `pgprot_t`, and I/O helpers mutate framebuffer memory.

Dependencies and integration points: depends on `linux/io.h`, `mm_types.h`, `pgtable.h`, and type definitions. Used by framebuffer and DRM/fbdev compatibility layers.

Risks: raw framebuffer I/O deliberately allows reordering and no endian conversion; drivers needing ordered MMIO semantics must not use these helpers blindly. Default `video_is_primary_device()` returns false, so platform primary-device detection requires an override.

Test signals: framebuffer console/DRM fbdev smoke tests, architecture compile tests with and without `__raw_readq`, and memory attribute validation for mapped framebuffers.
