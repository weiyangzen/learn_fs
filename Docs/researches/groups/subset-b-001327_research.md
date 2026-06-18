# subset-b-001327 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx10.h

## Purpose
`clearstate_gfx10.h` is a generated/static AMDGPU clear-state data table for GFX10 devices. It defines the default context-register payload used to initialize the graphics clear-state block so the CP/RLC can restore known baseline graphics context state. The file contains no executable functions; its interface is the `gfx10_cs_data` static section table consumed by `gfx_v10_0.c`.

## Important APIs, Types, and Data
The file relies on `struct cs_extent_def` and `struct cs_section_def` from `clearstate_defs.h`. It defines eight `static const unsigned int gfx10_SECT_CONTEXT_def_*[]` arrays and combines them in `gfx10_SECT_CONTEXT_defs[]`, terminated by `{ 0, 0, 0 }`. The exported-to-include-unit table is `gfx10_cs_data[]`, with one `SECT_CONTEXT` section and a `{ 0, SECT_NONE }` terminator.

The context extents are `{reg_index, reg_count}` clusters starting at `0x0000a000` (215 registers), `0x0000a0d8` (272), `0x0000a1f5` (4), `0x0000a1ff` (158), `0x0000a2a0` (2), `0x0000a2a3` (1), `0x0000a2a5` (66), and `0x0000a2f5` (203). The register comments show coverage across depth buffer, scissor/viewport, shader/primitive, VGT, PA, and color-buffer registers, including CB DCC/FMASK/CMASK/base/attribute registers for eight color targets. Most values are zero, but required hardware defaults include scissor bounds such as `0x40004000`, full target/shader masks, viewport `ZMAX` values of `0x3f800000`, cache-control defaults such as `DB_RMI_L2_CACHE_CONTROL` and `CB_RMI_GL2_CACHE_CONTROL`, and geometry defaults such as `VGT_GS_PER_ES`.

## Control Flow and Integration
There is no local control flow. At compile time `gfx_v10_0.c` includes this header, assigns `adev->gfx.rlc.cs_data = gfx10_cs_data`, and uses it in clear-state sizing/building paths. `gfx_v10_0_get_csb_size()` walks each `cs_section_def` and `cs_extent_def`, adding `2 + reg_count` dwords per context extent. `gfx_v10_0_cp_gfx_start()` emits `PACKET3_SET_CONTEXT_REG` packets over the graphics ring by subtracting `PACKET3_SET_CONTEXT_REG_START` from each extent `reg_index`, then writes every payload dword. GFX10 also appends `PA_SC_TILE_STEERING_OVERRIDE` from runtime config outside this static table.

## State and Persistence Behavior
The arrays are immutable kernel text/rodata. They do not persist state independently and are not updated at runtime. Their values are copied into the RLC clear-state buffer or written to the CP ring during graphics startup/resume. The persistent effect is on GPU hardware context initialization: after clear-state setup, command processor/RLC operations can restore these baseline context registers.

## Dependencies
The table depends on the `clearstate_defs.h` ABI, GFX10 context-register numbering, and the packet-building code in `gfx_v10_0.c`. It assumes the register offsets and array lengths match the hardware generation. The comments are register-name documentation only; the actual contract is positional data plus `reg_index` and `reg_count`.

## Risks
The primary risk is table drift from hardware definitions. A bad `reg_count`, wrong start index, missing hole, or misplaced nonzero default will shift every subsequent register write and can cause rendering failures, GPU hangs, or reset/resume bugs. Because the arrays are static and consumed by pointer walking until a null extent, terminator integrity is also critical. The file lacks an include guard, so it is intended for single inclusion from the matching GFX10 implementation.

## Test Signals
Useful signals are successful boot/resume on GFX10 ASICs, successful RLC clear-state block allocation, clean `gfx_v10_0_cp_gfx_start()` ring submission, absence of GPU hangs after clear-state preamble execution, and graphics validation covering depth/stencil, viewport/scissor, DCC, FMASK/CMASK, and multi-render-target paths. Static review should verify extent counts against array lengths and register ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h

