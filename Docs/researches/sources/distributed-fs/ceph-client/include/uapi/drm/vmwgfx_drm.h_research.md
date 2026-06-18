# sources/distributed-fs/ceph-client/include/uapi/drm/vmwgfx_drm.h

## Purpose
This header defines the VMware SVGA/vmwgfx DRM UAPI. It is a broad virtual GPU ABI for querying device capabilities, allocating host-visible BOs, creating contexts/surfaces/shaders, submitting SVGA command buffers, managing fences/events, presenting surfaces, synchronizing CPU access, updating display layout, sending guest messages, and exporting MKS statistics.

## Important APIs and types
The ioctl command IDs span `GET_PARAM`, BO allocation/handle close, cursor bypass, overlay streams, context create/unref, legacy and guest-backed surface create/ref/unref, `EXECBUF`, 3D caps, fence wait/signaled/unref/event, present/readback, layout update, shader create/unref, CPU sync, extended context create, extended GB surface create/ref, message, and MKSSTAT reset/add/remove. `drm_vmw_getparam_arg` exposes stream counts, 3D support, FIFO and hardware caps, max memory/object sizes, screen targets, DX/SM/GL support, and device ID. Surface structs distinguish legacy surfaces with face/mip arrays from guest-backed surfaces with backup buffers, scanout/coherent flags, array sizes, and extended 64-bit SVGA flags. `drm_vmw_execbuf_arg` submits userspace SVGA commands, supports throttle, context handle, fence import/export fds, and returns `drm_vmw_fence_rep`.

## Control flow and state
Userspace queries capabilities, allocates BOs, creates contexts and surfaces, builds SVGA command buffers that reference host-visible handles, submits through `EXECBUF`, and receives fence data for wait/poll/event synchronization. Display paths present surfaces to framebuffers or read back clips. CPU access to BOs is explicitly bracketed by `SYNCCPU` grab/release. Advanced paths create DX contexts, shaders, guest-backed surfaces, and MKS stats records. Overlay stream ioctls claim/control/unref streams when stream support exists.

## State and persistence behavior
Contexts, surfaces, shaders, streams, BO handles, and MKS stat records are persistent resources until unreferenced/closed/removed. Fence handles and sequence numbers persist as synchronization objects; sequence numbers can wrap, so `passed_seqno` is part of the ABI. CPU sync grabs block or constrain command submissions referencing a BO until release or fd close. Guest-backed surfaces may own or reference backup buffers and expose map handles. Layout updates persist preferred connector modes/positions.

## Dependencies and integration points
The header depends on `drm.h`, SVGA3D host command semantics, VMware FIFO capability pages, DRM events, GEM/BO mmap offsets, dma-fence fd import/export, framebuffer/present paths, and userspace drivers such as Mesa svga. It also integrates with guest/host communication through `DRM_VMW_MSG` and with MKS guest statistics shared pages.

## Risks and test signals
Risks include very wide ABI surface, legacy aliasing of DMABUF and BO ioctls, command-buffer pointer validation, fence error tri-state handling, sequence wraparound, surface ref/create union layout, CPU sync deadlocks, coherent-surface semantics, and page-aligned MKS stats pointers. Tests should cover getparam gates, BO allocation/mmap/handle close, context/surface/shader lifecycle, execbuf fence import/export and error paths, fence wait/signaled/event behavior, present/readback clips, synccpu grab/release flags, extended surface fields/MBZ validation, message send/receive lengths, and MKS stat add/remove/reset.
