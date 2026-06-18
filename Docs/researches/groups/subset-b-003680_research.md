# subset-b-003680 research

Grouped research for Nouveau NVKM graphics-engine files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgm107.fuc5.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/hubgm107.fuc5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/os.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/os.h

## Purpose
Defines the small error-code ABI shared between Nouveau graphics Falcon microcode headers and the host-side GR interrupt/debug code.

## Important APIs, types, and functions
- Include guard `__NVKM_GRAPH_OS_H__`.
- `E_BAD_COMMAND` is error code `0x00000001`.
- `E_CMD_OVERFLOW` is error code `0x00000002`.
- `E_BAD_FWMTHD` is error code `0x00000003`.

## Control flow
The header is declarative. Host C code includes it so FECS status values can be decoded consistently. In `gf100_gr_ctxctl_isr()`, `E_BAD_FWMTHD` causes the driver to print the FECS-submitted class, subchannel, method, and data instead of only reporting a generic ucode error.

## State and persistence
No state is stored. These constants form a persistent ABI with compiled Falcon firmware images.

## Dependencies and integration points
Included by `gf100.c` and paired with `fuc/*.h` microcode arrays. The constants integrate FECS firmware status reporting with NVKM logging and interrupt handling.

## Risks
The numeric values must stay synchronized with firmware. If a code is changed independently of the microcode, interrupt diagnostics will become misleading and bad firmware-method events may be misclassified.

## Test signals
Build coverage catches missing include guards or macro names. Runtime validation comes from FECS error interrupt logs matching expected decoded paths, especially `FECS MTHD ...` messages for `E_BAD_FWMTHD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/fuc/os.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/g84.c

## Purpose
Provides the NV84/G84-era Tesla graphics-engine implementation by extending the `nv50` GR path with a hardware TLB flush routine and class table.

## Important APIs, types, and functions
- `g84_gr_tlb_flush()` disables GR FIFO access, waits for PGRAPH virtual status registers to go idle, requests the MMU TLB flush through `0x100c80`, then re-enables GR access.
- `nv50_gr_status`, `nv50_gr_vstatus_0`, `nv50_gr_vstatus_1`, and `nv50_gr_vstatus_2` decode busy and per-unit idle status for timeout logging.
- `g84_gr_new()` constructs the engine through `nv50_gr_new_()`.
- `g84_gr` installs `nv50_gr_init`, `nv50_gr_intr`, `nv50_gr_chan_new`, `g84_gr_tlb_flush`, `nv50_gr_units`, and Tesla/NV50 object classes.

## Control flow
The flush path takes `nv50_gr.lock`, masks off GR access in `0x400500`, polls `0x400380`, `0x400384`, and `0x400388` until all encoded unit statuses are idle or two seconds elapse, emits detailed status logs on timeout, writes the flush request, waits for hardware to clear it, and restores GR access.

## State and persistence
The function mutates PGRAPH control register `0x400500` and MMU register `0x100c80` only for the duration of a flush. Long-lived state is the `nv50_gr` object and its spinlock inherited from the NV50 implementation.

## Dependencies and integration points
Depends on `nv50.h`, NVKM timer, NVKM bitfield formatting, and NVIF class IDs. It is used by GPU MMU invalidation paths on G84-family devices and shares most engine behavior with `nv50_gr`.

## Risks
Idle detection is register-encoding sensitive. A false idle can flush while GR is active; a false busy can cause avoidable timeouts. The spinlock and IRQ-save region protect GR access sequencing, so changes must not sleep inside the locked region except through existing polling helpers that are already used in this path.

## Test signals
Signals include absence of `PGRAPH TLB flush idle timeout fail`, successful GPU VM invalidation under rendering, and correct class exposure for `NV50_TWOD`, M2MF, compute, and `G82_TESLA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ga102.c

## Purpose
Implements the Ampere GA10x Nouveau GR backend for GPUs that are not managed by GSP-RM. It supplies Ampere-specific ZBC programming, Falcon reset and ACR bootloader descriptors, interrupt routing, nonstall reporting, netlist firmware parsing, and the `gf100_gr_func` table for `AMPERE_B`.

## Important APIs, types, and functions
- `ga102_gr_zbc_clear_color()` writes color ZBC entries through the GA102 `0x41bc*` register window; `ga102_gr_zbc` combines that with GP100 depth and GP102 stencil helpers.
- `ga102_gr_fecs_reset()` and `ga102_gr_gpccs_reset()` reset FECS/GPCCS with Ampere register sequences.
- `ga102_gr_fecs_acr` and `ga102_gr_gpccs_acr` describe v2 Falcon bootloader descriptors and bootloader entry points.
- `ga102_gr_oneinit_intr()` selects VFN interrupt routing, and `ga102_gr_nonstall()` reports nonstall vectors from `0x400160`.
- `ga102_gr_load()` parses `gr/NET_img` regions into FECS/GPCCS firmware blobs and SW register packs.
- `ga102_gr_new()` refuses to instantiate when `nvkm_gsp_rm()` owns GR.

## Control flow
Construction calls `gf100_gr_new_()` with `ga102_gr_fwif`. Firmware loading fetches `NET_img`, scans region IDs, converts register-list regions into `gf100_gr_pack` arrays, and loads FECS/GPCCS through `nvkm_acr_lsfw_load_bl_sig_net()`. Later generic `gf100_gr_init()` calls GA102 hooks for GPC MMU, ZCULL, FS, PES mask, FECS exceptions, ROP exceptions, SM exceptions, and context-control startup.

## State and persistence
State is stored in `struct gf100_gr`: netlist-derived `sw_nonctx1..4`, `sw_ctx`, `bundle`, `bundle_veid`, `bundle64`, `method`, ZBC arrays, topology, and Falcon firmware blobs. Hardware state persists in FECS/GPCCS, GR exception registers, VFN interrupt routing, and ZBC registers until reset.

## Dependencies and integration points
Depends on `gf100` common GR, `ctxgf100` GA102 context functions, TU102/GP102/GV100 helpers declared in `gf100.h`, ACR, GSP, VFN interrupts, firmware loader, and NVFW Falcon descriptor definitions. It exposes `AMPERE_B` and `AMPERE_COMPUTE_B` classes.

## Risks
`ga102_gr_load()` assumes required netlist regions are present before dereferencing them; malformed firmware can break initialization. GSP-managed devices must be rejected to avoid double ownership. Interrupt vector selection is platform-specific. Ampere ZBC and ROP register windows differ from prior chips, so reusing older helpers would silently program the wrong block.

## Test signals
Look for successful `NET_img` region debug logs, ACR bootstrap success for FECS and GPCCS, nonzero VFN interrupt handling, absence of FECS/GPCCS reset timeouts, working `AMPERE_B` class creation, and passing graphics/compute context-switch workloads without GR trap floods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf100.c

