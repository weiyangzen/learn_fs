# subset-b-003679 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv50.c

Purpose: `ctxnv50.c` builds the NV50-family PGRAPH context-switch program (`ctxprog`) and the initial per-channel graphics context image (`ctxvals`). NV50 hardware performs graphics context switches itself, but the driver must supply the microcode sequence and a correctly sized/defaulted context buffer; without both, Nouveau disables acceleration because 3D/CUDA state cannot be reliably switched or initialized.

Important APIs/types/functions: the exported entry points are `nv50_grctx_init(struct nvkm_device *, u32 *size)` and `nv50_grctx_fill(struct nvkm_device *, struct nvkm_gpuobj *)`. Both drive the private `nv50_grctx_generate(struct nvkm_grctx *)`, which emits either context-program words (`NVKM_GRCTX_PROG`) or context values (`NVKM_GRCTX_VALS`) depending on `ctx->mode`. It uses helper op encoders from `ctxnv40.h` such as `cp_set`, `cp_bra`, `cp_out`, `cp_wait`, `cp_ctx`, `cp_lsr`, and `cp_pos`, plus `gr_def` for default register values. Hardware access is through `nvkm_rd32`, `nvkm_wr32`, and `nvkm_wo32`.

Control flow: generation starts by setting context-program flags, choosing save/load paths from `AUTO_SAVE`, `USER_SAVE`, `AUTO_LOAD`, and `USER_LOAD`, issuing `CP_NEWCTX` for loads, waiting for PGRAPH status/intr flags for saves, then swapping state. The swap consists of a small mandatory MMIO save at `0x400828`, a large MMIO/default section from `nv50_gr_construct_mmio()`, and two xfer areas from `nv50_gr_construct_xfer1()` and `nv50_gr_construct_xfer2()`. After a save pass it branches back to check whether a load is also pending; exit clears pending flags, disables xfer switching, stops the context program, and adds padding to the context-value size.

State and persistence: `nv50_grctx_init()` allocates a 512-word temporary ctxprog buffer, emits the program, uploads it through registers `0x400324/0x400328`, and returns the required context-object size in bytes. `nv50_grctx_fill()` emits the same logical layout into a `struct nvkm_gpuobj` so each channel starts with initialized MMIO, xfer strand, render-target, shader, texture, M2MF, 2D, ROP, and TPC/MPC state. State layout is highly chipset-dependent: it reads unit masks from register `0x1540`, gates ROP/TPC/MP sections on those bits, checks chipsets from NV50 through NVAx, and varies defaults on framebuffer RAM type for one ROP register.

Dependencies and integration points: this file depends on `ctxnv40.h` for the context-program DSL, `nv50.h` for device context, and `<subdev/fb.h>` for RAM type. It is part of the pre-Fermi Nouveau GR path, unlike the later GF100 FECS/GPCCS firmware model. Its generated size and fill routines are consumed by NV50 graphics engine/channel setup code when allocating and initializing channel graphics contexts.

Risks: the file is almost entirely hardware reverse-engineering data encoded as control flow. Off-by-one strand sizes, 64-word alignment mistakes, wrong unit-mask interpretation, or a bad magic default can cause GPU hangs, flicker, silent rendering corruption, broken context switching, or failures limited to one chipset. `ctxprog` is capped at 512 instructions; growth must be checked. Many comments explicitly mark unknown fields, guessed boundaries, and unexplained lockup fixes, so changes need real hardware coverage.

Test signals: useful signals are successful module load and GR init on NV50/NV84/NV9x/NVAx boards, correct `*size` allocation, no PGRAPH context-switch timeouts, stable 2D/3D/CUDA channel switching, render/texture/streamout/zeta/ROP correctness, and no regressions in suspend/resume or multi-channel workloads. Unit tests are not meaningful without hardware or an emulator that models PGRAPH ctxprog/xfer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxnv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxtu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxtu102.c

