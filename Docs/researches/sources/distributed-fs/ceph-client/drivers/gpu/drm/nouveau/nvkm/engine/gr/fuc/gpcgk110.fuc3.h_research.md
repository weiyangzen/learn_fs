# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk110.fuc3.h

Purpose: this header embeds GK110 GPCCS FUC3 firmware for Kepler GPC context-control tasks. It defines `gk110_grgpc_data[]` and `gk110_grgpc_code[]`, which the GK110 GR driver loads into GPCCS to execute GPC-local portions of graphics context switching.

Important APIs/types/functions: the only C interface is the static data/code arrays. `gk110.c` includes the header and publishes it as `struct gf100_gr_ucode gk110_gr_gpccs_ucode`. Labeled firmware blocks include queue helpers, register read/write waits, MMIO context sizing and transfer, strand setup, `init_unk_loop`, wait/main loops, interrupt handling, hub barrier completion, redswitch delay, and context-transfer load/save completion.

Control flow: the firmware follows the later Fermi/Kepler GPCCS pattern: initialize topology and unknown units, idle in `wait/main`, accept hub commands through the queue, execute MMIO or strand transfer subroutines, signal `hub_barrier_done`, and return to the main loop after `ctx_xfer_done`. The label map matches GK104 closely, but the binary is chip-specific.

State and persistence: `gk110_grgpc_data[]` uses the `0x6c` data layout with GPC/TPC/unknown MMIO list heads and tails, `gpc_id`, `tpc_count`, `tpc_mask`, `unk_count`, `unk_mask`, and command queue storage at `0x0024`. The kernel image stores the initial data; live state exists in GPCCS data memory after upload.

Dependencies and integration points: this GPCCS image pairs with `hubgk110.fuc3.h` FECS firmware and the GK110 graphics engine functions. It depends on the shared GF100 firmware loader ABI through `struct gf100_gr_ucode`.

Risks: GPCCS and FECS firmware must agree on queue layout and barrier protocol. A size, prefix, or code-word mistake can cause initialization failure, hangs during `ctx_xfer`, or per-GPC state corruption. Similarity to GK104 should not be treated as interchangeability.

Test signals: expected signals are successful GK110 GR firmware load, no GPCCS error/timeout during channel creation or switching, correct GPC/TPC mask handling on partially fused chips, and stable rendering/compute workloads across repeated context switches.