## Purpose
Provides the core Fermi-and-newer Nouveau graphics-engine implementation. It owns ZBC management, GR object class creation, per-channel graphics context setup, register-pack programming, FECS/GPCCS context-control startup, trap and interrupt decoding, global GR initialization/finalization/reset, firmware selection, and the shared constructor used by later chip files.

## Important APIs, types, and functions
- ZBC APIs: `gf100_gr_zbc_color_get()`, `gf100_gr_zbc_depth_get()`, `gf100_fermi_mthd_zbc_color()`, `gf100_fermi_mthd_zbc_depth()`, and `gf100_gr_zbc_init()`.
- Channel/context APIs: `gf100_gr_chan_new()`, `gf100_gr_chan_bind()`, `gf100_gr_chan_dtor()`, and `gf100_grctx_generate()`.
- Register programming: `gf100_gr_mmio()`, `gf100_gr_icmd()`, `gf100_gr_mthd()`, and many exported `gf100_gr_init_*` hooks.
- FECS/GPCCS: `gf100_gr_init_ctxctl()`, internal and external firmware loaders, FECS mailbox methods, context switch pause/resume, golden-save and bind-pointer helpers.
- Interrupts: `gf100_gr_intr()`, `gf100_gr_trap_intr()`, GPC/TPC/MP trap decoders, and `gf100_gr_ctxctl_isr()`.
- Constructors: `gf100_gr_new_()` and `gf100_gr_new()`.

## Control flow
`gf100_gr_new_()` allocates `struct gf100_gr`, constructs the `nvkm_gr` engine, selects a firmware interface, constructs FECS and GPCCS Falcon objects, and stores the selected function table. `gf100_gr_oneinit()` registers the interrupt handler, disables PMU power gating, discovers ROP/GPC/TPC/PPC topology, allocates shared pagepool/bundle/attribute buffers, computes tile and SM ordering, and prepares global state. `gf100_gr_init_()` optionally applies the GP107/GP108 reset workaround, grabs Falcon ownership, calls the generation-specific `init` hook, and enables interrupts.

The common `gf100_gr_init()` path disables GR access, programs GPC MMU and register packs, waits idle, applies optional chip hooks, enables FIFO access and exception masks, clears per-unit trap state, initializes ZBC entries, then starts context control through built-in microcode or external firmware. Channel creation maps global buffers into the channel VMM, lazily generates the golden context under `fecs.mutex`, allocates the per-channel MMIO-list buffer, and writes context patch entries through `grctx` callbacks. Interrupt handling resolves the active channel by instance pointer, decodes illegal methods/classes/data errors, delegates traps to unit-specific handlers, acknowledges FECS interrupts, and re-arms PGRAPH.

## State and persistence
Persistent driver state includes selected `gf100_gr_func`, firmware mode, Falcon blobs, firmware-derived or built-in register packs, topology fields, global context buffers, ZBC tables, tile/SM maps, golden context image `data`, context image sizes, and FECS disable count. Per-channel state includes VMM references, mapped pagepool/bundle/attribute/unknown buffers, a channel MMIO-list memory object, and VMA addresses embedded in the context image. Hardware state persists in GR registers, FECS/GPCCS Falcon memory, context images, exception masks, and ZBC entries until reset or reinitialization.

## Dependencies and integration points
Depends on NVKM core object, GPU memory, VMM, FIFO channel lookup, firmware loader, ACR secure boot, Falcon helpers, LTC ZBC programming, FB MMU fault buffers, PMU power gating, therm clock gating, timer polling, NVIF class/method definitions, and generation-specific `ctxgf100` functions. It is the shared backend used by GF100 through GA102 generation files.

## Risks
This file is high-risk because it coordinates hardware sequencing, firmware ABI, memory mappings, and interrupt recovery. Timeout loops around FECS commands, idle waits, and context-control startup are common failure points. Firmware and no-firmware paths use different context layouts. ZBC table consistency is checked only by `WARN_ON()` on L2 mismatch. Trap acknowledgement mistakes can lose diagnostics or create interrupt storms. Channel teardown must release VMM and memory references in the exact reverse ownership pattern.

## Test signals
Strong signals include successful module probe, `oneinit` topology matching hardware fuses, successful FECS/GPCCS startup, no `failed to construct context` logs, context switch pause/resume working, correct class enumeration, passing 2D/3D/compute workloads, ZBC ioctl success, clean suspend/resume, and useful GR trap logs rather than unknown interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf100.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf100.h

## Purpose
Defines the shared private interface for Fermi-and-newer Nouveau graphics engines. It describes the `struct gf100_gr` state container, per-generation function-table contracts, register-pack formats, microcode formats, channel state, address macros, and cross-generation helper prototypes.

## Important APIs, types, and functions
- Address macros `ROP_BCAST`, `ROP_UNIT`, `GPC_BCAST`, `GPC_UNIT`, `PPC_UNIT`, and `TPC_UNIT` encode GR unit register windows.
- `struct gf100_gr` contains the base GR engine, FECS/GPCCS Falcons, firmware blobs, loaded register packs, ZBC tables, topology, global memory buffers, tile/SM maps, and context image metadata.
- `struct gf100_gr_func` is the main per-generation vtable with hooks for oneinit, init, trap handling, firmware, topology limits, grctx, clock gating, ZBC, and supported classes.
- `struct gf100_gr_func_zbc`, `struct gf100_gr_chan`, `struct gf100_gr_init`, `struct gf100_gr_pack`, `struct gf100_gr_ucode`, and `struct gf100_gr_fwif` define core data contracts.
- Declares helpers exported across generation files, including GF100, GK104, GK20A, GM107, GM200, GP100, GP102, GV100, TU102, and GA102 support routines.

## Control flow
The header does not execute code but drives dispatch. `gf100.c` calls through `gf100_gr_func` hooks during construction, topology discovery, initialization, exception setup, ZBC programming, trap decoding, and firmware loading. Generation files fill only the hooks that differ from the common path.

## State and persistence
The declarations identify all persistent GR state. `struct gf100_gr` lives for the engine lifetime; `struct gf100_gr_chan` lives per FIFO channel object. Register packs and firmware blobs are retained until engine destruction because they are reused for init and context generation.

## Dependencies and integration points
Includes `priv.h`, GPU object, LTC, MMU, and Falcon definitions. It is the coupling point between chip-specific GR files, context generators such as `ctxgf100`, ACR firmware loaders, and common `nvkm_gr` engine methods.

## Risks
Vtable changes have wide blast radius. Adding a hook requires careful defaulting in all generation structures. Fixed maximums (`GPC_MAX`, `TPC_MAX_PER_GPC`) must match all supported hardware. Structure layout assumptions are used by several source files, so lifetime or ownership changes can create leaks, use-after-free, or incorrect context images.

