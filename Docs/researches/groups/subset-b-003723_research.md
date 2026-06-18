# Research: subset-b-003723

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100d.h

## Purpose
`r100d.h` is a shared register and command-packet definition header for the early Radeon KMS driver families. It supplies CP packet encoding macros, common MMIO/PLL register addresses, and bitfield helpers used by R100/R200/R300/R420-era code. In this subset it is pulled into `r200.c`, `r300.c`, and `r420.c` so those implementation files can emit packet0/packet2/packet3 commands and manipulate reset, bus, interrupt, memory-controller, CRTC, cursor, CP, RBBM, and clock-control registers with symbolic names rather than raw constants.

## Important APIs, Types, And Macros
The core exported surface is macro-only. `CP_PACKET0`, `CP_PACKET1`, `CP_PACKET2`, and `CP_PACKET3` describe the top bits of command processor packets. `PACKET0(reg, n)`, `PACKET2(v)`, and `PACKET3(op, n)` build command words using `REG_SET`, `PACKET*_COUNT`, and opcode/index shifts. The PACKET3 opcodes include draw, immediate draw, indexed draw, vertex-buffer pointer load, HyperZ clear, index-buffer, and blit operations used by the command-submission validators.

The register definitions include `R_0000F0_RBBM_SOFT_RESET` and its soft-reset bits, `R_000030_BUS_CNTL` bus-mastering and retry controls, `R_000040_GEN_INT_CNTL` and `R_000044_GEN_INT_STATUS` interrupt enable/status bits, display control registers such as `R_000050_CRTC_GEN_CNTL`, `R_000054_CRTC_EXT_CNTL`, CRTC2/cursor/display-base registers, memory-controller placement registers `R_000148_MC_FB_LOCATION`, `R_00014C_MC_AGP_LOCATION`, `R_000170_AGP_BASE`, CP registers `R_00070C_CP_RB_RPTR_ADDR`, `R_000740_CP_CSQ_CNTL`, scratch registers, `R_0007C0_CP_STAT`, `R_000E40_RBBM_STATUS`, and PLL/power-management registers including `R_00000D_SCLK_CNTL`.

Bit helper naming follows the local ASIC convention: `S_` macros set a field, `G_` macros extract a field, and `C_` constants clear a field. The header has no structs, enums, storage, or functions.

## Control Flow And State
There is no runtime control flow in the header. Its state impact is indirect: implementation code writes the defined registers through `WREG32`, `WREG32_PLL`, or ring packet emission. For example, `r300_fence_ring_emit()` uses `PACKET0()` and `RADEON_GEN_INT_STATUS` style definitions to flush caches, invalidate HDP, write a fence scratch register, and fire a software interrupt. `r300_asic_reset()` and `r420_resume()` inspect RBBM/CP status and use soft-reset fields to reset selected engines. Startup and suspend paths depend on the memory-controller, CP, and clock fields remaining accurate.

## Dependencies And Integration Points
The macros assume `REG_SET` and Radeon MMIO helpers are available from surrounding driver headers. They are included into ASIC implementation files that already have `radeon.h`, `radeon_reg.h`, and ASIC-specific headers in scope. The packet constants integrate with `radeon_ring_write()`, `radeon_cs_packet_parse()`, `r100_cs_parse_packet0()`, and packet3 validation paths. Register addresses integrate with BIOS posting, GART programming, fence/IRQ setup, display enable/disable, and debug/status logging.

## Risks
The highest risk is silent hardware misuse: a bad field mask, address, or packet count affects privileged GPU register writes and can cause hangs, data corruption, lost interrupts, or broken display state. `PACKET0()` count semantics must match command processor expectations; off-by-one count mistakes can desynchronize the ring. Reset and bus-control bit definitions are especially sensitive because they are used around GPU reset and bus-mastering transitions. Several definitions are shared across chip generations, so changing a bit for one ASIC can regress older paths.

## Test Signals
Useful signals are successful boot and resume on R100/R200/R300/R420 cards, clean CP ring startup, working fence interrupts, stable display modes, and lack of GPU lockups during reset and buffer moves. Unit tests are unlikely for this header; practical validation is compile coverage, command-submission tests that exercise packet builders, suspend/resume, debugfs status reads, and DRM/KMS workloads that emit fences and packet3 draws.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r100d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r200.c