Purpose: `ctxtu102.c` defines the Turing TU102 graphics-context function table for Nouveau's GF100-style GR implementation. It does not build a full context generator itself; instead it selects existing GV100/GP100/GM107/GM200 helpers and supplies TU102-specific register programming, bundle initialization, SM ID writes, and an unknown context-buffer patch region.

Important APIs/types/functions: the public symbols are `tu102_grctx_generate_unknown(struct gf100_gr_chan *, u64 addr, u32 size)` and `const struct gf100_grctx_func tu102_grctx`. Private helpers are `tu102_grctx_generate_r419c0c(struct gf100_gr *)`, `tu102_grctx_generate_sm_id(struct gf100_gr *, int gpc, int tpc, int sm)`, and the `tu102_grctx_pack_sw_bundle64_init` pack around `struct gf100_gr_init` entries. Register writes use `nvkm_mask`, `nvkm_wr32`, `TPC_UNIT()`, and `gf100_grctx_patch_wr32()`.

Control flow: the generic GF100 context-generation path calls through `tu102_grctx`. The `.main` slot delegates to `gf100_grctx_generate_main`; `.unkn`, `.bundle`, `.pagepool`, `.attrib_cb`, `.attrib`, `.rop_mapping`, `.r406500`, and `.r400088` are inherited from prior GPU generations. TU102-specific callbacks mask registers `0x419c0c`, `0x40584c`, and `0x400080`, translate logical TPC indices through `gv100_gr_nonpes_aware_tpc()` before writing SM IDs to TPC offsets `0x608` and `0x088`, and patch channel context registers `0x408070`, `0x408074`, `0x419034`, and `0x408078` with an address/size pair.

State and persistence: this file encodes persistent per-channel context sizing constants: bundle size `0x3000`, pagepool size `0x20000`, unknown buffer size `0x80000`, attribute maximum/current counts `0x800/0x700`, alpha counts `0xc00/0x800`, and `gfxp_nr = 0xfa8`. The patch helper stores an address shifted by 8 into two context registers and stores a guessed size field shifted by 8. `skip_pd_num_tpc_per_gpc = true` changes how topology-derived state is emitted.

Dependencies and integration points: it includes `ctxgf100.h`, is declared there as `extern const struct gf100_grctx_func tu102_grctx`, and is selected by `tu102.c` through `.grctx = &tu102_grctx`. It integrates TU102 into the shared Fermi-and-newer GR context framework rather than the NV50 ctxprog system.

Risks: the `/*XXX: guess */` on the unknown size patch is a direct correctness risk. Register masks and shifted addresses are hardware contracts; a wrong value can break context allocation, SM identification, per-TPC scheduling, or channel restore. The non-PES-aware TPC mapping is essential on Volta/Turing-style topology, so bypassing it would write SM IDs to the wrong hardware TPC.

Test signals: TU102 and compatible Turing boards should initialize GR, create channels, switch contexts, and run graphics/compute workloads without FECS/GPCCS context errors. Specific checks include correct SM numbering exposed to shaders/debug paths, no faults from the unknown buffer address/size patch, and no regressions in topology variants with disabled GPC/TPC units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxtu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgf100.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgf100.fuc3.h

Purpose: this header embeds the GF100 GPCCS/GPC falcon firmware image used by the Fermi GF100 graphics engine. It provides `gf100_grgpc_data[]`, the firmware data segment, and `gf100_grgpc_code[]`, the instruction image that manages GPC-side context initialization, MMIO context transfers, strand setup, interrupt handling, and hub barrier synchronization.

Important APIs/types/functions: there are no C functions; the API is the two static `uint32_t` arrays. `gf100.c` includes this header and exposes the arrays through `struct gf100_gr_ucode gf100_gr_gpccs_ucode` with `.code.data/.code.size` and `.data.data/.data.size`. The firmware labels in comments identify routines such as `queue_put`, `queue_get`, `nv_rd32`, `nv_wr32`, `mmctx_size`, `mmctx_xfer`, `strand_ctx_init`, `init`, `main`, `ih`, `ctx_redswitch`, and `ctx_xfer`.