## Test signals
Build coverage across all Nouveau GPU generations is the primary static signal. Runtime signals are successful construction for each generation, correct class tables, no missing hook NULL dereferences, and context buffer sizes/topology values that match hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf104.c

## Purpose
Specializes the common GF100 GR implementation for GF104-class Fermi GPUs by replacing selected MMIO register packs, context generator data, and supported classes.

## Important APIs, types, and functions
- Exports register arrays `gf104_gr_init_ds_0`, `gf104_gr_init_tex_0`, and `gf104_gr_init_sm_0`, reused by other Fermi variants.
- Defines local PE and MMIO pack arrays, with `gf104_gr_pack_mmio` feeding the common `gf100_gr_mmio()` path.
- `gf104_gr_new()` constructs through `gf100_gr_new_()`.
- `gf104_gr` uses common GF100 hooks with `gf104_grctx` and Fermi class IDs.

## Control flow
Initialization follows `gf100_gr_init()`, but `gr->func->mmio` points at `gf104_gr_pack_mmio`. That pack swaps in GF104 DS/TEX/PE/SM programming while retaining most GF100 packs. Context-control startup uses GF100 FECS/GPCCS ucode unless external firmware is requested.

## State and persistence
The file contributes immutable register-pack state and a static function table. Runtime state is stored in the shared `struct gf100_gr` object, especially selected MMIO pack and `gf104_grctx`.

## Dependencies and integration points
Depends on `gf100.h`, `ctxgf100.h`, GF100 ucode, and NVIF Fermi class definitions. It integrates as the chip-specific constructor called by Nouveau device tables.

## Risks
Register-pack differences are hardware-specific and mostly magic values. Incorrect reuse by another chip can leave GR units misconfigured. The file relies on the common GF100 firmware and hooks being compatible with GF104.

## Test signals
Booting a GF104-family board, successful class creation for `FERMI_A` and compute, clean context generation using `gf104_grctx`, and absence of GR trap or context-control startup errors validate the file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf108.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf108.c

## Purpose
Adapts the GF100 common GR path for GF108 by providing GF108-specific register initialization packs, a small `0x405a14` initialization hook, GF108 context data, and Fermi B class exposure.

## Important APIs, types, and functions
- Exports `gf108_gr_init_gpc_unk_0` and `gf108_gr_init_setup_1`, reused by GF110, GF119, GK104, and later packs.
- Defines GF108 GPC/PE pack variants and `gf108_gr_pack_mmio`.
- `gf108_gr_init_r405a14()` writes `0x80000000` to `0x405a14`.
- `gf108_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
The common `gf100_gr_init()` sequence programs GF108's MMIO pack, calls `init_r405a14`, then uses common zcull, exceptions, FECS/GPCCS, and trap handling. Object creation exposes both `FERMI_A` and `FERMI_B` graphics classes plus compute.

## State and persistence
Static state is the MMIO pack and function table. Persistent runtime state is common `gf100_gr` state populated with `gf108_grctx`, GF100 firmware mode, and ZBC/context buffers.

## Dependencies and integration points
Depends on GF100 common hooks, GF104 register arrays, GF108 context generator data, and NVIF class IDs. It also provides register arrays consumed by later Fermi and Kepler code.

## Risks
The extra `0x405a14` write is chip-specific; omitting or moving it can regress GF108 initialization. Exported register arrays make accidental incompatible reuse possible.

## Test signals
Successful initialization on GF108/GF10x low-end boards, no `0x405a14`-related GR hangs, correct `FERMI_B` class availability, and clean 2D/3D context switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf110.c

## Purpose
Specializes Fermi GF110-class GR by providing the GF110 SM register pack, a composite MMIO pack, GF110 context data, and expanded Fermi graphics/compute class support.

## Important APIs, types, and functions
- Defines `gf110_gr_init_sm_0` with GF110-specific SM values.
- Defines `gf110_gr_pack_mmio`, combining GF100, GF108, and GF110 arrays.
- `gf110_gr_new()` constructs through `gf100_gr_new_()`.
- `gf110_gr` uses common GF100 hooks, `gf110_grctx`, and supports `FERMI_A/B/C` plus compute A/B.

## Control flow
Initialization uses the common GF100 path with the GF110 pack. The file does not override firmware, traps, zcull, or exception logic, so the shared FECS/GPCCS and ZBC behavior applies.

## State and persistence
Only static register data and the function table are defined here. The runtime engine state is in `struct gf100_gr` and includes the selected context generator and class table.

## Dependencies and integration points
Depends on GF100/GF108 register arrays, GF100 built-in microcode, GF110 context generation, and NVIF Fermi class definitions. Device bring-up selects this constructor for GF110-family GPUs.

## Risks
GF110 inherits many arrays from related Fermi chips; the few changed SM values are critical to matching the chip. Class exposure must match hardware capabilities, or userspace may submit unsupported methods.

## Test signals
Validation includes class enumeration for `FERMI_C`/`FERMI_COMPUTE_B`, successful `gf110_grctx` context generation, no shader exception misconfiguration, and stable rendering/compute workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf117.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf117.c

## Purpose
Adds GF117-specific GR support, including PPC/PES-era register packs, GF117 FECS/GPCCS built-in microcode, a modified zcull setup routine, and the GF117 function table.

## Important APIs, types, and functions
- Exports `gf117_gr_init_pes_0`, `gf117_gr_init_wwdx_0`, and `gf117_gr_init_cbm_0` for reuse by Kepler packs.
- Embeds `hubgf117.fuc3.h` and `gpcgf117.fuc3.h` as `gf117_gr_fecs_ucode` and `gf117_gr_gpccs_ucode`.
- `gf117_gr_init_zcull()` writes tile-bank mappings and uses a later broadcast register offset `0x3fd4`.
- `gf117_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
The common init path programs `gf117_gr_pack_mmio`, then calls `gf117_gr_init_zcull()` instead of the GF100 zcull hook. FECS/GPCCS startup uses GF117 built-in ucode unless external firmware is selected. The function table sets `ppc_nr = 1`.

## State and persistence
Static state includes register packs, microcode arrays, and the function table. Runtime zcull/tile state comes from `gf100_gr_oneinit_tiles()` and is written to GPC registers during init.

## Dependencies and integration points
Depends on GF100 common code, GF119/GF108 arrays, GF117 context generation, and GF117 microcode headers. Its exported PES/WWDX/CBM arrays are used by Kepler-generation files.

## Risks
The zcull tile count has a TODO for litter values across GF117-GM2xx and falls back to function-table limits when available. Wrong tile counts can affect zcull correctness/performance. Built-in microcode must match GF117 register lists.