## Purpose
`clearstate_gfx11.h` provides the static clear-state context register defaults for GFX11 AMDGPU devices. It is included by `gfx_v11_0.c` and supplies the generation-specific `gfx11_cs_data` table used to size and populate the RLC clear-state block and to build clear-state command streams.

## Important APIs, Types, and Data
The file defines `gfx11_SECT_CONTEXT_def_1` through `gfx11_SECT_CONTEXT_def_7`, wraps them in `gfx11_SECT_CONTEXT_defs[]`, and exposes `gfx11_cs_data[]` as a `SECT_CONTEXT` section. It uses the `cs_extent_def`/`cs_section_def` structures from `clearstate_defs.h` and terminates extent/section arrays with zero sentinels.

The extents cover `0x0000a000` for 215 registers, `0x0000a0d8` for 272, `0x0000a1f5` for 4, `0x0000a1ff` for 158, `0x0000a2a0` for 2, `0x0000a2a3` for 1, and `0x0000a2a6` for 282. Compared with GFX10, the last extent is consolidated and starts at `0xa2a6`; comments also show GFX11-specific naming such as `DB_RESERVED_REG_*`, `DB_SPI_VRS_CENTER_LOCATION`, conservative rasterization control, and updated color-buffer base/DCC extension coverage. Nonzero defaults preserve expected scissor rectangles, masks, viewport depth max values, clip controls, and rasterization defaults.

## Control Flow and Integration
The file has no functions. `gfx_v11_0_get_csb_size()` iterates `gfx11_cs_data`, accepting only `SECT_CONTEXT` and counting each extent as packet header plus data. `gfx_v11_0_get_csb_buffer()` uses generic helpers (`amdgpu_gfx_csb_preamble_start()`, `amdgpu_gfx_csb_data_parser()`, and `amdgpu_gfx_csb_preamble_end()`) after `adev->gfx.rlc.cs_data` is set to `gfx11_cs_data`. The GFX11 startup path also programs `PA_SC_TILE_STEERING_OVERRIDE` separately from runtime configuration.

## State and Persistence Behavior
The table is immutable static data. It does not retain runtime state and has no persistence beyond the driver image. Its values become persistent GPU baseline context state only after they are copied into the clear-state buffer or emitted through CP packets during initialization/resume. Because the table is static, suspend/resume consistency depends on the consumer reusing it rather than modifying it.

## Dependencies
Dependencies include the clear-state struct definitions, GFX11 register layout, CP `PACKET3_SET_CONTEXT_REG` semantics, RLC clear-state allocation in common AMDGPU graphics code, and the `gfx_v11_0.c` assignment of `adev->gfx.rlc.cs_data`. The include guard prevents accidental duplicate definitions within a translation unit.

## Risks
The most important risk is positional mismatch: comments do not drive behavior, so the table must exactly match hardware register order and the declared extent lengths. GFX11-specific reserved/register additions make copy-forward from older generations risky. Any malformed terminator can overrun consumer walks. Incorrect nonzero defaults in scissor, mask, VRS, conservative rasterization, or color-buffer metadata registers can surface as subtle rendering corruption rather than immediate compile failures.

## Test Signals
Validation should include GFX11 boot and resume, successful `amdgpu_gfx_rlc_init_csb()` setup, no clear-state parser rejection, and GPU ring progress after clear-state preambles. Rendering tests should stress VRS/conservative rasterization, depth/stencil, clip/scissor, viewport arrays, color target metadata, DCC, and multi-target output. Static checks should compare the seven extent counts with actual array element counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx11.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx12.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx12.h

## Purpose
`clearstate_gfx12.h` is the compact GFX12 clear-state table used by GFX12 AMDGPU graphics code. It defines the context-register clusters that are written into the newer RLC clear-state buffer format for GFX12 and GFX12.1 consumers.

## Important APIs, Types, and Data
The file defines six `static const unsigned int gfx12_SECT_CONTEXT_def_*[]` arrays, `gfx12_SECT_CONTEXT_defs[]`, and `gfx12_cs_data[]`. It uses `struct cs_extent_def` and `struct cs_section_def`, and is protected by `__CLEARSTATE_GFX12_H_`.

