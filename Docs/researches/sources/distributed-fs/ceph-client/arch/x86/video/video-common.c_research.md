<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/video/video-common.c -->
# sources/distributed-fs/ceph-client/arch/x86/video/video-common.c

## Purpose
`video-common.c` provides common x86 framebuffer page-protection and primary-display detection helpers.

## Important APIs, types, and functions
Exports `pgprot_framebuffer()` and `video_is_primary_device()`.

## Control flow
Framebuffer mappings clear cache mode bits and use UC-minus on CPUs newer than 386. Primary-device detection checks PCI display class, VGA default device, and optionally whether PCI BARs overlap resources derived from `screen_info`.

## State and persistence behavior
No long-lived state is local; it reads `boot_cpu_data`, `sysfb_primary_display`, VGA arbiter state, and PCI resources.

## Dependencies and integration points
It depends on PCI, sysfb/screen_info, VGA arbitration, cache-mode helpers, and `asm/video.h`.

## Risks and edge cases
Cache attributes affect framebuffer correctness/performance. Primary detection can be wrong if firmware screen_info resources do not match PCI BARs.

## Test signals
Signals are framebuffer mmap behavior, boot console handoff, DRM/fbdev primary-device selection, and PCI resource matching tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/video/video-common.c -->