## Test signals
Signals include successful FECS/GPCCS startup with GF117 ucode, stable zcull behavior under 3D workloads, no PPC exception storms, and correct Fermi class availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf117.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf119.c

## Purpose
Provides GF119-specific Fermi GR register packs and function-table data while relying on the common GF100 initialization, firmware, context, trap, and ZBC logic.

## Important APIs, types, and functions
- Exports reusable register arrays such as `gf119_gr_init_pd_0`, `gf119_gr_init_ds_0`, `gf119_gr_init_prop_0`, `gf119_gr_init_gpm_0`, `gf119_gr_init_gpc_unk_1`, `gf119_gr_init_tex_0`, `gf119_gr_init_sm_0`, and `gf119_gr_init_fe_1`.
- Defines local PE, WWDx, TPCCS, and full MMIO pack arrays.
- `gf119_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
The chip uses the standard GF100 `oneinit`, `init`, trap, FECS, and channel paths. During init, `gf119_gr_pack_mmio` is programmed and then common hooks enable zcull, exceptions, ZBC, and context control.

## State and persistence
The file contributes immutable register tables. Runtime state is shared `struct gf100_gr` populated with `gf119_grctx`, GF100 firmware choice, and class table.

## Dependencies and integration points
Depends on GF100 common code and GF119 context generation. It also acts as a provider of register arrays for GF117 and Kepler packs.

## Risks
GF119 arrays are reused widely, so changing them can regress multiple chips. Register values are undocumented and hardware-sensitive. The file shares GF100 ucode, so any ABI mismatch would surface only at initialization or context switching.

## Test signals
Successful probe on GF119 hardware, clean context generation with `gf119_grctx`, class support for `FERMI_A/B/C` and compute, no FECS startup failures, and stable rendering/compute workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk104.c

## Purpose
Implements GK104 Kepler GR support on top of the GF100 framework. It supplies Kepler register packs, block-level clock-gating packs, Kepler FECS/GPCCS built-in microcode, and Kepler-specific init hooks for SKED, FECS exceptions, active FBPs, PPC exceptions, and VSC stream master.

## Important APIs, types, and functions
- Exports Kepler register arrays and `gk104_gr_pack_mmio`.
- Exports many `gk104_clkgate_blcg_init_*` arrays and `gk104_clkgate_pack`.
- `gk104_gr_init_sked_hww_esr()`, `gk104_gr_init_fecs_exceptions()`, `gk104_gr_init_rop_active_fbps()`, `gk104_gr_init_ppc_exceptions()`, and `gk104_gr_init_vsc_stream_master()` customize common init.
- Embeds `hubgk104.fuc3.h` and `gpcgk104.fuc3.h`.
- `gk104_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
Common `gf100_gr_init()` programs `gk104_gr_pack_mmio`, optionally applies clock-gating through therm, calls the GK104 stream-master, zcull, ROP/FBE, FECS, SKED, PPC, and exception hooks, then starts context control with Kepler ucode. `oneinit` uses the common topology and tile algorithms with `ppc_nr = 1`.

## State and persistence
Static state includes register packs, clock-gating packs, microcode arrays, function table, and class table. Runtime state is in `struct gf100_gr`, including Kepler topology, tile maps, ZBC, and context buffers.

## Dependencies and integration points
Depends on `gf100.h`, `gk104.h`, `ctxgf100.h`, therm clock-gating APIs, GF117 register arrays, and NVIF Kepler classes. Several later Kepler/Maxwell files reuse exported GK104 arrays and hooks.

## Risks
Clock-gating tables can cause difficult hangs if programmed on the wrong block. PPC exception setup depends on discovered `ppc_mask`. Active FBP masks must match fuse state. Built-in ucode and register packs are tightly coupled.

## Test signals
Signals include correct Kepler class exposure, BLCG initialization without hangs, FECS startup with GK104 ucode, correct ROP/FBE masks from `0x120074`, PPC exception clearing, and stable graphics/compute workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk104.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk104.h

## Purpose
Declares GK104 block-level clock-gating register arrays so other GR generation files can reuse the same Kepler clock-gating data.

## Important APIs, types, and functions
- Includes `<subdev/therm.h>` for `struct nvkm_therm_clkgate_init`.
- Extern declarations cover main, rstr2d, unknown, GCC, SKED, GPC context-control, GPC subblocks, ROP, crop/zrop, and PXBAR clock-gating arrays.
- Uses include guard `__GK104_GR_H__`.

## Control flow
No runtime control flow. Files include this header and assemble clock-gating packs that are later consumed by `nvkm_therm_clkgate_init()`.

## State and persistence
No state is defined here. The declared arrays are immutable static data defined in `gk104.c` and programmed into hardware by the therm clock-gating helper.

## Dependencies and integration points
Used by `gk104.c`, `gk110.c`, and related generation files that share Kepler BLCG settings. It links the GR backend to the therm subdev clock-gating interface.

## Risks
The header intentionally exposes low-level register tables. Adding declarations without definitions breaks builds; reusing arrays on incompatible chips can cause GR or clock-gating instability.

## Test signals
Build coverage catches declaration/definition mismatches. Runtime validation is successful clock-gating initialization and absence of GR hangs on chips that use these arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk104.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk110.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk110.c

## Purpose
Adds GK110 Kepler GR support, including GK110 register-pack variants, microcode, clock-gating reuse, an adjusted SM register hook, and class support for Kepler B.

## Important APIs, types, and functions
- Exports GK110 register arrays such as `gk110_gr_init_fe_0`, `gk110_gr_init_ds_0`, `gk110_gr_init_sked_0`, `gk110_gr_init_cwd_0`, `gk110_gr_init_gpc_unk_1`, `gk110_gr_init_tex_0`, and `gk110_gr_init_sm_0`.
- Provides `gk110_gr_init_419eb4()` with GK110-specific masking.
- Embeds GK110 FECS/GPCCS microcode.
- Defines `gk110_gr_new()`, `gk110_gr_fwif`, and the GK110 function table.

## Control flow
The common GF100 lifecycle is used. During init, GK110's MMIO pack is programmed, GK104 hooks handle VSC stream master, active FBPs, SKED, and PPC exceptions, while GK110 overrides `init_419eb4`. The function table sets `ppc_nr = 2` and uses `gk110_grctx`.

## State and persistence
Static state consists of register packs, ucode arrays, and the function table. Runtime topology records two PPCs per GPC and context state generated by `gk110_grctx`.

## Dependencies and integration points
Depends on GF100 common code, GK104 helpers/clock-gating declarations, GF117 arrays, GK110 context generation, and NVIF Kepler B classes. Exported arrays are reused by GK110B and GK208.