Unlike older clearstate headers, the table is much smaller. Extents are `0x0000a03e` for 34 registers, `0x0000a0cc` for 2, `0x0000a0d8` for 1, `0x0000a0db` for 6, `0x0000a2e5` for 11, and `0x0000a3c0` for 8. Comments identify the covered registers as memory temporal/speculative-read controls, 16 viewport TL/BR pairs, programmable near clip/rate control, perfmon context control, cliprect extension registers, HIZ/HIS metadata registers, binner controls, and `CB_MEM0_INFO` through `CB_MEM7_INFO`. All listed payload values are zero.

## Control Flow and Integration
There is no local execution path. `gfx_v12_0.c` and `gfx_v12_1.c` include this file and assign `adev->gfx.rlc.cs_data = gfx12_cs_data`. The GFX12 clear-state buffer builder differs from prior generations: `gfx_v12_0_get_csb_size()` starts with one dword for a cluster count and then adds `2 + reg_count` per extent, while `gfx_v12_0_get_csb_buffer()` writes `{reg_count, reg_index, payload...}` clusters and stores the final cluster count in `buffer[0]`. It does not build the older packet preamble format in this path.

## State and Persistence Behavior
The table is immutable rodata and has no runtime state. Its values are copied to the allocated RLC clear-state object during graphics initialization and reused across normal driver lifecycle events. Because every payload value is zero, the table primarily acts as a whitelist of GFX12 context registers that must be reset by clear-state, rather than carrying many generation-tuned nonzero defaults.

## Dependencies
Dependencies are the GFX12 register address map, `clearstate_defs.h`, and the GFX12/GFX12.1 clear-state buffer builders. The table assumes the consumer interprets `reg_index` as the hardware context-register index expected by the GFX12 RLC firmware format, not as an offset adjusted by `PACKET3_SET_CONTEXT_REG_START`.

## Risks
The small table makes missing coverage the key risk. If a register that should be reset is absent, stale context state may leak across queues or submissions. If the cluster count or extent lengths become inconsistent with the arrays, RLC firmware may parse the buffer incorrectly. Because all payloads are zero, accidental zeroing of a register that requires a nonzero architectural default is also a generation-porting risk.

## Test Signals
Signals include successful initialization in `gfx_v12_0_rlc_init()`/`gfx_v12_1` paths, valid clear-state buffer size/count, no RLC firmware errors, clean suspend/resume, and rendering tests that exercise viewport setup, clip rectangles, HIZ/HIS, binner behavior, and color-buffer memory info. Static validation should compare the six declared counts to the actual arrays and confirm the cluster count written by the consumer is six.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx12.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx9.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx9.h

## Purpose
`clearstate_gfx9.h` defines the GFX9 graphics context clear-state defaults for AMDGPU. It supplies static register payload arrays used by GFX9 graphics initialization so CP/RLC clear-state operations can restore a known baseline after context switches, resets, and startup.

## Important APIs, Types, and Data
The file defines eight `gfx9_SECT_CONTEXT_def_*` arrays and the `gfx9_SECT_CONTEXT_defs[]` extent table, exposed through `gfx9_cs_data[]` with a `SECT_CONTEXT` entry. Extents begin at `0x0000a000` (212 registers), `0x0000a0d6` (282), `0x0000a1f5` (4), `0x0000a200` (157), `0x0000a2a0` (2), `0x0000a2a3` (1), `0x0000a2a5` (66), and `0x0000a2f5` (155).

The arrays cover depth/stencil DB registers, scissor and viewport registers, SPI shader inputs, VGT geometry defaults, primitive assembly/rasterization settings, and CB color target metadata through `CB_COLOR7_*`. Nonzero defaults include full masks, standard screen/window/scissor bounds, viewport max depth floats, clip and edge rules, stencil ref masks, GS/ES/VS ratios, and binner/vertex reuse/deallocation controls.

