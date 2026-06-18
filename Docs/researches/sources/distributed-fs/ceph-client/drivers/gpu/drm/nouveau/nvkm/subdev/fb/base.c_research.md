<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/base.c

## Purpose
Common NVKM framebuffer subdevice implementation. It owns framebuffer construction, lifecycle, tile/comptag setup, RAM allocation/init, VPR scrub dispatch, system-memory flush-page setup, and generic wrappers around generation function tables.

## Important APIs, Types, And Functions
Public helpers include `nvkm_fb_ctor()`, `nvkm_fb_new_()`, `nvkm_fb_tile_init()`, `nvkm_fb_tile_prog()`, `nvkm_fb_tile_fini()`, `nvkm_fb_bios_memtype()`, `nvkm_fb_mem_unlock()`, and `nvkm_fb_vidmem_size()`. The `nvkm_subdev_func` instance supplies dtor/preinit/oneinit/init/intr.

## Control Flow
Oneinit constructs RAM through `func->ram_new`, runs optional generation oneinit, computes compression tags, and initializes the tag allocator. Init initializes RAM, reprograms all tile regions, initializes system-memory flush handling, runs generation init/remapper/page/unknown hooks, and returns errors for failed page setup. Teardown releases MMU scratch memory, tile state, tag allocator, RAM, VPR scrub firmware, and DMA flush page.

## State And Persistence
Persistent state lives in `struct nvkm_fb`: RAM object, tile regions, tag allocator, sysmem flush page, MMU read/write memory, and VPR scrubber firmware. Hardware state persists through tile registers, RAM controller registers, remapper/page setup, and VPR lock state.

## Dependencies And Integration Points
Depends on NVKM subdev lifecycle, BIOS M0203 RAM type parsing, core options, GR/MPEG tile notification, RAM helpers, MM allocator, DMA mapping, and VPR firmware hooks. It is the common base under every generation wrapper.

## Risks
Lifecycle ordering is critical: RAM must exist before tile/tag use, VPR scrub may require oneinit, and tile programming notifies engines that may or may not exist. BIOS memory type fallback to unknown affects downstream timing/reclocking. Flush page DMA cleanup must match allocation.

## Test Signals
Signals include framebuffer probe logs with RAM type/size, successful `nvkm_mm_init()` for tags and VRAM, tile programming without engine errors, VPR locked/unlocked messages, and suspend/resume init/fini stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fb/base.c -->