## Risks
GK110 has a larger PPC/TPC layout than GK104; incorrect `ppc_nr` or exception masks can leave PPC traps uncleared. The file mixes arrays from several generations, so changes must be checked on actual GK110 hardware.

## Test signals
Successful `KEPLER_B` and compute class creation, correct two-PPC topology, clean PPC/SM exception handling, FECS/GPCCS startup with GK110 ucode, and stable compute-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk110b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk110b.c

## Purpose
Specializes GK110 support for GK110B by replacing L1C and SM register packs and selecting the GK110B context generator while reusing GK110 microcode and most common Kepler hooks.

## Important APIs, types, and functions
- Defines `gk110b_gr_init_l1c_0` and `gk110b_gr_init_sm_0`.
- Defines `gk110b_gr_pack_mmio`, mostly composed from GK104/GK110/GF117 arrays plus GK110B L1C/SM arrays.
- `gk110b_gr_new()` constructs via `gf100_gr_new_()`.
- `gk110b_gr` uses `gk110b_grctx`, GK110 ucode, `ppc_nr = 2`, and Kepler B classes.

## Control flow
Initialization is the shared GF100 path with the GK110B MMIO pack. GK104 and GK110 hooks configure stream master, zcull, active FBPs, FECS/SKED/PPC exceptions, and `419eb4`.

## State and persistence
Only static pack/function data is defined here. Runtime state is common `gf100_gr` state with GK110B context data and topology.

## Dependencies and integration points
Depends on GF100, GK104, GK110, GF117, and `gk110b_grctx`. It is selected by device tables for GK110B-family GPUs.

## Risks
The distinction from GK110 is narrow but hardware-sensitive. Accidentally using GK110 SM/L1C values on GK110B may cause subtle shader/cache failures. Reusing GK110 ucode assumes context-control ABI compatibility.

## Test signals
Probe on GK110B hardware, correct `gk110b_grctx` golden context, no SM/L1C trap storms, and stable rendering/compute workloads are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk110b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk208.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk208.c

## Purpose
Implements GK208 GR support with GK208-specific register packs, fuc5 built-in FECS/GPCCS microcode, and Kepler B class exposure.

## Important APIs, types, and functions
- Defines GK208 main, DS, GPC, setup, TEX, L1C, and full MMIO pack arrays.
- Exports `gk208_gr_init_gpc_unk_0`, reused by GM107.
- Embeds `hubgk208.fuc5.h` and `gpcgk208.fuc5.h`.
- `gk208_gr_new()` constructs via `gf100_gr_new_()`.

## Control flow
Common GF100 init programs `gk208_gr_pack_mmio`, then uses GK104 hooks for stream master, ROP FBP masks, SKED, and PPC exceptions. It uses `gf117_gr_init_zcull()`, GK208 fuc5 microcode, `ppc_nr = 1`, and `gk208_grctx`.

## State and persistence
Static state is register packs, ucode arrays, and function table. Runtime state is common GR topology, ZBC, context buffers, and Falcon state.

## Dependencies and integration points
Depends on GF100 common code, GK110 and GK104 arrays, GF117 arrays, GF119 arrays, GK208 context data, and NVIF Kepler B classes.

## Risks
GK208 uses fuc5 microcode and a compact topology; register pack or microcode mismatches can lead to context-control timeouts. Exported GPC arrays should not be changed without checking GM107 reuse.

## Test signals
Signals include FECS/GPCCS startup with GK208 fuc5 images, correct `KEPLER_B` class operation, stable zcull and context switching, and no GPC/TPC trap floods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk208.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk20a.c

## Purpose
Implements Tegra GK20A GR support with external NVIDIA firmware loading and conversion of firmware-provided register lists into the common `gf100_gr_pack` format.