Control flow: the code image starts with queue helpers, MMIO read/write/wait helpers, context-size and context-transfer helpers, strand initialization, error handling, firmware `init`, wait/main loops, interrupt handling, a hub barrier acknowledgement at `hub_barrier_done`, redswitch delay handling, and context transfer load/save paths. GF100 lacks the later `unk_count`/`unk_mask` fields and `init_unk_loop` present in GF117/GK104/GK110 headers.

State and persistence: `gf100_grgpc_data[]` stores list head/tail offsets for GPC/TPC/unknown MMIO lists at `0x64`, `gpc_id`, `tpc_count`, `tpc_mask`, and an 18-word command queue starting at `0x001c`. The kernel loads this data into GPCCS data memory; firmware mutates queue and topology fields while it runs. The arrays persist in the kernel image as immutable source data.

Dependencies and integration points: this image pairs with `hubgf100.fuc3.h` FECS firmware. The GF100 GR init path loads both images to coordinate hub-level channel switching and GPC-level context state movement. The labels mirror shared falcon firmware concepts used by later GF117/GK/GM images.

Risks: this is opaque machine code. Any edit to a word, symbol name, array size, or data offset can prevent GPCCS boot, desynchronize the FECS/GPCCS command queue, or corrupt context images. Because GF100 has a slightly smaller data layout than later Fermi/Kepler GPC firmware, copying later offsets into this file would be unsafe.

Test signals: GF100 hardware should complete GR context-control initialization, load GPCCS firmware, execute context transfers, acknowledge hub barriers, and switch channels under 3D workloads without GPCCS watchdogs, firmware error labels, or PGRAPH context faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgf100.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgf117.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgf117.fuc3.h

Purpose: this header embeds GF117 GPCCS firmware for GPC-side graphics context control. It supplies `gf117_grgpc_data[]` and `gf117_grgpc_code[]` for the GF117 GR driver, covering command queues, MMIO context movement, strand initialization, interrupt handling, and GPC-to-hub synchronization.

Important APIs/types/functions: the C-visible contract is the two static arrays, included by `gf117.c` and wrapped in `static struct gf100_gr_ucode gf117_gr_gpccs_ucode`. Firmware label comments identify queue helpers, MMIO helpers, wait helpers, `mmctx_size`, `mmctx_xfer`, `strand_wait/pre/post/set`, `strand_ctx_init`, `init`, `init_unk_loop`, `main`, `ih`, `ih_no_fifo`, `hub_barrier_done`, `ctx_redswitch`, and `ctx_xfer`.

Control flow: compared with GF100, GF117 adds explicit unknown-unit count/mask state and an `init_unk_loop/init_unk_next/init_unk_done` sequence before the main wait loop. The runtime path receives work from FECS/hub firmware via the command queue, services context-transfer requests, waits for MMIO/strand readiness, posts barrier completion back to the hub, and returns to its wait/main loop.

State and persistence: `gf117_grgpc_data[]` uses a `0x6c` list base and includes `gpc_id`, `tpc_count`, `tpc_mask`, `unk_count`, `unk_mask`, and an 18-word command queue at `0x0024`. These offsets are part of the firmware ABI with the kernel-side GR loader and the hub firmware. The arrays are built into the driver and loaded into GPCCS instruction/data memory during GR initialization.

Dependencies and integration points: `gf117.c` includes this file after `hubgf117.fuc3.h`, then binds it as the GPCCS ucode image. It relies on the GF100-era context-control loader and coordinates with FECS hub firmware for channel switching and GPC-local state transfers.

Risks: the word stream is not self-validating at compile time. Data-layout drift from the kernel loader, queue offset mistakes, or mismatched FECS/GPCCS firmware can hang context switches. The additional unknown-unit loop is particularly sensitive because it likely tracks hardware units not present in GF100.