## Purpose
`r200.c` contains R200-family command submission validation and a DMA copy helper for the classic Radeon driver. Its main job is to make user command streams safe before they reach the GPU: it rewrites relocatable addresses, imports tiling metadata from buffer objects, tracks render/texture/depth state, rejects unsupported or dangerous registers, and computes vertex sizes for draw validation. It also installs the R200 safe-register bitmap into the device configuration.

## Important APIs And Functions
`r200_copy_dma()` emits a CP DMA copy on the graphics ring. It waits for 2D idle, splits the copy into chunks no larger than `0x1FFFFF`, writes source/destination/size packets, waits for DMA GUI idle, emits a fence on `RADEON_RING_TYPE_GFX_INDEX`, and commits the ring.

`r200_packet0_check()` is the central packet0 register validator. It handles vline parsing, 2D pitch/offset relocation, color/depth buffer offsets, texture and cube-map texture offsets, render extents, color/depth pitch and formats, z/stencil formats, z-pass address relocation, texture enable state, vertex format, vertex/index bounds, texture dimensions, mip levels, pitch, coordinate type, compression format, and cube face dimensions. It returns `-EINVAL` for forbidden or inconsistent state.

`r200_get_vtx_size_0()` and `r200_get_vtx_size_1()` derive vertex dword counts from `R200_SE_VTX_FMT_0` and `R200_SE_VTX_FMT_1`. `r200_set_safe_registers()` points `rdev->config.r100.reg_safe_bm` at `r200_reg_safe_bm`.

## Control Flow
For packet0 validation, the parser passes each safe-register write to `r200_packet0_check()`. The function reads the IB value with `radeon_get_ib_value()`, switches on the register, and either rewrites the IB dword, updates `struct r100_cs_track`, or rejects the packet. Registers that reference GPU memory consume the next relocation with `radeon_cs_packet_next_reloc()`. If the relocation is missing, it warns once, dumps the packet, and fails. Draw validation is not performed directly here; this function prepares the state consumed later by common R100 tracking checks.

For `r200_copy_dma()`, control is ring-lock, wait, chunked DMA packet emission, idle wait, fence emit, then ring commit. On lock or fence failure it returns `ERR_PTR()`, undoing the ring lock when a fence cannot be emitted.

## State And Persistence Behavior
Persistent device state touched here lives under `rdev->config.r100` for safe-register policy and the graphics ring/fence subsystem for DMA copies. Per-command-submission state lives in `p->ib.ptr` and `p->track`: the IB is modified in place to add validated GPU offsets and tiling bits, while `r100_cs_track` records color buffer, z buffer, texture, vertex, and max-index metadata until final draw checks run. No state is persisted to disk.

## Dependencies And Integration Points
The file depends on `radeon.h`, `radeon_asic.h`, `radeon_reg.h`, `r100d.h`, `r200_reg_safe.h`, and `r100_track.h`. It integrates with the DRM CS parser, BO relocation list, TTM-backed buffer objects, tiling flags, fence emission, graphics ring locking, common R100 packet helpers, and safe-register bitmap infrastructure. The validator relies on texture and render format constants from R200/Radeon headers matching hardware and userspace command generation.

## Risks
This is a security boundary for untrusted command streams. Missing relocation checks or incorrect offset rewrites can allow GPU access outside validated BOs. Tiling flag handling is subtle because `RADEON_CS_KEEP_TILING_FLAGS` changes whether userspace-provided tiling bits are preserved. Vertex-size computation must match hardware packet layout or draw validation can undercount embedded vertices. Format tables and cube-face indexing are brittle because invalid cpp/compression metadata feeds bounds checking. `r200_copy_dma()` is hang-sensitive; the explicit idle waits document that DMA while 2D is busy can lock up hardware.

## Test Signals
Good signals include successful `drm/radeon` command submission from Mesa on R200 hardware, piglit or historical 3D tests covering textures, cube maps, depth/stencil, indexed and immediate draws, and buffer moves using CP DMA. Negative tests should submit missing relocations, invalid color/depth formats, forbidden registers, oversized texture settings, and keep-tiling versus driver-tiling cases. Runtime logs should not show "Forbidden register" or "No reloc" for valid workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300.c

## Purpose
`r300.c` implements R300/R350/RV350/RV370/RV380 and related early R4xx support in the Radeon KMS driver. It covers PCIe GART setup, fence and ring initialization, GPU and memory-controller setup, reset/resume/suspend/fini paths, PCIe lane control, debugfs reporting, command stream validation, and safe-register installation. The file is both an ASIC lifecycle driver and a command-submission security layer.