## Important APIs, types, and functions
- `gk20a_gr_av_to_init_()`, `gk20a_gr_av_to_init()`, `gk20a_gr_aiv_to_init()`, and `gk20a_gr_av_to_method()` convert firmware blobs into MMIO, context, bundle, and method packs.
- `gk20a_gr_wait_mem_scrubbing()` waits for FECS/GPCCS memory scrubbing to finish.
- `gk20a_gr_init()` is a Tegra-specific init path that loads `sw_nonctx`, waits for scrubbing/idle, programs MMU/zcull/FBP/exceptions, initializes ZBC, and starts context control.
- `gk20a_gr_load_sw()` and `gk20a_gr_load()` load required firmware blobs.
- `gk20a_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
Firmware loading pulls FECS/GPCCS inst/data and SW netlists from firmware files, converts them into runtime packs, and marks the engine as firmware-backed. Init clears SCC RAM, applies firmware-provided noncontext registers, waits for Falcon memory scrubbing, configures basic GR registers and exceptions, then starts the external context-control firmware through `gf100_gr_init_ctxctl()`.

## State and persistence
Firmware-derived packs are stored in `gr->sw_nonctx`, `gr->sw_ctx`, `gr->bundle`, and `gr->method` until destructor cleanup. FECS/GPCCS firmware blobs live in `gr->fecs` and `gr->gpccs`. Hardware state persists in GR registers and Falcon memory after init.

## Dependencies and integration points
Depends on firmware files under `nvidia/gk20a`, NVKM firmware blob loader, timer polling, GF100 common context-control code, and GK20A context data. It is compiled conditionally with Tegra firmware declarations.

## Risks
All required firmware files must be present; this path has no no-firmware fallback. Blob conversion trusts sizes to be multiples of expected structs. `gk20a_gr_av_to_method()` supports only 16 classes. Memory-scrubbing timeouts block init.

## Test signals
Signals include successful firmware load of all GK20A blobs, successful pack conversion, no FECS/GPCCS scrubbing timeout logs, valid `KEPLER_C` class operation, and stable Tegra graphics workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm107.c

## Purpose
Implements GM107 Maxwell A GR support using the GF100 framework with Maxwell register packs, BIOS-driven initialization hooks, GPC MMU changes, Maxwell shader exception masks, and GM107 fuc5 microcode.

## Important APIs, types, and functions
- Defines many GM107 register arrays and `gm107_gr_pack_mmio`.
- `gm107_gr_init_bios()` programs BIOS P0260-derived register/data sequences.
- `gm107_gr_init_bios_2()` executes a BIOS init script referenced from BIT P table data while preserving `0x619444`.
- `gm107_gr_init_gpc_mmu()` writes broadcast MMU debug buffer registers.
- `gm107_gr_init_400054()`, `gm107_gr_init_504430()`, and `gm107_gr_init_shader_exceptions()` override common register hooks.
- Embeds `hubgm107.fuc5.h` and `gpcgm107.fuc5.h`.

## Control flow
Common GF100 initialization programs Maxwell register packs, runs BIOS hooks before/after selected fixed initialization, configures GPC MMU, stream master, zcull, active FBPs, SKED/PPC/ROP exceptions, TPC exception registers, ZBC, and fuc5 context control. `oneinit` discovers topology with `ppc_nr = 2`.

## State and persistence
Static register packs and built-in ucode are compiled into the driver. Runtime state includes BIOS-derived register programming, topology, ZBC, context buffers, and FECS/GPCCS Falcon state.

## Dependencies and integration points
Depends on GF100 common code, GK110/GK208/GK104 helpers, BIOS BIT/P0260 parsing and init scripts, FB MMU buffers, GM107 context data, and NVIF Maxwell classes.

## Risks
BIOS table parsing is conditional and platform-sensitive; incorrect script execution can disturb unrelated display state. The saved/restored `0x619444` register indicates a cross-subsystem side effect. Maxwell register packs are large and hardware-specific.

## Test signals
Validate GM107 probe, BIOS init debug behavior, successful fuc5 FECS/GPCCS startup, class support for `MAXWELL_A`, no shader exception storm, and stable suspend/resume and graphics workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm200.c

## Purpose
Implements GM200/GM204/GM206 Maxwell B GR support with secure firmware loading, ACR bootloader descriptor handling, Maxwell B topology/tile hooks, GM200 MMU/LTC/ROP hooks, and firmware-only initialization.

## Important APIs, types, and functions
- `gm200_gr_nofw()` rejects no-firmware operation.
- `gm200_gr_acr_bld_write()` and `gm200_gr_acr_bld_patch()` build/adjust v1 Falcon bootloader descriptors.
- `gm200_gr_fecs_acr` and `gm200_gr_gpccs_acr` describe FECS/GPCCS secure loading.
- `gm200_gr_load()` loads signed FECS/GPCCS firmware and SW register packs through `gk20a_gr_load_sw()`.
- `gm200_gr_rops()`, `gm200_gr_init_gpc_mmu()`, `gm200_gr_init_num_active_ltcs()`, `gm200_gr_init_ds_hww_esr_2()`, and tile-map helpers customize common init.
- `gm200_gr_new()` constructs with firmware interfaces for GM200-family chips.

## Control flow
The constructor selects `gm200_gr_load()` only; fallback returns `-ENODEV`. Firmware loading populates signed FECS/GPCCS Falcon images and firmware-derived SW packs. Common init uses firmware-provided noncontext packs, GM200 MMU/LTC/ROP hooks, BIOS init from GM107, Maxwell exception hooks, ZBC, and external firmware context control.

## State and persistence
Persistent state includes ACR-loaded firmware metadata, SW packs from firmware, tile maps for special 2/4/6 GPC configurations, and global context/ZBC/topology state in `gf100_gr`.

## Dependencies and integration points
Depends on ACR, NVFW Falcon descriptors, firmware loader, GK20A SW netlist conversion, GM107 BIOS helpers, GF100 common engine code, and GM200 context data. Firmware declarations cover GM200, GM204, and GM206.

## Risks
Firmware is mandatory. Bootloader descriptor address adjustment must match WPR relocation. Hardcoded tile maps have comments noting incomplete reverse engineering. Incorrect FBP/LTC fuse reads can break ROP or cache setup.

## Test signals
Successful load of signed firmware and SW packs, ACR bootstrap success, correct tile mapping on 2/8, 4/16, and 6/24 configurations, no `firmware unavailable` failures, and working `MAXWELL_B` graphics/compute classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm20b.c

## Purpose
Implements Tegra GM20B Maxwell B GR support with FECS secure loading, non-secure GPCCS blob loading, Tegra-specific bootloader descriptors, GPC MMU programming, and GK20A-style firmware netlist initialization.

## Important APIs, types, and functions
- `gm20b_gr_acr_bld_write()` and `gm20b_gr_acr_bld_patch()` handle Falcon bootloader descriptors with high address fields.
- `gm20b_gr_fecs_acr` describes FECS ACR loading.
- `gm20b_gr_init_gpc_mmu()` optionally bypasses secure-boot MMU checks when no ACR exists, then programs GM20B MMU registers.
- `gm20b_gr_set_hww_esr_report_mask()` writes Maxwell warning masks.
- `gm20b_gr_load()` loads signed FECS, raw GPCCS inst/data, and SW packs.
- `gm20b_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
Firmware load first secures FECS through ACR, loads GPCCS directly, marks firmware mode, then loads SW netlists. Init uses `gk20a_gr_init()`, which is tailored for Tegra firmware-provided noncontext registers and memory-scrubbing waits, while GM20B hooks provide MMU and warning-mask differences.

## State and persistence
Runtime state includes firmware blobs, SW packs, ACR bootloader descriptors, and common `gf100_gr` context/ZBC/topology fields. Hardware state includes optional MMU bypass register `0x100ce4` and GR MMU registers.

## Dependencies and integration points
Depends on ACR, firmware loader, GK20A init/SW conversion, GM200 topology/tile helpers, GM20B context data, and Tegra-specific firmware files.

## Risks
The non-secure boot bypass path warns that failure should lead to later errors. FECS and GPCCS are loaded through different mechanisms. Firmware availability is mandatory on Tegra. Address packing in bootloader descriptors is easy to get wrong.

## Test signals
Signals include FECS ACR load success, GPCCS firmware load success, absence of secure-boot bypass warnings on secure systems, no memory-scrubbing timeout, and working `MAXWELL_B` classes on Tegra 210.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp100.c

## Purpose
Implements GP100 Pascal A GR support, adding Pascal ZBC register programming, FECS/shader exception differences, active FBP masking, and the GP100 function table.

## Important APIs, types, and functions
- `gp100_gr_zbc_clear_color()` and `gp100_gr_zbc_clear_depth()` program Pascal ZBC entries in the `0x4180*` window.
- `gp100_gr_zbc` supplies color/depth ZBC hooks.
- `gp100_gr_init_shader_exceptions()`, `gp100_gr_init_419c9c()`, `gp100_gr_init_fecs_exceptions()`, and `gp100_gr_init_rop_active_fbps()` customize init.
- `gp100_gr_new()` constructs using `gm200_gr_load()` and GM200 ACR descriptors.

## Control flow
Initialization follows the common GF100 path with GM200-style firmware-derived SW packs. GP100 hooks adjust FECS exception mask, L1/SM registers, ROP active FBP masks, Pascal ZBC programming, and shader exception masks. Firmware loading is mandatory through the GM200 loader.

## State and persistence
ZBC state is stored in common `gr->zbc_color` and `gr->zbc_depth` arrays and persisted to Pascal registers during init or ZBC allocation. Function table limits specify six GPCs, five TPCs per GPC, and two PPCs.