Test signals: GF117-class boards should boot GR firmware, initialize all GPC/TPC/unknown unit masks, run channel switches, and sustain graphics workloads without FECS/GPCCS timeouts, hub barrier stalls, or context image corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgf117.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk104.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk104.fuc3.h

Purpose: this header embeds GK104 Kepler GPCCS firmware. It provides `gk104_grgpc_data[]` and `gk104_grgpc_code[]`, the GPC-side falcon data/code image used for context-state transfers, strand setup, GPC/TPC/unknown-unit initialization, and synchronization with hub FECS firmware.

Important APIs/types/functions: there are no callable C routines. `gk104.c` includes the header and wraps the arrays in `static struct gf100_gr_ucode gk104_gr_gpccs_ucode`. Comment labels expose the firmware routine map: queue operations, `nv_rd32`/`nv_wr32` waits, `mmctx_size`, `mmctx_xfer`, `strand_ctx_init`, `init_unk_loop`, `wait`, `main`, interrupt handler paths, `hub_barrier_done`, `ctx_redswitch`, and `ctx_xfer`.

Control flow: the label structure is the GF117-style FUC3 GPCCS flow with an unknown-unit init loop and context-transfer paths. Runtime execution waits for hub commands, pulls queue entries, performs MMIO or strand context movement, acknowledges hub barriers, handles redswitch delay, and finalizes transfer state through `ctx_xfer_post`/`ctx_xfer_done`.

State and persistence: `gk104_grgpc_data[]` has list heads/tails at `0x6c`, GPC identity/topology fields, `unk_count`, `unk_mask`, and an 18-entry command queue. This is persistent firmware data memory initialized by the driver and then updated by GPCCS during operation. The array sizes are consumed via `sizeof()` by the GR ucode wrapper.

Dependencies and integration points: it pairs with `hubgk104.fuc3.h` and the GK104 GR implementation. The hub firmware orchestrates global channel/context switching while this GPCCS image performs GPC-local work, so the command queue and barrier semantics must match between the two images.

Risks: although it resembles GF117/GK110 firmware, it is a chip-specific binary. Substituting another chip's words or changing offsets can break Kepler context switching in ways that only appear under multi-channel or per-GPC workloads. Since comments are labels only, source review cannot prove instruction correctness.

Test signals: GK104 boards should load GPCCS, initialize all enabled GPC/TPC resources, run graphics context switches, and avoid firmware error paths, hub barrier waits, and GR faults during 3D/compute stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk104.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk110.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk110.fuc3.h

Purpose: this header embeds GK110 GPCCS FUC3 firmware for Kepler GPC context-control tasks. It defines `gk110_grgpc_data[]` and `gk110_grgpc_code[]`, which the GK110 GR driver loads into GPCCS to execute GPC-local portions of graphics context switching.

Important APIs/types/functions: the only C interface is the static data/code arrays. `gk110.c` includes the header and publishes it as `struct gf100_gr_ucode gk110_gr_gpccs_ucode`. Labeled firmware blocks include queue helpers, register read/write waits, MMIO context sizing and transfer, strand setup, `init_unk_loop`, wait/main loops, interrupt handling, hub barrier completion, redswitch delay, and context-transfer load/save completion.

Control flow: the firmware follows the later Fermi/Kepler GPCCS pattern: initialize topology and unknown units, idle in `wait/main`, accept hub commands through the queue, execute MMIO or strand transfer subroutines, signal `hub_barrier_done`, and return to the main loop after `ctx_xfer_done`. The label map matches GK104 closely, but the binary is chip-specific.

State and persistence: `gk110_grgpc_data[]` uses the `0x6c` data layout with GPC/TPC/unknown MMIO list heads and tails, `gpc_id`, `tpc_count`, `tpc_mask`, `unk_count`, `unk_mask`, and command queue storage at `0x0024`. The kernel image stores the initial data; live state exists in GPCCS data memory after upload.

Dependencies and integration points: this GPCCS image pairs with `hubgk110.fuc3.h` FECS firmware and the GK110 graphics engine functions. It depends on the shared GF100 firmware loader ABI through `struct gf100_gr_ucode`.

