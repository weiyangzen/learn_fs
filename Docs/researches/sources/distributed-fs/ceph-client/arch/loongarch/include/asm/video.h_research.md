<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/video.h

Purpose: provides LoongArch video/framebuffer memory helpers and platform defaults.
Important APIs and types: declares `screen_info` handling and architecture helpers for framebuffer physical/virtual mapping where needed.
Control flow: sysfb/simplefb/EFI BGRT and console drivers consult these helpers during early graphics setup.
State and persistence: framebuffer descriptors and primary display data persist after EFI/firmware discovery.
Dependencies and integration: integrates with EFI primary display parsing, sysfb, fbdev/simpledrm, and boot console code.
Risks and test signals: wrong memory attributes or addresses break early display. Signals include EFI framebuffer boot, simpledrm handoff, and console display tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/video.h -->
