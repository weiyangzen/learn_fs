# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgf100.fuc3.h

Purpose: this header embeds the GF100 GPCCS/GPC falcon firmware image used by the Fermi GF100 graphics engine. It provides `gf100_grgpc_data[]`, the firmware data segment, and `gf100_grgpc_code[]`, the instruction image that manages GPC-side context initialization, MMIO context transfers, strand setup, interrupt handling, and hub barrier synchronization.

Important APIs/types/functions: there are no C functions; the API is the two static `uint32_t` arrays. `gf100.c` includes this header and exposes the arrays through `struct gf100_gr_ucode gf100_gr_gpccs_ucode` with `.code.data/.code.size` and `.data.data/.data.size`. The firmware labels in comments identify routines such as `queue_put`, `queue_get`, `nv_rd32`, `nv_wr32`, `mmctx_size`, `mmctx_xfer`, `strand_ctx_init`, `init`, `main`, `ih`, `ctx_redswitch`, and `ctx_xfer`.

Control flow: the code image starts with queue helpers, MMIO read/write/wait helpers, context-size and context-transfer helpers, strand initialization, error handling, firmware `init`, wait/main loops, interrupt handling, a hub barrier acknowledgement at `hub_barrier_done`, redswitch delay handling, and context transfer load/save paths. GF100 lacks the later `unk_count`/`unk_mask` fields and `init_unk_loop` present in GF117/GK104/GK110 headers.

State and persistence: `gf100_grgpc_data[]` stores list head/tail offsets for GPC/TPC/unknown MMIO lists at `0x64`, `gpc_id`, `tpc_count`, `tpc_mask`, and an 18-word command queue starting at `0x001c`. The kernel loads this data into GPCCS data memory; firmware mutates queue and topology fields while it runs. The arrays persist in the kernel image as immutable source data.

Dependencies and integration points: this image pairs with `hubgf100.fuc3.h` FECS firmware. The GF100 GR init path loads both images to coordinate hub-level channel switching and GPC-level context state movement. The labels mirror shared falcon firmware concepts used by later GF117/GK/GM images.

Risks: this is opaque machine code. Any edit to a word, symbol name, array size, or data offset can prevent GPCCS boot, desynchronize the FECS/GPCCS command queue, or corrupt context images. Because GF100 has a slightly smaller data layout than later Fermi/Kepler GPC firmware, copying later offsets into this file would be unsafe.

Test signals: GF100 hardware should complete GR context-control initialization, load GPCCS firmware, execute context transfers, acknowledge hub barriers, and switch channels under 3D workloads without GPCCS watchdogs, firmware error labels, or PGRAPH context faults.