## Control Flow and Integration
There is no executable code in the header. Its data is consumed by matching GFX9 code in the same style as other generations: the graphics code iterates `cs_section_def` and `cs_extent_def` entries, accepts `SECT_CONTEXT`, and emits context-register writes or builds an RLC clear-state buffer. Each extent maps to one context register range; the consumer relies on `reg_count` to know how many dwords to copy.

## State and Persistence Behavior
The table is static const data and does not store runtime state. Its payload is applied to GPU context registers during graphics clear-state setup. Once applied, it affects hardware baseline state, but the source arrays remain unchanged and are reused on later initialization/resume paths.

## Dependencies
Dependencies are `clearstate_defs.h`, GFX9 register numbering, AMDGPU graphics/RLC initialization, and CP packet conventions for setting context registers. The table is coupled to the exact hardware register layout, including holes represented by zero entries.

## Risks
The risk profile is high because this is dense positional hardware data. Incorrect holes, counts, or nonzero defaults can corrupt all later writes in an extent. Errors may appear as rendering corruption, failed ring tests, hangs during clear-state preamble, or resume instability. The file has no include guard and should remain included only once by its intended C translation unit.

## Test Signals
Boot/resume on GFX9 hardware, successful clear-state block creation, clean CP ring startup, and no RLC parser or GPU reset errors are key signals. Rendering coverage should include depth/stencil, viewport/scissor arrays, shader input defaults, geometry/VGT behavior, binner settings, and color-buffer DCC/FMASK/CMASK paths. Static tests should validate extent counts and sentinel termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_gfx9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_si.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_si.h

## Purpose
`clearstate_si.h` contains Southern Islands/GFX6 clear-state context defaults. It is included by `gfx_v6_0.c` and provides `si_cs_data`, the static data source used when programming clear-state packets for SI-generation GPUs.

## Important APIs, Types, and Data
The file defines seven `static const u32 si_SECT_CONTEXT_def_*[]` arrays, `si_SECT_CONTEXT_defs[]`, and `si_cs_data[]`. The extent table covers `0x0000a000` for 212 registers, `0x0000a0d8` for 272, `0x0000a1f5` for 6, `0x0000a200` for 157, `0x0000a2a1` for 1, `0x0000a2a3` for 1, and `0x0000a2a5` for 233. It uses `NULL` sentinels rather than plain zero for pointer fields.

The register comments cover early DB/depth state, PA scissor/window/viewport arrays, CB masks, SPI state, VGT defaults, clip/raster state, and SI-era color target registers using pitch/slice naming rather than newer base-extension naming. Defaults include nonzero scissor bounds, full CB masks, viewport `ZMAX` values, maximum vertex index, clip control, GS/ES/VS ratios, and vertex reuse/deallocation controls.

## Control Flow and Integration
The header has no functions. `gfx_v6_0.c` assigns `adev->gfx.rlc.cs_data = si_cs_data` for SI ASICs and later walks the table in `gfx_v6_0_cp_gfx_start()`. That path emits `PACKET3_PREAMBLE_BEGIN_CLEAR_STATE`, then for each `SECT_CONTEXT` extent emits `PACKET3_SET_CONTEXT_REG`, the adjusted register offset, and all data dwords before ending the clear-state preamble.

## State and Persistence Behavior
The arrays are immutable and carry no runtime state. Their values are transferred into hardware context registers during CP graphics startup. Persistence is hardware-side only: after the preamble, CP/RLC clear-state behavior uses these defaults until the device is reset or reinitialized.

## Dependencies
Dependencies include `clearstate_defs.h`, SI/GFX6 context-register layout, `gfx_v6_0.c` graphics startup, and packet definitions such as `PACKET3_SET_CONTEXT_REG_START`. The use of `u32` assumes an includer has already made Linux integer typedefs available.

## Risks
SI hardware is older and register layouts differ from VI/GFX9+, so porting entries between generations is risky. A shifted hole or incorrect count can misprogram large register ranges. Since this file uses `NULL` sentinels while newer headers often use `0`, consumers must treat both as null pointers; current pointer checks do. Missing nonzero defaults can break legacy rendering paths that rely on established clear-state behavior.