## Important APIs And Functions
PCIe indirect access is provided by `rv370_pcie_rreg()` and `rv370_pcie_wreg()`, both serialized by `pcie_idx_lock`. GART support includes `rv370_pcie_gart_tlb_flush()`, `rv370_pcie_gart_get_page_entry()`, `rv370_pcie_gart_set_page()`, `rv370_pcie_gart_init()`, `rv370_pcie_gart_enable()`, `rv370_pcie_gart_disable()`, and `rv370_pcie_gart_fini()`.

Ring and fence functions include `r300_fence_ring_emit()` and `r300_ring_start()`. Hardware setup functions include `r300_errata()`, `r300_mc_wait_for_idle()`, `r300_gpu_init()`, `r300_asic_reset()`, `r300_mc_init()`, `r300_mc_program()`, and `r300_clock_startup()`. Lifecycle entry points are `r300_init()`, `r300_resume()`, `r300_suspend()`, and `r300_fini()`.

Command submission is handled by `r300_cs_parse()`, `r300_packet0_check()`, and `r300_packet3_check()`. Debug support is exposed through `rv370_debugfs_pcie_gart_info_show()` and its init helper.

## Control Flow
Initialization starts with VGA disable, scratch/surface setup, sanity restore, BIOS discovery, combios init, reset/post checks, errata setup, clock discovery, optional AGP init, MC init, fence and BO setup, optional PCIe/PCI GART init, safe-register setup, PM init, then `r300_startup()`. Startup programs common registers and MC, starts clocks and GPU pipes, enables GART/bus mastering, initializes writeback, starts fence ring, installs IRQs, initializes CP with a 1 MiB ring, and creates the IB pool. Resume disables existing GART paths, clocks and resets the GPU, posts combios, reinitializes surfaces, then restarts acceleration. Suspend tears down PM, CP, WB, IRQ, and GART.

The CS parser allocates and clears an `r100_cs_track`, then loops over IB packets. Type0 packets are filtered by `r100_cs_parse_packet0()` and the R300 safe bitmap before `r300_packet0_check()` performs per-register handling. Type3 packets go to `r300_packet3_check()`. Draw packet handling records VAP control, validates embedded draw walk mode where needed, and calls `r100_cs_track_check()` before allowing draws.

## State And Persistence Behavior
Device state is stored in `struct radeon_device`: `gart`, `mc`, `ring`, `fence_drv`, `irq`, `config.r300`, `num_gb_pipes`, `num_z_pipes`, `pll_errata`, `accel_working`, and BIOS/PM/BO subsystems. GART page entries are written into a pinned VRAM table and hardware GART registers. Command validation mutates the IB in place with relocated offsets and tiling bits and tracks transient render state in `p->track`. Debugfs exposes live register snapshots only. No file-backed persistence is present.

## Dependencies And Integration Points
The file integrates with DRM core headers, PCI helpers, debugfs/seq_file, Radeon BO/GART/TTM, ring/fence/IB pools, IRQ handling, PM, combios/atombios helpers, common R100 tracking, safe-register tables, and generated register headers `r300d.h` and `rv350d.h`. It relies on low-level MMIO macros `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_PLL`, and `WREG32_PLL`.

## Risks
The parser is a kernel security boundary. Incorrect register whitelisting, relocation consumption, tiling-bit synthesis, or `r100_cs_track` metadata can permit out-of-bounds GPU access or hangs. HyperZ and CMASK ownership checks guard privileged compression/fast-clear resources and must remain strict. R300 reset contains explicit comments about possible hard lockups when resetting CP; changing delay/order is high risk. GART setup assumes 32-bit table address programming and correct page-entry endian handling. Startup error unwinding disables acceleration but must not leave IRQ, GART, or CP partially active.

## Test Signals
Signals include successful module load and modeset on R300/R350/RV350/RV370/RV380 hardware, PCIe GART debugfs showing sane base/start/end/error values, stable suspend/resume, working fences and IB submission, Mesa/piglit workloads for textures, MRT color buffers, z/stencil, HyperZ-denied paths, index buffers, and immediate draws. Negative CS tests should cover missing relocations, forbidden registers, unauthorized CMASK/HyperZ, invalid texture/color/depth formats, old-family-only restrictions, and unsupported packet3 opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300_reg.h