## Dependencies and integration points
Depends on GF100 common code, GM200 firmware/ACR path, GM200 MMU/LTC/tile hooks, GK104 exception hooks, and GP100 context data. Exposes `PASCAL_A` and `PASCAL_COMPUTE_A`.

## Risks
ZBC indexing subtracts one from the logical ZBC index, so table bounds and LTC min/max contracts matter. Firmware is mandatory. Pascal FBP count masking differs from GM200 and is explicitly called out in a comment.

## Test signals
Successful signed firmware load, correct `PASCAL_A` class exposure, ZBC clear allocation working for color/depth, no FECS exception misconfiguration, and stable graphics/compute workloads on GP100.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp102.c

## Purpose
Implements GP102 Pascal B GR support and extends GP100 ZBC handling with stencil entries plus a SWDX PES mask initialization hook.

## Important APIs, types, and functions
- `gp102_gr_zbc_stencil_get()` allocates or finds stencil ZBC entries and informs LTC through `nvkm_ltc_zbc_stencil_get()`.
- `gp102_gr_zbc_clear_stencil()` programs stencil ZBC registers.
- `gp102_gr_zbc` combines GP100 color/depth with GP102 stencil hooks.
- `gp102_gr_init_swdx_pes_mask()` reads per-GPC PES masks and writes the packed mask to `0x4181d0`.
- `gp102_gr_new()` uses `gm200_gr_load()` and GM200 ACR descriptors.

## Control flow
Common init uses GM200-style firmware packs and GP102 hooks for ZBC, PES mask, FECS/shader exceptions, and Pascal B context data. ZBC allocation follows the GF100 table search pattern and writes hardware immediately after reserving an entry.

## State and persistence
Adds `gr->zbc_stencil[]` usage to common GR state. Function table records six GPCs, five TPCs, and three PPCs. Hardware state includes the SWDX PES mask and stencil ZBC registers.

## Dependencies and integration points
Depends on GP100 ZBC helpers, GM200 firmware path, GF100 common initialization, GK104/GF117 hooks, LTC stencil ZBC support, and `gp102_grctx`. Exposes `PASCAL_B` classes.

## Risks
Stencil ZBC must stay consistent with LTC state or clears can use wrong compression metadata. PES mask construction assumes `GPC_UNIT(gpc, 0x0c50)` layout. Firmware is mandatory.

## Test signals
Signals include successful stencil ZBC allocation, correct PES mask programming, `PASCAL_B` class creation, no ZBC WARN_ON mismatch, and stable workloads using stencil/depth clears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp104.c

## Purpose
Provides GP104/GP106 Pascal B GR function-table support, mostly reusing GP102 behavior with GP104 context data and firmware declarations.

## Important APIs, types, and functions
- Defines `gp104_gr`, a `gf100_gr_func` table using GM200/GK104/GP100/GP102 hooks.
- `gp104_gr_fwif` uses `gm200_gr_load()` and GM200 ACR descriptors.
- `gp104_gr_new()` constructs through `gf100_gr_new_()`.
- Firmware declarations cover both GP104 and GP106 GR firmware sets.

## Control flow
The engine follows the shared GF100 construction and GM200 firmware load path. Init uses GM200 MMU/LTC/tile hooks, GP100 FECS/shader exceptions, GP102 PES mask and ZBC with stencil, and `gp104_grctx`.

## State and persistence
No local mutable state is declared. Persistent runtime state is common `gf100_gr` firmware, topology, context, ZBC, and Falcon state. The function table advertises six GPCs, five TPCs, and three PPCs.

## Dependencies and integration points
Depends on GF100 common code, GM200 firmware path, GP100 and GP102 exported hooks, and GP104 context data. Exposes Pascal B classes to userspace.

## Risks
Because the file is mostly a function table, wrong hook selection is the main risk. GP104/GP106 must be compatible with GP102's PES/ZBC assumptions and GM200 ACR loading.

## Test signals
Signals include successful GP104/GP106 firmware load, correct Pascal B class creation, `gp104_grctx` context generation, ZBC stencil operation, and stable rendering/compute workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp107.c

## Purpose
Defines the GP107 Pascal B GR function table and firmware interface. It is also reused by GP108 with a different ACR descriptor format.

## Important APIs, types, and functions
- Exports `const struct gf100_gr_func gp107_gr`.
- `gp107_gr_new()` uses `gm200_gr_load()` with GM200 ACR descriptors.
- Firmware declarations cover GP107 FECS/GPCCS and SW netlist blobs.
- Function table sets smaller topology limits: two GPCs, three TPCs, one PPC.

## Control flow
The common GF100 lifecycle and GM200 firmware loader are used. Init combines GM200 MMU/LTC/tile hooks, GP100 FECS/shader exception hooks, GP102 PES/ZBC hooks, and `gp107_grctx`.

## State and persistence
No local mutable state. Runtime state is in `gf100_gr`, with topology limits and context generator selected by the function table.

## Dependencies and integration points
Depends on GM200 firmware loading, GP100/GP102 hooks, GF100 common engine code, and GP107 context generation. `gp108.c` references the exported `gp107_gr` table.

## Risks
The exported function table makes GP108 share all GP107 behavior except ACR descriptors. If GP108 needs different hooks, this reuse can hide bugs. The GP107/GP108 reset workaround in `gf100_gr_init_()` is relevant to this generation.

## Test signals
Successful firmware load, no GR reset workaround regressions on cold boot, correct Pascal B class exposure, stable context switching, and no PES/ZBC mismatch warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp108.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp108.c

## Purpose
Provides GP108-specific ACR bootloader descriptor support and firmware declarations while reusing the GP107 GR function table.