## Test Signals
Signals include successful `gfx_v6_0_cp_gfx_start()`, ring tests passing after clear-state preamble, no GPU lockups on SI devices, and rendering correctness across depth/stencil, scissor/viewport, geometry shader defaults, and color-buffer pitch/slice/CMASK/FMASK paths. Static checks should verify all seven extents against actual array lengths and confirm sentinel termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_si.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_vi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_vi.h

## Purpose
`clearstate_vi.h` provides Volcanic Islands-era clear-state context register defaults. It supplies `vi_cs_data`, the static table used by VI graphics startup code to program baseline context state for CP/RLC clear-state handling.

## Important APIs, Types, and Data
The file defines seven `static const unsigned int vi_SECT_CONTEXT_def_*[]` arrays, a `vi_SECT_CONTEXT_defs[]` extent list, and `vi_cs_data[]`. Extents start at `0x0000a000` for 212 registers, `0x0000a0d6` for 274, `0x0000a1f5` for 6, `0x0000a200` for 157, `0x0000a2a0` for 2, `0x0000a2a3` for 1, and `0x0000a2a5` for 233. The table is terminated with `{ 0, 0, 0 }` and `{ 0, SECT_NONE }`.

The register payload spans DB, PA, SPI, VGT, raster, binner, and CB color target state. Compared with SI it includes VI-era DCC controls and DCC base entries while retaining pitch/slice style color target registers. Nonzero defaults include common scissor/window bounds, full color masks, viewport max-depth values, clip/raster defaults, IA multi-VGT parameters, and vertex reuse/deallocation settings.

## Control Flow and Integration
The header itself has no control flow. It is included by VI graphics code that stores `vi_cs_data` in `adev->gfx.rlc.cs_data` and walks the section/extent list when building clear-state command streams. The consumer emits context-register write packets for `SECT_CONTEXT` extents and relies on each extent's start index/count to align payload entries with hardware registers.

## State and Persistence Behavior
The data is static const and not mutated. It is copied to GPU-visible command streams or clear-state memory during graphics initialization/resume. There is no filesystem or driver-level persistence; the effect lasts as programmed hardware context baseline state.

## Dependencies
Dependencies are the VI register map, `clearstate_defs.h`, AMDGPU VI graphics startup, and CP/RLC context register programming semantics. Because this file is pure data, correctness depends on the includer providing the expected type definitions and on the generation-specific C file choosing this table only for compatible ASICs.

## Risks
The dense register table can fail silently if a count or hole is wrong; subsequent values would target incorrect registers. DCC-related entries are especially generation-sensitive. Bad clear-state defaults can manifest as corruption in render target metadata paths, hangs during CP startup, or resume failures. Like several older clearstate headers, it has no include guard and is designed for controlled single inclusion.

## Test Signals
Use VI hardware boot/resume, CP ring startup, RLC clear-state setup, and rendering tests that exercise DCC, color compression metadata, depth/stencil, scissor/viewport arrays, and multi-engine graphics contexts. Static validation should check extent sizes, terminators, and register-family coverage against VI hardware headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_vi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cyan_skillfish_reg_init.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cyan_skillfish_reg_init.c

## Purpose
`cyan_skillfish_reg_init.c` initializes AMDGPU register base offset tables for Cyan Skillfish, a Navi-family APU configuration using static IP offset tables. Its single function, `cyan_skillfish_reg_base_init()`, maps each hardware IP block enum to the corresponding generated base-address table used by register access macros.

## Important APIs, Types, and Functions
The file exports `int cyan_skillfish_reg_base_init(struct amdgpu_device *adev)`, declared in `nv.h`. It includes `amdgpu.h`, `nv.h`, SOC15 common/IP headers, and `cyan_skillfish_ip_offset.h`, which defines symbols such as `GC_BASE`, `HDP_BASE`, `MMHUB_BASE`, and other per-IP base arrays.