## Purpose
`r300_reg.h` is the primary R300 3D register dictionary. It defines memory-controller latency registers, vertex array processing, viewport and vertex program upload state, rasterization and interpolator routing, scissor/clip rectangles, texture units and formats, fragment program instruction encoding, fog/alpha/blend/color buffer state, z/stencil/HyperZ state, vertex program instruction encoding, packet3 draw constants, and a small set of R500-era aliases used by shared validation code. Its comments record reverse-engineered behavior and uncertainty.

## Important APIs, Types, And Macros
The file is macro-only. Important groups include `R300_VAP_*` for primitive control, vertex formats, input routes, vertex shader upload, and PVS control; `R300_GB_*` for geometry backend, tile config, multisample positions, FIFO sizing, fog/depth selection, and AA; `R300_TX_*` for texture enable, filter, size, format, pitch, offset, chroma key, and border color; `R300_PFS_*` and `R300_FPI*` for fragment program node, texture instruction, ALU source, destination, operand, and opcode fields; `R300_RS_*` for raster interpolator and route registers; `R300_RE_*` for point/line/polygon/fog/cull/scissor/clip state; `R300_RB3D_*` for blending, color masks, color offsets/pitches, and AA resolve; and `R300_ZB_*` for z/stencil, z-cache, HyperZ, zmask/hiz offsets, zpass, and depth XY offset.

The helper `R300_EASY_TX_FORMAT()` assembles texture format swizzles. The packet section defines primitive type/walk bits and packet constants such as `R300_PACKET3_3D_LOAD_VBPNTR`, `R300_PACKET3_INDX_BUFFER`, and `R300_CP_CMD_BITBLT_MULTI`.

## Control Flow And State
No code executes in this header. Its definitions drive command construction and validation elsewhere. In this subset, `r300_packet0_check()` depends on texture offset, size, filter, format, color pitch, depth pitch, z format, HyperZ, CMASK-related, AA resolve, and zpass definitions. `r300_ring_start()` and `r420_pipes_init()` use GB tile, pipe, multisample, cache, and destination pipe constants. State represented here is GPU pipeline state: vertex inputs, shader programs, texture images, render targets, depth buffers, interpolation, and caches.

## Dependencies And Integration Points
This header is included by R300/R420-era driver sources and complements `r300d.h`, `r420d.h`, `radeon_reg.h`, and safe-register bitmap headers. It integrates with Mesa/userspace command generation because many constants describe the exact command stream ABI accepted by the kernel. It also feeds `r100_cs_track` validation by letting kernel code interpret cpp, pitch, compression, coordinate type, tiling, and z/CB enable state.

## Risks
Many comments say "GUESS", "Dangerous", or describe reverse-engineered behavior. That means edits can produce hardware lockups even when the code compiles. Texture format, compression, pitch, and tiling constants are directly tied to bounds checks in `r300_packet0_check()`. HyperZ, zmask, hiz, CMASK, and fast-fill constants are security-sensitive because unauthorized access is rejected by ownership checks. Shader instruction encodings and PVS control registers can hang GPUs if invalid program bounds or unknown fields are emitted.

## Test Signals
Compile coverage is necessary but weak. Stronger signals are 3D rendering tests covering vertex arrays, immediate draws, programmable vertex and fragment shaders, all texture formats allowed by the validator, NPOT/pitched textures, depth/stencil, blending, scissor/cliprects, AA resolve, and HyperZ/CMASK authorization failures. Hardware hang absence and consistent piglit/Mesa behavior across R300, R420, and R500-family variants are the practical regression checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300d.h

## Purpose
`r300d.h` is a compact generated-style definition header for R300-family core registers and command packets. It overlaps with `r100d.h` for packet builders and status/reset fields but uses R300 naming for VAP/GA reset bits, MC address programming, AGP high-address programming, CP/RBBM status, and SCLK force bits. It is included by `r300.c` for reset, MC programming, CP status logging, packet emission, and clock startup.

## Important APIs, Types, And Macros
The header defines `CP_PACKET*`, PACKET3 opcodes, and `PACKET0/2/3()` builders. Register groups include `R_000148_MC_FB_LOCATION`, `R_00014C_MC_AGP_LOCATION`, `R_00015C_AGP_BASE_2`, `R_000170_AGP_BASE`, `R_0007C0_CP_STAT`, `R_000E40_RBBM_STATUS`, `R_0000F0_RBBM_SOFT_RESET`, and `R_00000D_SCLK_CNTL`.