Risks: GPCCS and FECS firmware must agree on queue layout and barrier protocol. A size, prefix, or code-word mistake can cause initialization failure, hangs during `ctx_xfer`, or per-GPC state corruption. Similarity to GK104 should not be treated as interchangeability.

Test signals: expected signals are successful GK110 GR firmware load, no GPCCS error/timeout during channel creation or switching, correct GPC/TPC mask handling on partially fused chips, and stable rendering/compute workloads across repeated context switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk110.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk208.fuc5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk208.fuc5.h

Purpose: this header embeds GK208 GPCCS firmware using the FUC5 instruction encoding. It defines `gk208_grgpc_data[]` and `gk208_grgpc_code[]` for GPC-side context-control work on GK208 graphics hardware.

Important APIs/types/functions: `gk208.c` includes the header and exposes the arrays through `static struct gf100_gr_ucode gk208_gr_gpccs_ucode`. Firmware labels show the same conceptual routines as FUC3 images, but at different offsets and with FUC5 opcodes: queue helpers, MMIO read/write/wait helpers, `mmctx_size`, `mmctx_xfer`, strand operations, `init_unk_loop`, `main`, `ih`, `hub_barrier_done`, `ctx_redswitch`, and `ctx_xfer`.

Control flow: the firmware initializes GPC/TPC/unknown topology, waits for commands from FECS/hub firmware, performs MMIO/strand context transfers, handles interrupts and no-FIFO cases, reports hub barrier completion, and finalizes transfer state. Compared with FUC3 Kepler images, offsets are compressed/shifted and the word count is smaller, reflecting the FUC5 encoding rather than a C-level API change.

State and persistence: `gk208_grgpc_data[]` keeps the `0x6c` layout with GPC/TPC/unknown list heads/tails, IDs, masks, counts, and an 18-word command queue. This state is loaded into GPCCS data memory and mutated by firmware while the static array remains the kernel-side source.

Dependencies and integration points: it pairs with `hubgk208.fuc5.h` and is selected by the GK208 GR implementation. The shared GF100 GR ucode loader uses the array sizes, so the code/data definitions are the binding contract.

Risks: FUC5 instruction streams are opaque and architecture-specific. Accidentally treating the file as equivalent to FUC3 GK104/GK110 firmware, altering a branch target word, or changing data offsets can break GPCCS boot or context transfer. The smaller image still depends on the same hub/GPC queue protocol.

Test signals: GK208 hardware should load FECS and GPCCS FUC5 images, initialize topology, handle channel switches, and run graphics workloads without GPCCS hangs, barrier stalls, or context-transfer faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgk208.fuc5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgm107.fuc5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgm107.fuc5.h

Purpose: this header embeds GM107 Maxwell GPCCS FUC5 firmware. It supplies `gm107_grgpc_data[]` and `gm107_grgpc_code[]`, adding Maxwell-specific TPC strand initialization to the GPC-side context-control firmware path.

Important APIs/types/functions: the C interface is the two static arrays included by `gm107.c` and wrapped as `static struct gf100_gr_ucode gm107_gr_gpccs_ucode`. Labels identify queue and MMIO helpers, `mmctx_*` transfer routines, strand helpers, `tpc_strand_wait`, `tpc_strand_busy`, `init`, `init_unk_loop`, `tpc_strand_init_tpc_loop`, `tpc_strand_init_idx_loop`, wait/main loops, interrupt handling, `hub_barrier_done`, redswitch handling, and context-transfer completion.

Control flow: the first half mirrors GK208-style FUC5 GPCCS firmware, but GM107 adds explicit TPC strand wait/busy and nested TPC strand initialization loops before normal runtime handling. During operation it waits for hub commands, transfers context state, coordinates barriers, handles redswitch delay, and completes load/save transfer paths.