The function sets `adev->gfx.xcc_mask = 1`, then loops `i` from `0` to `MAX_INSTANCE - 1` and fills `adev->reg_offset[HWIP][i]` for GC, HDP, MMHUB, ATHUB, NBIO, MP0, MP1, VCN, DF, DCE, OSSSYS, SDMA0, SDMA1, SMUIO, THM, and CLK. SDMA0 and SDMA1 intentionally point at `GC_BASE.instance[i]`, and VCN maps to `UVD0_BASE`. It returns `0` unconditionally.

## Control Flow and Integration
Control flow is linear: initialize the graphics XCC mask, populate all relevant hardware-IP offset pointers for each instance, and return success. The function is called from the discovery/Navi initialization path for Cyan Skillfish; `amdgpu_discovery.c` invokes it for this ASIC path when static/discovery register base setup is needed. After this function runs, SOC15 register macros can resolve logical IP/register accesses through `adev->reg_offset`.

## State and Persistence Behavior
The function mutates only in-memory driver state on `struct amdgpu_device`: `adev->gfx.xcc_mask` and `adev->reg_offset`. There is no persistent storage and no allocation. The offset pointers remain valid as long as the generated static base tables remain linked into the driver image and the `amdgpu_device` instance is alive. The function is idempotent for the same device because it overwrites the same fields with the same static addresses.

## Dependencies
The critical dependency is `cyan_skillfish_ip_offset.h`, whose generated structures must match `MAX_INSTANCE` and the hardware IP enum layout. It also depends on the SOC15 register access model, `amdgpu_device.reg_offset`, and the caller selecting this function only for Cyan Skillfish-compatible hardware.

## Risks
Wrong IP-to-base mapping causes register reads/writes to target the wrong MMIO ranges, which can break initialization broadly. The comment notes hardware has more IP blocks than the driver initializes; future code accessing an uninitialized IP block would fail or use null offsets. The cast to `uint32_t *` assumes generated base structures are layout-compatible with the register offset table. An incorrect `xcc_mask` would misrepresent graphics complex topology.

## Test Signals
Signals include successful device discovery/probe on Cyan Skillfish, correct MMIO access through SOC15 macros, no null `reg_offset` use for initialized IPs, and successful initialization of GC, SDMA, VCN, display, SMU/thermal/clock, and memory hub paths. Regression checks should compare generated IP offset headers with this mapping whenever Cyan Skillfish tables are regenerated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cyan_skillfish_reg_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c

## Purpose
`cz_ih.c` implements the Carrizo/VI interrupt handler IP block for AMDGPU. It configures the hardware interrupt ring buffer, provides IH ring callbacks for write-pointer retrieval, interrupt-vector decoding, and read-pointer updates, and exposes the `cz_ih_ip_block` lifecycle hooks used by VI ASIC initialization.

## Important APIs, Types, and Functions
The exported object is `const struct amdgpu_ip_block_version cz_ih_ip_block`, with type `AMD_IP_BLOCK_TYPE_IH`, version `3.0.0`, and `cz_ih_ip_funcs`. The internal `amd_ip_funcs` implementation covers early init, software init/fini, hardware init/fini, suspend/resume, idle wait, soft reset, and clock/power gating stubs.

Core functions are `cz_ih_irq_init()`, `cz_ih_irq_disable()`, `cz_ih_get_wptr()`, `cz_ih_decode_iv()`, and `cz_ih_set_rptr()`. `cz_ih_funcs` installs these as `amdgpu_ih_funcs`. `cz_ih_sw_init()` allocates the main IH ring at 64 KiB and the software IH ring at `IH_SW_RING_SIZE`, then calls `amdgpu_irq_init()`. `cz_ih_early_init()` adds the IRQ domain and installs `adev->irq.ih_funcs`.

## Control Flow
Hardware init disables interrupts, programs dummy-page and interrupt-control registers, writes the IH ring GPU base address, computes ring size with `order_base_2(ring_size / 4)`, enables overflow handling and write-pointer writeback, sets writeback addresses, clears RPTR/WPTR, optionally arms MSI rearm behavior, calls `pci_set_master()`, and enables interrupts. Hardware fini disables interrupts and waits briefly.

