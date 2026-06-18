# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-driver.h

## Purpose
`ivtv-driver.h` is the central internal header for the ivtv driver. It defines the CX23415/CX23416 memory map, stream types, debug macros, options, mailbox and DMA structures, stream queue state, VBI/YUV state, the main `struct ivtv`, register access macros, subdevice call wrappers, and core prototypes.

## Important APIs, Types, and Functions
Important types are `ivtv_options`, `ivtv_mailbox`, `ivtv_mailbox_data`, `ivtv_api_cache`, `ivtv_buffer`, `ivtv_queue`, `ivtv_stream`, `ivtv_open_id`, `ivtv_user_dma`, `vbi_info`, `yuv_playback_info`, and `ivtv`. It defines per-buffer, per-stream, and per-device bit flags, output modes, stream type IDs, register offsets, `file2id()`, `to_ivtv()`, `ivtv_raw_vbi()`, `read_reg()`/`write_reg()`/sync variants, and `ivtv_call_hw()` wrappers.

## Control Flow
The header controls behavior through flags and macros rather than functions. Stream and device flags drive capture, decode, DMA, PIO, VBI insertion, firmware initialization, and event handling. Register macros assume local functions have an `itv` pointer in scope and map symbolic operations onto MMIO access.

## State and Persistence
`struct ivtv` is the full runtime state container: PCI/V4L2 identity, card descriptor pointers, MMIO mappings, controls, standards, locks, streams, counters, ALSA hooks, IRQ worker state, DMA state, mailbox/cache state, I2C adapter/client state, program index cache, VBI and YUV data, and OSD/ivtvfb hooks. The state is volatile and rebuilt on probe/first open.

## Dependencies and Integration Points
This header pulls in Linux PCI, interrupt, I2C, scatterlist, kthread, locking, user access, and V4L2/cx2341x/tuner/IR interfaces. Nearly every ivtv source file depends on it, and exported symbols in `ivtv-driver.c` expose selected helpers to ivtvfb, ivtv-alsa, and IR support.

## Risks and Edge Cases
Because this header centralizes layout and flags, mistakes have broad effects. Some flag values are shared or surprising, such as `IVTV_F_S_PIO_HAS_VBI` reusing bit 1 like the DMA VBI flag. MMIO macros depend on implicit variable naming and do not perform bounds checks. Large embedded arrays in `struct ivtv` make allocation size and zero-initialization assumptions important.

## Test Signals
Build all ivtv objects and extension modules to catch signature drift. Runtime validation should cover stream flag transitions, DMA/PIO queue movement, VBI raw versus sliced mode decisions, register sync behavior on real hardware, firmware mailbox access, YUV/OSD state restoration, and concurrent open/close/read/write paths.
