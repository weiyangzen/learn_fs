<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/video.h -->
# sources/distributed-fs/ceph-client/arch/parisc/include/asm/video.h

Source read size: 16 lines, 353 bytes.

Purpose: provides the PA-RISC hook for selecting the primary video device when STI core and generic video support are enabled. Important APIs: optional `video_is_primary_device(struct device *)` override plus generic video inclusion. Control flow: generic video helpers call the architecture hook only in enabled configurations; otherwise behavior falls back to `asm-generic/video.h`. State and persistence: no state here. Dependencies and integration points: depends on `CONFIG_STI_CORE`, `CONFIG_VIDEO`, generic video, and PA-RISC STI console/video drivers. Risks: wrong primary-device selection can choose the wrong framebuffer/console on systems with multiple display devices. Test signals: boot console selection, framebuffer registration order, multi-GPU/STI systems, and build coverage with and without STI/video enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/parisc/include/asm/video.h -->