## Important APIs, types, and functions
- `gp108_gr_acr_bld_write()` and `gp108_gr_acr_bld_patch()` handle `flcn_bl_dmem_desc_v2` descriptors.
- Exports `gp108_gr_gpccs_acr` and `gp108_gr_fecs_acr`.
- `gp108_gr_fwif` uses `gm200_gr_load()` with the GP108 v2 ACR functions and `gp107_gr`.
- `gp108_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
Firmware loading is delegated to `gm200_gr_load()`, but FECS/GPCCS LSF setup uses v2 descriptor builders from this file. Once firmware is loaded, all init/control flow follows the GP107 function table and common GF100 lifecycle.

## State and persistence
No local mutable state. ACR descriptor data is written to WPR through the ACR helper. Runtime GR state is the GP107 common state stored in `struct gf100_gr`.

## Dependencies and integration points
Depends on GF100 declarations, GM200 firmware loader, GP107 exported function table, ACR, and NVFW v2 Falcon descriptor structures.

## Risks
Descriptor format is the main differentiator. Using GM200 v1 descriptors would boot invalid firmware. Sharing GP107 hooks assumes GP108 topology and register programming compatibility.

## Test signals
Successful GP108 signed firmware boot, v2 descriptor dump sanity, no FECS/GPCCS bootstrap failure, and stable Pascal B workloads after cold boot/reset workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp10b.c

## Purpose
Implements Tegra GP10B Pascal A GR support with Tegra-style ACR descriptors, a compact Pascal function table, and signed firmware loading through the GM200 path.

## Important APIs, types, and functions
- `gp10b_gr_gpccs_acr` uses GM20B bootloader descriptor helpers and forces privileged GPCCS load.
- `gp10b_gr` defines a Pascal A function table with one GPC, two TPCs, one PPC, `gp100_grctx`, and GP100 ZBC hooks.
- `gp10b_gr_fwif` uses `gm200_gr_load()` with `gm20b_gr_fecs_acr` and `gp10b_gr_gpccs_acr`.
- `gp10b_gr_new()` constructs through `gf100_gr_new_()`.

## Control flow
Firmware loading follows the GM200 signed-firmware path, but ACR descriptor construction uses GM20B-style descriptors. Init uses the common GF100 path with GM200 MMU, GK104 stream/exception helpers, GP100 FECS/shader/ZBC hooks, and GP10B topology constants.

## State and persistence
No local mutable state. Runtime state is common GR state populated from signed firmware blobs and SW netlists. Function-table topology constrains context and SM/tile setup.

## Dependencies and integration points
Depends on GF100 common code, GM200 firmware loading, GM20B ACR helpers, GP100 hooks, and Tegra 186 firmware files. Exposes Pascal A classes.

## Risks
Topology constants are small and must match Tegra GP10B. Mixing GM20B ACR descriptors with GM200 loading must remain compatible. Firmware is mandatory and conditionally declared for Tegra 186.

## Test signals
Successful GP10B firmware load, ACR bootstrap of FECS/GPCCS, correct Pascal A class creation, no topology-derived context errors, and stable Tegra graphics workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gt200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gt200.c

## Purpose
Defines GT200 Tesla GR support by selecting the common NV50 GR implementation, the G84 TLB flush routine, and a GT200-specific class table.

## Important APIs, types, and functions
- `gt200_gr` installs `nv50_gr_init`, `nv50_gr_intr`, `nv50_gr_chan_new`, `g84_gr_tlb_flush`, and `nv50_gr_units`.
- Class table exposes null, NV50 2D, M2MF, compute, and `GT200_TESLA`.
- `gt200_gr_new()` constructs through `nv50_gr_new_()`.

## Control flow
The file has no custom runtime function beyond construction. Runtime GR behavior comes from `nv50` common code and `g84_gr_tlb_flush()` when MMU invalidation needs a PGRAPH flush.

## State and persistence
No local mutable state. Engine state is the `nv50_gr` object built by `nv50_gr_new_()`.

## Dependencies and integration points
Depends on `nv50.h`, `g84_gr_tlb_flush()`, and NVIF class IDs. Device tables use `gt200_gr_new()` for GT200-family GPUs.

## Risks
The only chip-specific behavior here is class selection. Wrong class exposure can break userspace channel creation. TLB flush behavior inherits all G84 risks.

## Test signals
Successful GT200 probe, expected `GT200_TESLA` class availability, correct NV50 channel creation, and no TLB flush timeout under VM invalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gt200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gt215.c

## Purpose
Defines GT215/GT214 Tesla GR support by selecting NV50 common GR behavior, G84 TLB flushing, and GT214 graphics/compute class IDs.

## Important APIs, types, and functions
- `gt215_gr` installs NV50 init, interrupt, channel, units, and G84 TLB flush hooks.
- Class table exposes null, NV50 2D, M2MF, NV50 compute, `GT214_TESLA`, and `GT214_COMPUTE`.
- `gt215_gr_new()` constructs through `nv50_gr_new_()`.

## Control flow
All runtime control flow is inherited from `nv50_gr` and `g84_gr_tlb_flush()`. This file only selects the right function table at construction.

## State and persistence
No local mutable state. Long-lived state is the inherited `nv50_gr` engine object.

## Dependencies and integration points
Depends on `nv50.h`, `g84_gr_tlb_flush()`, and NVIF class definitions. It is a device-table integration file for GT215-family chips.

## Risks
Incorrect class table entries can expose unsupported classes or hide supported compute functionality. Flush behavior inherits G84 idle-detection risk.

## Test signals
Expected `GT214_TESLA` and `GT214_COMPUTE` class enumeration, successful NV50 channel operation, and no PGRAPH TLB flush timeouts under memory-management stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gv100.c

## Purpose
Implements GV100 Volta GR support by extending Pascal/Maxwell common hooks with Volta SM trap handling, SM ordering, shader exception programming, TPC numbering helpers, and Volta class/firmware interfaces.

## Important APIs, types, and functions
- `gv100_gr_trap_sm()` and `gv100_gr_trap_mp()` decode two SM trap banks per TPC.
- `gv100_gr_init_shader_exceptions()`, `gv100_gr_init_504430()`, `gv100_gr_init_419bd8()`, and `gv100_gr_init_4188a4()` program Volta-specific registers.
- `gv100_gr_nonpes_aware_tpc()` maps PES-aware TPC indexes to non-PES-aware order.
- `gv100_gr_scg_estimate_perf()` and `gv100_gr_oneinit_sm_id()` build an SM order by iteratively removing the TPC that maximizes a performance heuristic.
- `gv100_gr_new()` uses `gm200_gr_load()` with GP108 v2 ACR descriptors.

## Control flow
`oneinit` discovers topology, then `gv100_gr_oneinit_sm_id()` builds SM ordering from PPC/TPC masks. Init uses common GF100 flow with GM200 tiles/MMU/LTC, GP102 PES/ZBC, GP100 FECS, Volta shader exception and trap hooks, and signed firmware. Trap handling reads and clears Volta's per-SM trap registers.

## State and persistence
The computed `gr->sm[]` order and `sm_nr` are persistent for the engine lifetime. Function-table limits specify six GPCs, seven TPCs, and three PPCs. Firmware-derived packs and ZBC state are common GF100 state.

## Dependencies and integration points
Depends on GF100 common code, GM200 firmware loading and tile hooks, GP100/GP102 helpers, GP108 ACR descriptors, GV100 context data, and Volta class IDs.

## Risks
The SM ordering heuristic is complex and allocation-sensitive. It has safety checks for duplicate TPC removal and invalid performance values. Volta has two SM trap banks per TPC; incomplete handling can leave errors uncleared. Firmware is mandatory.

## Test signals
Signals include successful GV100 signed firmware load, correct SM ordering count, no allocation failure in oneinit, useful `SM0/SM1 trap` logs, working `VOLTA_A` and compute classes, and stable compute-heavy workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/gv100.c -->
