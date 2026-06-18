# sources/distributed-fs/ceph-client/include/media/drv-intf/saa7146_vv.h

Purpose: Video/VBI layer definitions for SAA7146 bridge devices, covering DMA queues, pixel formats, standards, V4L2 ioctl hooks, resource locking, and capture programming helpers.

Important APIs/types/functions: Types include `saa7146_video_dma`, `saa7146_format`, `saa7146_standard`, `saa7146_buf`, `saa7146_dmaqueue`, `saa7146_vv`, `saa7146_ext_vv`, and `saa7146_use_ops`. APIs register/unregister video devices, queue/finish/advance buffers, handle timeouts, initialize/release VV support, program capture/DMA/HPS/GPIO, expose video/VBI ioctl and vb2 ops, and manage DMA resources. Defines resource bits, HPS source/sync, clipping modes, hardware pixel format encodings, planar detection, and byte-swap modes.

Control flow: Extension data advertises inputs, audio count, standards, flags, and optional callbacks. Capture queues hold `saa7146_buf` instances with per-plane page tables; buffer activation programs DMA/RPS, timer expiry marks failures, and IRQ completion advances queues.

State and persistence: `saa7146_vv` stores active VBI/video queues, formats, timers, sequence number, standard, flip/source/sync settings, and resource bitmask. Buffers own DMA page tables until completion/release.

Dependencies and integration: Depends on SAA7146 core, V4L2 ioctl/filehandle/common APIs, and videobuf2 DMA-SG. It bridges PCI core support to V4L2 capture devices.

Risks and test signals: Risks include buffer timeout races, resource leaks, incorrect planar/byte-swap programming, standard geometry mismatches, and shared setting semantics across opens. Test video and VBI streaming, queue cancellation, timeout recovery, resource contention, standard switching, clipping, and all advertised formats.