State and persistence: `gm107_grgpc_data[]` uses the `0x6c` layout with GPC/TPC/unknown MMIO list offsets, topology counts/masks, and command queue storage. Runtime mutations happen in GPCCS data memory. The longer code array and extra labels are persistent evidence that GM107 needs more per-TPC setup than GK208.

Dependencies and integration points: `gm107.c` includes this file after `hubgm107.fuc5.h`, using the shared `struct gf100_gr_ucode` loader. This requested subset includes the GPC file but not its matching hub file; integration still depends on the paired GM107 FECS image and GM107 GR initialization sequence.

Risks: Maxwell-specific TPC strand loops make topology handling sensitive. A mismatch between `tpc_count`/`tpc_mask`, firmware expectations, and kernel GR topology discovery can hang initialization or leave TPC context strands uninitialized. As with all firmware blobs, code-word edits have no compile-time semantic checks.

Test signals: GM107 hardware should complete GPCCS firmware init, including TPC strand loops, and then survive repeated channel switches and graphics/compute workloads without GPCCS busy waits, barrier stalls, or per-TPC rendering faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/gpcgm107.fuc5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgf100.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgf100.fuc3.h

Purpose: this header embeds GF100 FECS/hub FUC3 firmware for global graphics context control. It defines `gf100_grhub_data[]` and `gf100_grhub_code[]`, which orchestrate channel switches, hub MMIO context state, GPC initialization, channel context load/save, xfer execution, and interrupt handling.

Important APIs/types/functions: there are no C-callable routines. `gf100.c` includes the header and publishes it as `struct gf100_gr_ucode gf100_gr_fecs_ucode`. Firmware labels include queue helpers, MMIO helpers, `mmctx_size`, `mmctx_xfer`, strand helpers, `init`, `init_gpc`, `wait`, `main`, channel-switch branches (`chsw_prev_no_next`, `chsw_no_prev`, `chsw_done`), interrupt paths, context register handlers (`ctx_4160s`, `ctx_4160c`, `ctx_4170s`, `ctx_4170w`), memory load/wait, channel context load, MMIO execution loop, and xfer pre/exec/post/done.

Control flow: FECS initializes hub state, starts GPC firmware via `init_gpc`, waits for work, decides channel-switch cases, saves previous channel state, loads next channel state, executes MMIO list operations, coordinates xfer operations with GPC firmware, and handles firmware method/interrupt paths. Hub code owns global sequencing while GPCCS owns GPC-local execution.

State and persistence: `gf100_grhub_data[]` starts with hub MMIO list head/tail `0x300/0x304`, `gpc_count`, `rop_count`, an 18-word command queue, `ctx_current`, `chan_data` including channel MMIO count/address entries, `xfer_data`, and `hub_mmio_list_base`. FECS data memory stores current channel and transfer state across context switches after upload.

Dependencies and integration points: it pairs with `gpcgf100.fuc3.h` and is loaded by the GF100 GR context-control init path. It uses the same `struct gf100_gr_ucode` mechanism as later chips and must agree with GPCCS on command queues, barriers, and transfer layout.

Risks: FECS hub firmware is central to all channel switching. A wrong data offset or instruction word can prevent GR initialization, corrupt the current-channel pointer, deadlock waiting for GPCs, or mis-save channel context. GF100 includes `ctx_4160*` handlers that later GK104/GK110 hub images no longer label, so cross-family substitution is unsafe.

Test signals: GF100 boards should load FECS, start all GPC firmware, create and switch channels, save/load contexts, and run workloads without FECS interrupt storms, no-context-switch paths, xfer idle timeouts, or channel-state corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgf100.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgf117.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgf117.fuc3.h

Purpose: this header embeds GF117 FECS/hub FUC3 firmware. It provides `gf117_grhub_data[]` and `gf117_grhub_code[]` for global graphics context-control sequencing on GF117-family hardware.