Bit helpers include setters/getters/clear masks for MC frame-buffer and AGP ranges, high AGP base address bits, CP busy fields, RBBM engine busy fields including VAP and GA, soft-reset bits for CP/VAP/GA and other blocks, and clock force/dynamic-stop fields such as `S_00000D_FORCE_CP`, `S_00000D_FORCE_VAP`, and `S_00000D_FORCE_VIP`.

## Control Flow And State
The header has no executable flow. It shapes the flow in `r300.c`: `r300_mc_program()` writes MC FB and AGP placement fields; `r300_asic_reset()` checks `G_000E40_GUI_ACTIVE`, resets VAP/GA and CP through `R_0000F0_RBBM_SOFT_RESET`, then checks `G_000E40_GA_BUSY` and `G_000E40_VAP_BUSY`; `r300_clock_startup()` forces CP/VIP and sometimes VAP clocks on through `R_00000D_SCLK_CNTL`; debug logging reads CP/RBBM status addresses.

## Dependencies And Integration Points
It assumes the Radeon register-access layer and `REG_SET` macro are available. It integrates with `r300.c`, `radeon_asic_reset()`, MC save/restore helpers, PCI state helpers, ring packet emission, and clock-gating code. Because names are R300-specific, the file also documents how R300 maps R100-era concepts onto VAP/GA terminology.

## Risks
Reset and clock fields are hang-sensitive. A wrong bit name or mask can reset the wrong engine, fail to reset a busy engine, or gate clocks needed during CP startup. MC range fields are address-space critical; incorrect shifts can expose invalid VRAM/GART windows. The packet builders have the same command-stream desynchronization risk as `r100d.h`.

## Test Signals
Validation comes from successful R300 boot, reset, suspend/resume, CP startup, MC programming on AGP and non-AGP systems, and stable clock-gating behavior. Logs from failed resets should show meaningful RBBM/CP status values. Compile tests should catch missing macro users; only hardware tests can catch wrong bit semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r300d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r420.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r420.c

## Purpose
`r420.c` implements R420/R4xx ASIC lifecycle support for the Radeon KMS driver. It initializes power profiles, safe-register policy, pipe/tile configuration, memory-controller indirect access, clock resume behavior, an R420/RV410 CP DMA erratum workaround, startup/resume/suspend/fini paths, and a debugfs pipe-info node. It builds on R300 infrastructure while handling R420-specific pipe counts, clock bits, register-safe bitmap, and reset/post behavior.

## Important APIs And Functions
`r420_pm_init_profile()` fills PM profile mappings for default, low/mid/high single-head, and low/mid/high multi-head cases. `r420_pipes_init()` programs GA enhance, determines GB pipe count from `R400_GB_PIPE_SELECT` with SE-chip overrides, configures `R500_SU_REG_DEST`, tile config, destination pipe auto-config, 2D destination cache mode, z-pipe count, and logs pipe topology.

`r420_mc_rreg()` and `r420_mc_wreg()` provide indirect MC register access using `mc_idx_lock` and `R_0001F8_MC_IND_INDEX/DATA`. `r420_clock_resume()` restores dynamic clock gating and forces CP/VIP plus R420-specific PX/TX clocks. `r420_cp_errata_init()` and `r420_cp_errata_fini()` reserve a scratch register and emit RESYNC/cache-finish packets for an RV410/R420 CP DMA-to-host-memory erratum.

Lifecycle functions are `r420_init()`, `r420_resume()`, `r420_suspend()`, and `r420_fini()`. `r420_debugfs_pipes_info_init()` registers `r420_pipes_info`.

## Control Flow
Initialization sets scratch/surface/sanity state, loads and initializes ATOM or COMBIOS, resets and verifies posting, reads clock info, initializes AGP/MC/debugfs/fence/BO/GART, installs the R420 safe bitmap, initializes PM, then runs `r420_startup()`. Startup sets common registers, programs MC via R300 code, resumes clocks, enables PCIe or PCI GART, programs pipes, initializes writeback, starts fences and IRQs, initializes CP, applies the CP erratum RESYNC, and creates the IB pool.

Resume disables active GART paths, resumes clocks, resets/posts using ATOM or COMBIOS, restores surfaces, then restarts acceleration. Suspend pauses PM, finalizes the CP erratum, disables CP/WB/IRQ/GART. Fini tears down PM, CP, WB, IB, GEM, GART/AGP, IRQ, fence, BO, BIOS, and frees `rdev->bios`.

