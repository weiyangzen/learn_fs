
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgm107.fuc5.h

## Purpose
Embeds the GM107 FECS/HUB Falcon microcode image used by the Nouveau graphics engine when the driver uses built-in context-control firmware rather than loading an external firmware file. The header provides both the DMEM seed data and IMEM instruction words consumed by `gm107.c`.

## Important APIs, types, and functions
- Defines `static uint32_t gm107_grhub_data[]`, a structured DMEM image with annotated offsets such as `hub_mmio_list_head`, `hub_mmio_list_tail`, `gpc_count`, `rop_count`, `cmd_queue`, `ctx_current`, `chan_data`, `chan_mmio_count`, `chan_mmio_address`, `xfer_data`, and `hub_mmio_list_base`.
- Defines `static uint32_t gm107_grhub_code[]`, the FECS instruction image with labels in comments for queue operations, MMIO read/write helpers, wait helpers, context-size calculation, context transfer, strand setup, interrupt handling, and initialization.
- The arrays are wrapped by `struct gf100_gr_ucode gm107_gr_fecs_ucode` in `gm107.c`.

## Control flow
There is no C control flow in the header, but the encoded Falcon program implements the runtime control flow for GM107 FECS. `gf100_gr_init_ctxctl_int()` loads the `data` array into FECS DMEM and the `code` array into FECS IMEM, then starts the HUB Falcon. The microcode initializes GPCs, maintains command queues, handles context switch requests, executes per-channel MMIO lists, transfers context data, and reports bad firmware-method commands with the error values declared in `os.h`.

## State and persistence
The file contains static immutable image data compiled into the kernel object. At runtime it becomes mutable Falcon DMEM/IMEM state after being copied to hardware. The seeded DMEM slots persist only while the FECS Falcon is loaded and running; per-channel context state lives in graphics context memory and the channel MMIO-list buffer prepared by `gf100_gr_chan_new()`.

## Dependencies and integration points
Included directly by `gm107.c`. It depends on the context-control ABI expected by `gf100_gr_init_csdata()`, `gf100_gr_fecs_bind_pointer()`, `gf100_gr_fecs_wfi_golden_save()`, and the `gf100_gr_chan_bind()` context image layout. It also depends on the error-code contract from `fuc/os.h`.

## Risks
The image is opaque machine code; C-level review cannot prove correctness. Register offsets, DMEM offsets, and context image conventions must match `ctxgf100` helpers and GM107 hardware. Any accidental edit can make GR initialization or context switching fail with FECS timeouts. Built-in firmware can diverge from NVIDIA external firmware behavior.

## Test signals
Useful signals are successful `gf100_gr_init_ctxctl_int()` startup, nonzero context image size at `0x409804`, absence of FECS watchdog or ucode error logs, successful channel context generation, and correct GR context switching under graphics and compute workloads.
