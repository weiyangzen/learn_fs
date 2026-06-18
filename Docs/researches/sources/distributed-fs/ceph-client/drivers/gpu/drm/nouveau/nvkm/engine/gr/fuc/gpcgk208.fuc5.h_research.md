# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk208.fuc5.h

Purpose: this header embeds GK208 GPCCS firmware using the FUC5 instruction encoding. It defines `gk208_grgpc_data[]` and `gk208_grgpc_code[]` for GPC-side context-control work on GK208 graphics hardware.

Important APIs/types/functions: `gk208.c` includes the header and exposes the arrays through `static struct gf100_gr_ucode gk208_gr_gpccs_ucode`. Firmware labels show the same conceptual routines as FUC3 images, but at different offsets and with FUC5 opcodes: queue helpers, MMIO read/write/wait helpers, `mmctx_size`, `mmctx_xfer`, strand operations, `init_unk_loop`, `main`, `ih`, `hub_barrier_done`, `ctx_redswitch`, and `ctx_xfer`.

Control flow: the firmware initializes GPC/TPC/unknown topology, waits for commands from FECS/hub firmware, performs MMIO/strand context transfers, handles interrupts and no-FIFO cases, reports hub barrier completion, and finalizes transfer state. Compared with FUC3 Kepler images, offsets are compressed/shifted and the word count is smaller, reflecting the FUC5 encoding rather than a C-level API change.

State and persistence: `gk208_grgpc_data[]` keeps the `0x6c` layout with GPC/TPC/unknown list heads/tails, IDs, masks, counts, and an 18-word command queue. This state is loaded into GPCCS data memory and mutated by firmware while the static array remains the kernel-side source.

Dependencies and integration points: it pairs with `hubgk208.fuc5.h` and is selected by the GK208 GR implementation. The shared GF100 GR ucode loader uses the array sizes, so the code/data definitions are the binding contract.

Risks: FUC5 instruction streams are opaque and architecture-specific. Accidentally treating the file as equivalent to FUC3 GK104/GK110 firmware, altering a branch target word, or changing data offsets can break GPCCS boot or context transfer. The smaller image still depends on the same hub/GPC queue protocol.

Test signals: GK208 hardware should load FECS and GPCCS FUC5 images, initialize topology, handle channel switches, and run graphics workloads without GPCCS hangs, barrier stalls, or context-transfer faults.