Important APIs/types/functions: the static arrays are included by `gf117.c` and wrapped in `static struct gf100_gr_ucode gf117_gr_fecs_ucode`. Labels cover queue operations, register read/write waits, MMIO context transfer, strand initialization, firmware `init`, `init_gpc`, wait/main loops, channel-switch branches, interrupt handling, `ctx_4160s`, `ctx_4160c`, `ctx_4170s`, `ctx_4170w`, context memory load/wait, channel context load, MMIO execution, and xfer pre/exec/post/done.

Control flow: FECS initializes hub state and GPC firmware, then idles until channel-switch or firmware-method work arrives. On context switch, it evaluates previous/next channel cases, saves and loads channel data, executes MMIO lists, coordinates xfer with GPCCS images, and returns to the main loop or interrupt handler as needed.

State and persistence: `gf117_grhub_data[]` uses the standard hub layout: hub MMIO list offsets at `0x300/0x304`, `gpc_count`, `rop_count`, command queue, `ctx_current`, `chan_data`, `xfer_data`, and `hub_mmio_list_base`. The live state persists in FECS data memory and tracks current channel plus transfer bookkeeping.

Dependencies and integration points: this file pairs with `gpcgf117.fuc3.h`, is selected by GF117 GR setup, and uses the GF100 ucode loading ABI. It must match the GPCCS command protocol and the kernel's channel context layout.

Risks: the image is a hardware firmware blob, so compile-time type checking only verifies array syntax. Context-switch regressions can appear as FECS timeouts, GPC barrier stalls, or corrupted channel state. The retained `ctx_4160*` labels indicate GF117 still follows the GF100-style hub handler map, so later Kepler assumptions are not automatically valid.

Test signals: GF117 hardware should complete FECS/GPCCS startup, initialize GPCs, perform channel save/load transitions, handle interrupts, and run repeated 2D/3D workloads without context-control errors or xfer stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgf117.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk104.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk104.fuc3.h

Purpose: this header embeds GK104 FECS/hub FUC3 firmware for Kepler graphics context control. It defines `gk104_grhub_data[]` and `gk104_grhub_code[]`, the global firmware image that manages channel switching and coordinates GPC firmware.

Important APIs/types/functions: `gk104.c` includes this header and wraps the arrays in `static struct gf100_gr_ucode gk104_gr_fecs_ucode`. Labels include queue/MMIO helpers, `mmctx_size`, `mmctx_xfer`, strand helpers, `init`, `init_gpc`, wait/main loops, channel-switch branches, interrupt paths, `ctx_4170s`, `ctx_4170w`, `ctx_redswitch`, `ctx_86c`, `ctx_mem`, `ctx_load`, channel/MMIO execution, and xfer pre/exec/post/done.

Control flow: after initialization and GPC startup, the hub firmware waits for channel/context work, handles previous/next channel cases, executes memory and MMIO context operations, directs xfer work, waits for xfer idle, and finalizes channel context state. Relative to GF100/GF117 hub images, the labeled `ctx_4160s` and `ctx_4160c` handlers are absent and offsets shift accordingly.

State and persistence: `gk104_grhub_data[]` follows the standard hub data layout with `hub_mmio_list_head/tail`, `gpc_count`, `rop_count`, an 18-word command queue, `ctx_current`, `chan_data`, `xfer_data`, and `hub_mmio_list_base`. The firmware updates current-channel and transfer fields in FECS data memory.

Dependencies and integration points: it pairs with `gpcgk104.fuc3.h`, is loaded through the GF100 GR ucode path, and is selected by GK104 GR functions. It must remain in sync with GPCCS firmware and the GK104 channel/context layout.

Risks: Kepler FECS firmware is opaque and tightly coupled to hardware register semantics. Missing or altered words can hang `init_gpc`, break channel switching, or desynchronize MMIO/xfer operations. The absence of GF100-style `ctx_4160*` handlers is a family-specific distinction that matters when comparing blobs.

Test signals: GK104 cards should load hub and GPC firmware, initialize GPCs, create multiple channels, switch between them, and run GL/compute workloads without FECS errors, xfer idle waits, or context corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk104.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk110.fuc3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk110.fuc3.h