## State And Persistence Behavior
State changes live in `struct radeon_device`: PM profile arrays, `config.r300.reg_safe_bm`, pipe counts, z-pipe counts, `config.r300.resync_scratch`, GART/MC/ring/fence/IRQ/BO/BIOS state, and `accel_working`. MC indirect accesses are serialized. Debugfs reads current hardware registers without persistence. Startup failure leaves the driver loaded but disables acceleration after cleaning key acceleration resources.

## Dependencies And Integration Points
The file depends on Linux PCI/debugfs/seq_file/slab, DRM device/file headers, `atom.h`, `r100d.h`, `r420_reg_safe.h`, `r420d.h`, `radeon.h`, `radeon_asic.h`, and `radeon_reg.h`. It integrates heavily with R100 and R300 helpers: common register setup, GUI idle waits, MC programming/init, CP init/fini, PCIe GART, PCI GART, AGP, PM, BIOS, fence, IRQ, BO, writeback, and debugfs.

## Risks
Pipe programming is hardware-sensitive; wrong pipe count or tile config can corrupt rendering or hang. `r420_cp_errata_init()` uses `WARN_ON(r)` but still writes ring commands after a failed lock, which is a historical pattern but a risk area if lock failure becomes possible. Scratch allocation for the erratum must be paired with free in suspend/fini paths. Resume/reset order is important because comments note ATOM can loop if reset/post order is wrong. Error unwind in `r420_init()` must keep resources balanced across PCIe, PCI, and AGP variants.

## Test Signals
Strong signals include boot, modeset, acceleration, and suspend/resume on R420/RV410/RV530-style hardware; debugfs `r420_pipes_info` showing expected pipe and tile registers; CP DMA workloads that avoid host-memory lockups; working PM profile selection; and successful Mesa rendering with multiple pipe configurations. Logs should show initialized quad/z pipe counts and no GUI-idle warnings under normal conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r420.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r420d.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r420d.h

## Purpose
`r420d.h` is a compact R420-specific generated-style register definition header. It supplies indirect memory-controller register access fields, CP and RBBM status fields, and R420 clock-control bitfields. It is included by `r420.c` to read/write indirect MC registers, log reset status, and force required clock domains during resume/startup.

## Important APIs, Types, And Macros
The exported surface is macro-only. `R_0001F8_MC_IND_INDEX` and `R_0001FC_MC_IND_DATA` define the indirect MC index/data pair used by `r420_mc_rreg()` and `r420_mc_wreg()`, with fields `S_0001F8_MC_IND_ADDR()` and `S_0001F8_MC_IND_WR_EN()`.

`R_0007C0_CP_STAT` defines CP busy/status bits including MRU/MWU, CSF/CSQ primary and indirect busy states, GUIDMA/VIDDMA, command stream, and CP busy. `R_000E40_RBBM_STATUS` defines command FIFO availability and engine-busy bits including RB2D, RB3D, VAP, RE, TAM/TDM, PB, TIM, GA, CBA2D, and GUI active. `R_00000D_SCLK_CNTL` defines dynamic stop latency and force bits for CP, HDP, display, VAP, VIP, RE, SR, PX, TX, US, TV, SU, and overlay clock domains.

## Control Flow And State
There is no executable control flow. In `r420.c`, MC accessors lock `rdev->mc_idx_lock`, write the index register with address and optional write-enable, then read or write the data register. Resume/startup reads `SCLK_CNTL`, ORs clock force bits, and writes it back. Reset warning paths read RBBM and CP status registers to show why reset failed.

## Dependencies And Integration Points
The header integrates with `r420.c`, `RREG32/WREG32`, `RREG32_PLL/WREG32_PLL`, spinlocks, and R420/R300 lifecycle code. It complements broader 3D register definitions from `r300_reg.h` and shared packet definitions from `r100d.h`. The indirect MC definitions are used only when the ASIC requires indexed MC access rather than direct MMIO.

## Risks
Indirect MC access is sensitive to locking and address width. Wrong address masks or write-enable bits can target the wrong MC register or corrupt controller state. Clock force fields are power-management and hang-sensitive; omitting a required force bit can leave CP or texture/pixel blocks gated during startup, while forcing the wrong block can affect power behavior. Status field mistakes reduce diagnosability and can mislead reset handling.

## Test Signals
Successful R420 boot/resume and working acceleration are the primary signals. Additional checks include valid MC indirect reads/writes, meaningful reset failure logs, no clock-gating related hangs, and stable debugfs pipe/status output. Build coverage verifies users of field helpers, but hardware validation is required for bit correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/r420d.h -->
