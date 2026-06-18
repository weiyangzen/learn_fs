# sources/distributed-fs/ceph-client/drivers/media/platform/ti/vpe/vpdma.h

Purpose: public VPDMA helper API and shared format/channel contract for TI VPE/VIP drivers. It exposes descriptor buffer/list state, VPDMA format tables, channel identifiers, descriptor flags, ADB helpers, list management, descriptor builders, interrupt helpers, client configuration, and VPDMA initialization.

Important APIs/types: `struct vpdma_buf`, `struct vpdma_desc_list`, and `struct vpdma_data` are the core state carriers. `struct vpdma_data_format` describes hardware data type/depth for YUV, RGB, raw, and misc formats. `enum vpdma_channel` names the VPE channels also reused by VIP output channel mapping. `VPDMA_SET_MMR_ADB_HDR()` and related macros fill address-data-block headers for register writes. Function prototypes cover buffer map/unmap, descriptor list submit/reuse/cleanup, hardware-list allocation, CFD/CTD/DTD emission, list IRQ masking/status, CSTAT line/frame-start programming, max-size/background configuration, register dump, and firmware/create.

Control flow: clients include this header, allocate a `struct vpdma_data`, initialize it with `vpdma_create()` or `vpdma_load_firmware()`, allocate descriptor/config buffers, append descriptors using the builder APIs, submit lists, and clear/listen for list-complete interrupts. VIP additionally uses hardware-list slots to map VPDMA list numbers back to `struct vip_stream`.

State and persistence: the header makes explicit which software state must survive across submissions: descriptor buffers must not be freed while mapped, `list->next` tracks append position, `hwlist_used[]` and `hwlist_priv[]` persist list ownership, and firmware callback state persists in `vpdma_data`.

Dependencies and integration: includes no large framework headers itself, but prototypes use DMA addresses, `platform_device`, V4L2 rectangles, and VPDMA private channel/client concepts. It is the shared ABI between `vpdma.c`, `vpe.c`, and `vip.c`.

Risks: channel constants mix VPE enum IDs with VIP raw channel offsets, so users must distinguish enum channel inputs from raw numeric channel inputs. `VPDMA_MAX_CHANNELS` is large enough for bitmap-style arrays but not type-safe. Descriptor and stride alignments are compile-time constants that callers must honor before hardware submission. ADB helper macros use pointer arithmetic through typed null pointers and require payload subblocks to be 16-byte aligned by the caller.

Test signals: compile all TI VPE/VIP users, check exported symbol availability when `CONFIG_VIDEO_TI_VPDMA=m`, run descriptor list creation/submission paths, validate packed/coplanar/raw format table indexing, and verify VPDMA list allocation/release under repeated video node registration/removal.
