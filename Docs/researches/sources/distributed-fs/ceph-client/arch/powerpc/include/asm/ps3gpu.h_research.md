# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/ps3gpu.h

Purpose: This header defines PS3 GPU LV1 context-attribute constants and inline wrappers used by framebuffer/video code to synchronize display, flip buffers, set up framebuffer memory, blit, and close framebuffer state.

Important APIs/types/functions: Constants include display sync/flip attributes, framebuffer setup/blit/sync/close attributes, blit wait flag, and HSYNC/VSYNC sync selectors. `ps3_gpu_mutex` is declared as the mutex synchronizing GPU accesses and video mode changes. Inline wrappers call `lv1_gpu_context_attribute`: `lv1_gpu_display_sync`, `lv1_gpu_display_flip`, `lv1_gpu_fb_setup`, `lv1_gpu_fb_blit`, and `lv1_gpu_fb_close`.

Control flow: GPU/framebuffer code locks around mode or GPU access, calls LV1 context-attribute wrappers with a context handle and offsets/LPAR addresses, waits or syncs as needed, flips display heads, and closes framebuffer mappings at teardown.

State and persistence: The mutex serializes shared GPU/video state. Persistent state resides in LV1 GPU context handles, DDR/XDR/ioif offsets, and framebuffer setup configured by hypervisor calls.

Dependencies and integration points: It includes `linux/mutex.h` and `asm/lv1call.h`, integrating PS3 framebuffer and AV/video mode code with the LV1 hypervisor GPU interface.

Risks and test signals: Incorrect offsets or context handles can corrupt display memory or fail LV1 calls. Missing mutex coverage can race mode changes with blits/flips. Tests include framebuffer setup/close, display flip on both heads, sync modes, blit with/without wait flag, video mode changes under load, and LV1 error propagation.