Purpose: this header embeds GK110 FECS/hub FUC3 firmware. It supplies `gk110_grhub_data[]` and `gk110_grhub_code[]`, the hub-side context-control image for GK110 graphics hardware.

Important APIs/types/functions: the static arrays are included by `gk110.c` and exposed as `struct gf100_gr_ucode gk110_gr_fecs_ucode`. Firmware labels cover queue helpers, MMIO read/write/wait helpers, MMIO context transfer, strand setup, `init`, `init_gpc`, wait/main, channel-switch branches, interrupt paths, `ctx_4170s`, `ctx_4170w`, redswitch delay, context memory load, channel load, MMIO execution, and xfer execution/post/done.

Control flow: FECS initializes, starts GPC firmware, idles in its wait/main loop, processes channel-switch decisions, saves/loads context memory, executes hub MMIO lists, coordinates xfer with GPCCS, and completes context-transfer state. Its label topology matches GK104 closely and lacks the GF100/GF117 `ctx_4160*` labels.

State and persistence: `gk110_grhub_data[]` uses hub list offsets `0x300/0x304`, GPC/ROP count fields, command queue storage, current context tracking, channel data, xfer data, and the hub MMIO list base. Live state persists in FECS data memory between channel switches.

Dependencies and integration points: it pairs with `gpcgk110.fuc3.h` and the GK110 GR implementation. The shared loader consumes it through `struct gf100_gr_ucode`; FECS/GPCCS queue and barrier contracts must match.

Risks: the file is binary firmware represented as C array initializers. Word-level corruption, wrong array binding, or mismatched GPCCS firmware can cause GR init failure, FECS deadlocks, incorrect current-channel tracking, or corrupted save/load contexts. Similarity to GK104 should not hide chip-specific binary differences.

Test signals: successful GK110 FECS/GPCCS firmware load, GPC startup, context switch stability, correct behavior on fused-unit variants, and absence of FECS watchdog, interrupt-handler error, or xfer timeout messages under graphics stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk110.fuc3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk208.fuc5.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk208.fuc5.h

Purpose: this header embeds GK208 FECS/hub firmware using the FUC5 instruction encoding. It defines `gk208_grhub_data[]` and `gk208_grhub_code[]` for hub-side graphics context control on GK208.

Important APIs/types/functions: `gk208.c` includes the header and wraps the arrays as `static struct gf100_gr_ucode gk208_gr_fecs_ucode`. Labels identify queue operations, MMIO helpers, context-size/transfer helpers, strand setup, `init`, `init_gpc`, wait/main loops, channel-switch branches, interrupt paths, `ctx_4170s`, `ctx_4170w`, redswitch handling, context memory load, channel load, MMIO loop, and xfer pre/exec/post/done.

Control flow: the firmware initializes hub state, starts GPC firmware, waits for channel-switch work, handles previous/next channel cases, saves/loads channel context, executes MMIO and xfer operations, and returns to the main loop. It is the FUC5 counterpart to the GK104/GK110 hub flow, with shorter code and shifted offsets.

State and persistence: `gk208_grhub_data[]` keeps hub MMIO list pointers at `0x300/0x304`, GPC/ROP counts, command queue, `ctx_current`, channel MMIO metadata, xfer metadata, and the hub MMIO list base. Runtime updates live in FECS data memory; the C arrays are the immutable load image.

Dependencies and integration points: it pairs with `gpcgk208.fuc5.h` and is selected by GK208 GR setup. The shared GF100 ucode wrapper provides code/data pointers and sizes to the firmware loader.

Risks: FUC5 opcodes are not interchangeable with FUC3 images. Any manual edit, bad size, or mismatched GPC image can break FECS startup, GPC init, xfer coordination, or channel context save/load. Family-specific label offsets should be treated as part of the firmware ABI.

Test signals: GK208 systems should complete FECS and GPCCS load, create channels, switch contexts repeatedly, and run rendering workloads without FECS/GPCCS timeouts, interrupt error paths, or context memory corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgk208.fuc5.h -->