`cz_ih_get_wptr()` reads the little-endian write pointer from writeback memory. For the software ring it returns directly. For hardware, it checks the overflow bit, re-reads `mmIH_RB_WPTR` to avoid stale writeback state, warns on real overflow, advances `ih->rptr` to `(wptr + 16) & ptr_mask`, toggles `WPTR_OVERFLOW_CLEAR`, and returns `wptr & ptr_mask`. `cz_ih_decode_iv()` reads four dwords at `ih->rptr >> 2`, decodes legacy client, source id, source data, ring id, VMID, and PASID, then advances RPTR by 16 bytes. `cz_ih_set_rptr()` writes `mmIH_RB_RPTR`.

## State and Persistence Behavior
The file mutates in-memory AMDGPU interrupt state (`adev->irq.ih.enabled`, `adev->irq.ih.rptr`, `adev->irq.ih_soft.enabled`, and `adev->irq.ih_funcs`) and IH hardware registers. Ring memory and writeback memory are allocated by common IH helpers; this code only programs their addresses into the device. No state is persisted beyond the device lifecycle. Suspend disables the block and resume reinitializes it.

## Dependencies and Integration Points
Dependencies include `amdgpu_ih.h`, `amdgpu_irq` core helpers, PCI bus mastering, VI OSS/BIF register headers, MMIO helpers `RREG32`/`WREG32`, and field macros from generated mask headers. `vi.c` adds `cz_ih_ip_block` for Carrizo/Stoney-style VI APUs. The IRQ processing core later calls through `adev->irq.ih_funcs` to fetch WPTR, decode IVs, and commit RPTR.

## Risks
Incorrect ring size/address programming can make interrupts disappear or overwrite memory. Overflow handling deliberately skips to the last non-overwritten vector; that preserves forward progress but can drop interrupts. Decode layout assumes 16-byte legacy IV entries; incompatible hardware formats need different IH implementations. `cz_ih_set_clockgating_state()` and `cz_ih_set_powergating_state()` are TODO stubs, so power-management expectations are minimal. Timeout/reset paths depend on `SRBM_STATUS.IH_BUSY` being reliable.

## Test Signals
Signals include successful IRQ domain creation, ring allocation, MSI/non-MSI interrupt delivery, correct handling of IH writeback, no spurious overflow warnings under normal load, valid decoded VMID/PASID/source IDs, suspend/resume interrupt recovery, and `cz_ih_wait_for_idle()` returning without timeout. Fault-injection or stress tests should cover overflow behavior, soft reset when IH busy, and both hardware and software IH rings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.h

## Purpose
`cz_ih.h` is the public header for the Carrizo interrupt handler IP block. It lets VI-family device setup code reference the `cz_ih_ip_block` object implemented in `cz_ih.c`.

## Important APIs, Types, and Data
The header has one declaration: `extern const struct amdgpu_ip_block_version cz_ih_ip_block;`. It uses an include guard `__CZ_IH_H__`. The concrete type is defined elsewhere in AMDGPU core headers included by translation units that include this header.

## Control Flow and Integration
There is no control flow. The integration point is compile-time linkage: `vi.c` includes this header and passes `&cz_ih_ip_block` to `amdgpu_device_ip_block_add()` for relevant Carrizo/Stoney VI devices. The object then supplies lifecycle callbacks from `cz_ih.c`.

## State and Persistence Behavior
The header stores no state and has no persistence behavior. It only exposes a read-only global object defined in the C file.

## Dependencies
Users must include this header in a context where `struct amdgpu_ip_block_version` is declared. It depends on `cz_ih.c` being linked into the driver; otherwise the extern declaration would be unresolved.

## Risks
The main risk is integration mismatch: adding the IP block for unsupported ASICs would bind the wrong IH register programming and IV decode format. Removing or renaming the extern without updating `vi.c` breaks build/link. The header intentionally does not expose private helper functions, keeping the surface small.

## Test Signals
Build coverage should confirm the extern resolves and `vi.c` can add the block. Runtime signals belong mostly to `cz_ih.c`: successful IP block registration, interrupt initialization, and working IRQ delivery on Carrizo/Stoney hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/cz_ih.h -->
