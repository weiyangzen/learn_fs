# subset-b-003668 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl902d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl902d.h

Purpose: `cl902d.h` is a generated-style hardware ABI header for the Fermi 2D class (`NV902D`). It exposes method offsets, bitfield ranges, and legal enum values used when Nouveau builds pushbuffer methods for the legacy 2D engine. There are no C functions or runtime data structures; the API surface is the `NV902D_*` macro namespace.

Important APIs and types: the header starts with object binding (`NV902D_SET_OBJECT`) and idle synchronization (`NV902D_WAIT_FOR_IDLE`). It then defines destination and source surface programming methods: format, memory layout, pitch, dimensions, and 40-bit-ish split offsets through `*_OFFSET_UPPER` and `*_OFFSET_LOWER`. Supported formats span common ARGB/XRGB layouts, 16-bit RGB, luminance/Y formats, floating-point formats, normalized formats, and packed color encodings. Drawing support includes clip enable, ROP selection, blend/ROP/source-copy operations, monochrome pattern format/color format, solid primitive modes and colors, point coordinate arrays, CPU-sourced pixel upload state, and memory-to-memory scaled blit state.

Control flow: callers program stateful methods in pushbuffer order: bind object, set destination and source surfaces, configure operation/ROP/blend state, then issue either solid primitive point/rectangle data, CPU pixel data, or pixels-from-memory coordinates. The header itself has no control flow, but its offsets encode the required hardware sequencing.

State and persistence: all state persists in the GPU channel/subchannel object until overwritten or the channel is reset. Source/destination offsets reference memory objects previously mapped into the GPU address space. Pixel upload data written to `NV902D_PIXELS_FROM_CPU_DATA` is consumed as method payload, not stored by the header.

Dependencies and integration: this file depends only on the C preprocessor. It is indirectly tied to Nouveau push helpers such as `PUSH_MTHD`, `PUSH_IMMD`, `NVVAL`, and `NVDEF`, and `include/nvif/push906f.h` reserves a `PUSH906F_SUBC_NV902D` subchannel for this class. In this tree, direct use of `NV902D_*` methods is not visible outside the header/subchannel definition, so the file mainly preserves ABI completeness for clients that may bind Fermi 2D.

Risks: method values are hardware ABI constants; changing an offset, field width, or enum value can hang the graphics channel or corrupt framebuffer memory. The offset split, pitch units, blocklinear versus pitch layout bit, and format enums must match the firmware/kernel object class exactly. The repeated `PITCH` field use pattern seen in nearby display code is not present here, so users must be careful to encode pitch and block dimensions according to this class, not a display class.

Test signals: build coverage should catch missing macro names when code includes the header. Runtime signals are successful 2D blits/fills, no channel exception interrupts, and correct framebuffer contents after source-copy, ROP, blend, CPU upload, and scaled memory blit paths. Useful targeted tests include using several RGB/Y/float formats, both pitch and blocklinear surfaces, overlap-safe memory copies, and clipping/ROP combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl902d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl9039.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl9039.h

Purpose: `cl9039.h` defines the Fermi memory-to-memory format class (`NV9039`) used for DMA-style buffer moves. It is a pure macro ABI header: no functions, structs, or persisted software state are declared.

Important APIs and types: `NV9039_SET_OBJECT` binds the class object. Copy state is described by output offset upper/lower, input offset upper/lower, input/output pitch, line length, line count, and `NV9039_LAUNCH_DMA`. The launch method exposes source inline mode, source/destination memory layout, completion behavior (`FLUSH_DISABLE`, `FLUSH_ONLY`, `RELEASE_SEMAPHORE`), interrupt behavior, and one-word/four-word semaphore structure size.

Control flow: Nouveau's `nouveau_bo9039.c` uses these macros in `nvc0_bo_move_m2mf()`. It chunks a TTM buffer move into up to 2047 pages per launch, emits destination and source offsets, pitch and line geometry, then writes `LAUNCH_DMA`. `nvc0_bo_move_init()` binds the object with `SET_OBJECT`. The header therefore participates in a tight loop that advances source and destination GPU virtual offsets after each hardware copy.

State and persistence: the class object keeps the programmed offsets and geometry for the channel until the next method write. The move helper does not persist software state in this header, but the GPU copy affects destination buffer contents and depends on valid Nouveau memory/vma mappings for old and new TTM resources.

Dependencies and integration: direct integration points are `nouveau_bo9039.c`, `nouveau_dma.h`, `nouveau_mem.h`, and `include/nvif/push906f.h`, which provides pushbuffer packing and subchannel assignments. The header also relies on field helpers (`NVVAL`, `NVDEF`) interpreting the `field high:low` macros consistently.

Risks: incorrect launch flags can copy with the wrong memory layout, fail to flush, or signal incorrectly. Offset upper fields are only eight bits, so callers must pass addresses in the hardware-supported aperture format. Page-count chunking in the caller protects line-count limits; bypassing that pattern risks oversized launches. Because this class performs memory movement, bad offsets or pitch values can corrupt unrelated GPU memory.

Test signals: compile-time inclusion by `nouveau_bo9039.c` verifies macro names. Runtime testing should exercise TTM migration between VRAM/GART placements, large moves crossing the 2047-page chunk boundary, non-zero high address bits, and failure-free pushbuffer submission. Correctness signals are byte-identical destination buffers, no PGRAPH/channel faults, and no stale data after completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl9039.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl906f.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl906f.h

Purpose: `cl906f.h` defines Fermi channel-control methods and DMA method packet fields for the `NV906F` class. It is the low-level ABI surface for semaphore-based fencing, non-stall interrupts, reference values, and pushbuffer packet encoding.

Important APIs and types: semaphore programming is split across `SEMAPHOREA` (upper offset), `SEMAPHOREB` (lower offset), `SEMAPHOREC` (payload), and `SEMAPHORED` (operation and flags). Supported operations include acquire, release, acquire-greater-or-equal, and acquire-and. `SEMAPHORED` also controls acquire context switching, release wait-for-idle, and 16-byte versus 4-byte release size. `NV906F_NON_STALL_INTERRUPT` and `NV906F_SET_REFERENCE` expose interrupt/reference methods. The DMA packet macros describe method address, subdevice mask, subchannel, tertiary/secondary opcodes, counts, and immediate data.

Control flow: `nvc0_fence.c` uses the semaphore macros in `nvc0_fence_emit32()` and `nvc0_fence_sync32()`. The emit path writes a semaphore address and payload, then releases with WFI enabled and a 16-byte release size. The sync path writes the target address/payload and emits an acquire-greater-or-equal with acquire switching enabled. `include/nvif/chan906f.c` and `push906f.h` use the DMA format definitions for channel push encoding.

State and persistence: semaphore methods cause the GPU to read or write memory-backed fence locations. The release persists the sequence value in mapped memory; acquire waits until the memory value satisfies the condition. Packet format constants shape pushbuffer contents but do not store state themselves.

Dependencies and integration: this header integrates with Nouveau fence management, nvif channel helpers, pushbuffer macros, and GPU channel scheduling. It is generation-specific; later `NVC36F` semaphore methods differ in method layout and 64-bit payload support.

Risks: semaphore address alignment is encoded by `SEMAPHOREB_OFFSET_LOWER 31:2`; incorrect low bits or release size can break fence memory layout. Enabling/disabling WFI changes ordering guarantees. Mistakes in DMA packet fields can make an entire pushbuffer decode incorrectly, causing channel exceptions rather than a local failure.

Test signals: successful fence emit/sync on NVC0-class hardware is the primary signal. Tests should verify monotonic fence sequence release, waits across channels, non-stall interrupt delivery where used, and no timeouts under GPU load. Packet encoding regressions normally appear as immediate channel faults, failed submissions, or fences that never signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl906f.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907c.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907c.h

Purpose: `cl907c.h` describes the `NV907C` display base channel class. It provides method offsets and field values used to present scanout surfaces, set LUTs, and program base-channel color conversion on Fermi-era display hardware.

Important APIs and types: present control supports non-tearing, immediate, on-line, and at-frame begin modes plus timestamp enable, min present interval, begin line, and line margin. Surface methods set ISO context DMAs, base/output LUT addresses and modes, LUT DMA handles, CSC matrix coefficients, per-surface offsets, size, storage (block height, pitch, layout), and params (format, supersampling, gamma, layout).

Control flow: `dispnv50/base907c.c` uses these constants for base image updates. It emits present control, ISO handle, surface offset/size/storage/format, and LUT/CSC state via `PUSH_MTHD`. LUT helper paths choose 257-entry or 1025-entry interpolate modes and enable/disable base or output LUT ownership. CSC helper paths either return ownership to core or write a 3x4 coefficient matrix owned by base.

State and persistence: base-channel state is latched by display update semantics and persists across frames until replaced. Surface offsets refer to DRM framebuffer memory, LUT methods refer to GPU-visible LUT buffers, and CSC coefficients persist in display hardware state for that base channel.

Dependencies and integration: the header is included by `dispnv50/base907c.c` and depends on the display atomic state machinery (`asyw->image`, `asyw->xlut`, `asyw->csc`) to provide valid values. It integrates with `nvif` push helpers and Nouveau's display interlock/update pipeline.

Risks: present mode and interval mistakes can cause tearing or missed vblank scheduling. Incorrect format/layout/pitch encoding can scan out corrupt pixels or trigger display underflow. LUT ownership fields (`USE_CORE_LUT`, `ENABLE`, `DISABLE`) must match how core and base channels share color state. CSC owner bit is important; writing coefficients under the wrong owner can leave stale color conversion active.

Test signals: DRM atomic modesets, page flips, gamma/LUT updates, and color-management tests should cover this class. Visible signals include correct framebuffer scanout, no underflow messages, stable vblank/page-flip completion, correct gamma ramp behavior for 257 and 1025 LUTs, and correct CSC effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907d.h

Purpose: `cl907d.h` is the main `NV907D` display core class ABI header. It defines notifier capability fields and core-channel methods for output ownership, head timing, CRC, LUT, cursor, dither, scaler, procamp, viewport, and base/overlay usage bounds.

Important APIs and types: the capability notifier exposes SOR0 LVDS/TMDS/DP capabilities and DP interlace support. Output methods include DAC and SOR owner masks and protocols. Head methods cover output resource control, progressive/interlaced structure, overscan/default colors, raster timing, CRC buffer/control, output LUT, pixel clock frequency/configuration/max, surface offset/size/storage/params, ISO DMA handles, cursor control and offset/context, dithering, output scaler taps, procamp color space/range/saturation, viewport in/out bounds, and base/overlay channel usage bounds.

Control flow: `core907d.c`, `head907d.c`, `sor907d.c`, `dac907d.c`, and `crc907d.c` emit these methods during modeset and atomic commit. The driver assigns heads to SOR/DAC resources, programs raster and pixel-clock state, binds scanout/cursor/LUT/CRC buffers, and uses CRC methods when DRM capture is enabled. `sor907d.c` also reads the notifier capability fields through `NVBO_RV32`.

State and persistence: core display state persists in hardware across flips and is updated through display channel pushes. The header's methods alter persistent output routing, head timing, cursor memory, LUT memory, and CRC notifier state. Notifier memory persists capability/status data for the driver to read.

Dependencies and integration: included by Nouveau connector defaults, display core/head/output/CRC code, and `disp.c` class selection. It integrates with DRM modesetting, Nouveau's display object model, and push helpers. It is the older baseline that later `NV917D`, `NVC37D`, and `NVC57D` variants extend or rearrange.

Risks: many fields are bit-position-sensitive and generation-specific. Incorrect owner masks can route a head to the wrong encoder or leave an encoder unowned. Timing and pixel-clock mistakes can blank displays. Cursor field sizes differ from later classes; copying `NV917D`/`NVC37D` assumptions here can truncate hotspot or size encoding. CRC primary/secondary output encodings are dense and easy to mismatch.

Test signals: external monitor modesets over DAC/TMDS/LVDS/DP, cursor movement and format tests, gamma/dither/scaler changes, page-flip stability, and DRM CRC capture are the strongest signals. Regression indicators include blank displays, wrong connector ownership, underflow, invalid CRC reads, cursor corruption, or modeset timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907e.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907e.h

Purpose: `cl907e.h` defines the `NV907E` overlay channel class. It exposes methods for overlay presentation, surface configuration, and simple composition/color-space selection on Fermi-era display hardware.

Important APIs and types: present control supports ASAP or timestamp begin modes and minimum present interval. The class has a single ISO DMA handle, composition control modes for source keying, destination keying, or opaque composition, and surface methods for offset, size, storage, format, and RGB/YUV color space. Formats include packed YUV, 10-bit RGB variants, ARGB, A1R5G5B5, and 16-bit floating/integer RGBA layouts.

Control flow: `dispnv50/ovly907e.c` programs overlay state by emitting present control, ISO context, opaque composition, surface offset, surface size, storage, and params. It uses atomic async window state (`asyw->image`) for interval, handle, offset, dimensions, block height, pitch/block count, layout, format, and colorspace.

State and persistence: overlay surface and composition state persists in the overlay channel until disabled or replaced. The configured ISO handle and offset point at scanout-capable framebuffer memory. Present control determines when the hardware applies the pending state.

Dependencies and integration: direct integration is `ovly907e.c`, with Nouveau display window abstractions providing the validated image state. The header relies on push macros for method emission and on DRM atomic plane validation to reject unsupported formats or dimensions before hardware programming.

Risks: the storage pitch field is also used by caller code for block counts depending on layout, so unit mismatches can create invalid scanout. Incorrect color-space selection can produce wrong YUV conversion. Overlay begin-mode differences from base/window classes matter; copying `NV907C` or `NVC37E` present bits directly would encode the wrong values.

Test signals: overlay-plane enable/disable, packed YUV and RGB plane scanout, vblank-synchronized flips, and plane format validation are key. Visual corruption, color-range errors, underflow, or page-flip events firing at unexpected times indicate misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl907e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl917d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl917d.h

Purpose: `cl917d.h` is a compact `NV917D` display core variant header. It keeps SOR control compatible with `NV907D` while adding wider cursor size/hotspot support and LUT usage-bound fields for later Fermi/Kepler display behavior.

Important APIs and types: SOR control defines owner masks for heads 0-3 and protocols for LVDS, single/dual TMDS, DP A/B, and custom modes. Cursor control supports A1R5G5B5 and A8R8G8B8 formats, 32/64/128/256 square cursors, 8-bit hotspot coordinates, and alpha/premultiplied/XOR composition. Dither control mirrors the older class. Base-channel usage bounds add base/output LUT usage fields for none, 257-entry, and 1025-entry LUTs.

Control flow: `head917d.c` emits the dither and cursor-related methods for heads on this class generation, while `disp.c` selects display class implementations. The flow remains display atomic commit driven: validate desired state, emit methods for the affected head/output, and update the display channel.

State and persistence: SOR ownership, cursor context/offset/control, dither settings, and base-channel bounds persist in display hardware until changed. Cursor memory context and offsets reference GPU-visible cursor images.

Dependencies and integration: included by `dispnv50/head917d.c` and `disp.c`. It is tightly coupled with `NV907D` conventions but not identical; the cursor size and hotspot fields are expanded compared with `NV907D`.

Risks: using `NV907D` cursor field widths on `NV917D` would mishandle 128/256 cursor sizes or larger hotspots. LUT usage bounds affect whether base/output LUT resources are reserved for a head, so incorrect values can break color management or resource validation. SOR protocol constants must match actual encoder capabilities.

Test signals: large hardware cursor tests, cursor hotspot tests, dither mode changes, SOR-driven modesets, and color-management paths that need 257/1025 LUT usage should cover this header. Failures show as cursor clipping/misalignment, blank links, or LUT programming rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cl917d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cla0b5.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cla0b5.h

Purpose: `cla0b5.h` defines the `NVA0B5` copy engine/memory-to-memory class used by newer Nouveau buffer moves and device-memory migration. It is a macro-only ABI header for DMA copy launch, physical/virtual aperture selection, line geometry, and component remapping.

Important APIs and types: source/destination physical mode methods select local framebuffer, coherent system memory, or noncoherent system memory. `NVA0B5_LAUNCH_DMA` contains transfer type, flush, semaphore, interrupt, source/destination layout, multiline, remap, L2 bypass, virtual/physical source/destination, and semaphore reduction fields. Offset, pitch, line length, and line count methods describe the copy. Remap constants and `SET_REMAP_COMPONENTS` allow constant fills or component swizzles using source components, constants, or no-write lanes.

Control flow: `nouveau_boa0b5.c` uses the header for BO moves: program offsets/pitches/line geometry and launch a non-pipelined flushed pitch-to-pitch copy. `nouveau_dmem.c` uses it for HMM/device-memory migration, selecting physical source/destination targets, emitting launch flags for physical addressing, and using remap mode for memory clear/fill-style operations.

State and persistence: copy state persists in the copy engine object until overwritten. The durable effect is modified destination memory or migrated page contents. Physical-mode methods affect how subsequent physical addresses are interpreted.

Dependencies and integration: included by `nouveau_boa0b5.c` and `nouveau_dmem.c`; it depends on Nouveau memory management, HMM migration paths, channel push helpers, and kernel address helpers such as `upper_32_bits`/`lower_32_bits`.

Risks: mixing virtual and physical address flags with the wrong address source can corrupt memory or fault the engine. Coherent versus noncoherent sysmem target selection affects CPU/GPU visibility. Remap component fields are compact and can turn a copy into a fill/no-write unexpectedly. Launch flag semantics differ substantially from older `NV9039`, so shared copy helpers must not assume compatible bit positions.

Test signals: BO migration tests, VRAM-to-sysmem and sysmem-to-VRAM dmem migrations, high-address copies, large multi-line transfers, and dmem clear/remap paths. Correctness signals include byte-accurate migrated pages, no copy engine faults, no cache-coherency stale reads, and successful memory-pressure migration loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/cla0b5.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc36f.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc36f.h

Purpose: `clc36f.h` defines the `NVC36F` channel-control class used on GV100-class hardware for non-stall interrupts, memory operations, TLB invalidation/replay cancel, access-counter clearing, and modern semaphore execution.

Important APIs and types: `MEM_OP_A` and `MEM_OP_B` carry targeted TLB invalidation address and replay-cancel target fields. `MEM_OP_C` carries membar type, PDB selection, GPC enable, replay action, ack type, access type or page-table level, PDB aperture/address, and access-counter notify tag fields. `MEM_OP_D` selects the operation: membar, MMU TLB invalidate, targeted invalidate, L2 peer/sysmem invalidate, comptag clean, dirty flush, wait for sys pending reads, or access-counter clear. Semaphore methods use low/high address, low/high payload, and `SEM_EXECUTE` for acquire/release/reduction, TSG switching, WFI, 32/64-bit payload, timestamp, and reduction format.

Control flow: `gv100_fence.c` emits semaphore releases/acquires using `SEM_ADDR_*`, `SEM_PAYLOAD_LO`, and `SEM_EXECUTE`. The fence emit path follows release with a system membar via `MEM_OP_A` through `MEM_OP_D`, then emits `NON_STALL_INTERRUPT`. `nvif/chanc36f.c` uses the memory operation fields for channel-level memory barriers and invalidations.

State and persistence: semaphore release persists fence payloads in memory; acquire waits on persisted memory values. MEM_OP methods cause ordering/cache/MMU side effects rather than persistent software state. TLB and L2 invalidation state affects subsequent GPU memory translations and cache visibility.

Dependencies and integration: included by `gv100_fence.c` and `nvif/chanc36f.c`, with push helpers and Nouveau fence/channel abstractions. It supersedes older `NV906F` semaphore layout for newer GPUs.

Risks: comments explicitly note `MEM_OP_A/B` changed in GP100 and old functionality moved to `MEM_OP_C/D`; mixing generations can produce invalid TLB operations. Targeted invalidation fields are overloaded depending on replay mode, PDB mode, and access type. Missing the required A-C writes before `MEM_OP_D` can make operations use stale operands. Incorrect semaphore payload size or WFI flag can break fence ordering.

Test signals: GV100+ fence emit/sync, channel memory barrier tests, UVM/HMM invalidation paths, replay-cancel scenarios, and access-counter clearing. Runtime regressions include stalled fences, stale page translations, replay storms, non-stall interrupt failures, or GPU faults during memory migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc36f.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37a.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37a.h

Purpose: `clc37a.h` defines the `NVC37A` cursor immediate/display cursor channel methods. It is a very small ABI header for cursor update submission and output hotspot programming.

Important APIs and types: `NVC37A_UPDATE` triggers the cursor channel update. `NVC37A_SET_CURSOR_HOT_SPOT_POINT_OUT(b)` is an indexed method that packs X in bits 15:0 and Y in bits 31:16. The header contains no structs or functions.

Control flow: `dispnv50/cursc37a.c` includes this header and emits hotspot/update methods during cursor atomic updates. The expected sequence is to program one or more hotspot output points and then issue `UPDATE`, coordinated with the core/window display update path as needed.

State and persistence: hotspot coordinates persist in the cursor channel until changed. The cursor image memory and enable state are controlled by related core/head methods in `NVC37D`/`NVC57D`-style headers, while this file handles the immediate cursor-position-style update surface.

Dependencies and integration: direct dependencies are Nouveau display cursor code and pushbuffer helpers. It complements `NVC37D_HEAD_SET_CONTROL_CURSOR` and related cursor context/offset methods, rather than replacing them.

Risks: this class uses 16-bit X/Y packing, unlike older core cursor control fields that pack smaller hotspot values. Incorrect index `b` or missed `UPDATE` can leave stale cursor position/hotspot state. Because cursor moves are latency-sensitive, interlock mistakes can show up as cursor tearing or lag.

Test signals: hardware cursor movement, hotspot correctness at screen edges, multi-head cursor placement, and rapid cursor updates. A good runtime signal is cursor movement without full modeset and without visible flicker or coordinate truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37b.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37b.h

Purpose: `clc37b.h` defines the `NVC37B` window-immediate class and its simple DMA packet format. It supports immediate point/output updates and optional interlock with regular window state.

Important APIs and types: the DMA packet macros define opcode, method count, method offset, data, jump offset, and subdevice mask fields for method, jump, non-incrementing method, and set-subdevice-mask commands. Class methods include `NVC37B_UPDATE` with `INTERLOCK_WITH_WINDOW` and indexed `NVC37B_SET_POINT_OUT(b)` packing X/Y coordinates.

Control flow: `dispnv50/wimmc37b.c` includes this header for window immediate commits. The driver programs output point coordinates, optionally asks update to interlock with the normal window channel, then emits update to apply the immediate state without a full core modeset.

State and persistence: point-out coordinates persist in the immediate window channel until replaced. DMA opcode definitions affect pushbuffer decoding but hold no state. Interlock state is per update and coordinates with other display channel updates.

Dependencies and integration: included by `wimmc37b.c` and `include/nvif/pushc37b.h`. It fits into Nouveau's Volta/Turing display split where window immediate state is separate from core, cursor, and regular window channels.

Risks: DMA packet field widths differ from `NV906F`; using the wrong packet encoder would corrupt display channel command parsing. Interlock misuse can apply immediate window changes out of sync with regular window updates. Coordinate packing must stay within 16-bit X/Y ranges.

Test signals: atomic plane position changes that use the window-immediate path, especially with and without interlock. Visual signals include tear-free plane movement, no stale coordinates after update, and no display channel exceptions from malformed DMA methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37d.h

Purpose: `clc37d.h` defines the `NVC37D` display core class for newer display hardware. It describes notifier layout, core update/interlock methods, SOR control, window resource usage bounds, and head-level procamp, timing, cursor, LUT, and CRC methods.

Important APIs and types: `NV_DISP_NOTIFIER` describes present status, count, field, flip type, and timestamps. `NVC37D_UPDATE` includes special handling, reason, and interrupt inhibition. Notifier control sets DMA handle, offset, awaken/write mode, and notify enable. Interlock methods cover cursor, core, and up to 32 windows. SOR control supports owner masks for heads 0-7 and DSI in addition to LVDS/TMDS/DP. Window usage bounds define supported RGB/YUV format families, rotated format support, max pixels fetched per line, input LUT use, scaler taps, and upscaling. Head methods cover procamp with BT.2020 and black-level controls, output resource controls with color-space override, pixel clocks, dither up to 12 bits, head usage bounds, viewport/raster timing, cursor context/offset/control/composition, output LUT control/address/context, and CRC control.

Control flow: `corec37d.c` emits global core/window usage bounds and update/notifier/interlock methods. `headc37d.c` programs head timing, procamp, dither, cursor, viewport, and LUT state. `sorc37d.c` sets SOR routing. `crcc37d.c` programs CRC context/control using the compact primary/secondary CRC selector fields.

State and persistence: core/head/window bounds and routing persist in display hardware across atomic commits. Notifier memory persists present completion state and timestamps. Interlock flags control synchronization of updates across display channels.

Dependencies and integration: included by the Volta/Turing display implementation files under `dispnv50/`. It integrates with DRM atomic state, Nouveau's display channel abstractions, DMA notifier buffers, and `NVDEF`/`NVVAL` push helpers.

Risks: this class changes many field offsets from `NV907D`, especially head base offsets, cursor format encoding, CRC selectors, and dither bits. Incorrect interlock flags can cause partially applied multi-plane updates. Window format-usage bounds gate what later window channels are allowed to scan out; overly broad or narrow bounds can create validation/hardware mismatches.

Test signals: multi-head modesets, window/plane format validation including YUV families, cursor sizes and composition, LUT/color management, DP/DSI/TMDS routing, display CRC capture, and atomic commits involving several windows with interlocks. Failures appear as atomic check/commit mismatches, underflow, wrong color, failed CRC setup, or display channel errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37e.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37e.h

Purpose: `clc37e.h` defines the `NVC37E` window channel class. It is the main plane/window programming ABI for newer display generations, covering semaphores, notifiers, surface memory, color processing, composition, keying, presentation, and interlocks.

Important APIs and types: update supports interlock with window-immediate state. Semaphore control/acquire/release/context methods allow display synchronization. Notifier context/control handles completion writes. Surface methods set size, storage, params, planar storage, ISO DMA contexts, offsets, input/output rectangles, input LUT control/address/context, CSC matrix, composition control, constant alpha, factor selection, color key ranges, present control, cursor/core/window interlock flags, and many RGB/YUV formats from 8-bit to 12-bit planar and semi-planar layouts.

Control flow: `dispnv50/wndwc37e.c` uses this header extensively. It emits CSC matrices, disables or programs input LUTs, programs blending and color key defaults, configures present mode/interval, writes surface size/storage/params/planar pitch/handles/offsets, sets source and destination rectangles, manages notifier and semaphore methods, then emits interlock flags and `UPDATE`.

State and persistence: window channel state persists across commits until updated. Notifier and semaphore methods write/read memory-backed synchronization objects. Surface offsets and contexts reference framebuffer planes. LUT/CSC/composition state persists and affects all subsequent scans from that window.

Dependencies and integration: direct integration is `wndwc37e.c` plus generic `dispnv50/wndw.c`. It depends on DRM plane state validation, Nouveau image/color/blend structs, push helpers, display interlock constants, and GPU-visible notifier/semaphore buffers.

Risks: this is a high-blast-radius header because it controls visible plane content. Format/color-space/input-range/degamma/CSC bits must match the DRM format modifier and color pipeline. Planar pitch and offset indexing must match the number of planes. Blend factor selection is dense and easy to encode incorrectly. Semaphore and notifier offset fields have limited ranges, so invalid offsets can silently target the wrong slot.

Test signals: plane scanout for RGB and YUV packed/planar/semi-planar formats, scaling, input LUT, CSC, alpha blending, color key disabled/enabled behavior, semaphores/notifiers, and atomic commits synchronized with window-immediate/cursor/core interlocks. Visible corruption, wrong color range, stuck page flips, or broken async update ordering are key regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57d.h

Purpose: `clc57d.h` defines the `NVC57D` display core class variant for a later generation than `NVC37D`. It preserves many core/window/head concepts while adding updated LUT capability fields, output resource extended-packet window selection, pixel-clock configuration, and OLUT programming.

Important APIs and types: the header defines notifier DMA context, window format and rotated-format usage bounds, window usage bounds with ILUT and TMO LUT allowance, scaler taps, and upscaling. Head methods cover procamp color space/range, output resource control including color-space override and `EXT_PACKET_WIN`, pixel clock frequency/configuration/max, head usage bounds with cursor, OLUT allowed, output scaler taps, and upscaling, raster timing, CRC context/control with explicit window/core controlling-channel values, and OLUT control/scale/context/offset.

Control flow: `corec57d.c` initializes context DMA notifier, window format usage bounds, and window usage bounds for each window using these macros. `headc57d.c` programs head timing, procamp, clocking, usage bounds, and OLUT state. `crcc57d.c` programs CRC control using the `NVC57D` selector fields.

State and persistence: programmed window/head/core bounds persist in display hardware. OLUT context/offset/control state persists per head. CRC context points at notifier memory, and output resource fields determine active head/output behavior.

Dependencies and integration: included by `corec57d.c`, `headc57d.c`, and `crcc57d.c`. It sits in the same Nouveau display stack as `NVC37D` but is not bit-compatible in all fields, so generation-specific files keep the use separated.

Risks: this class changes resource capability names and meanings: `ILUT_ALLOWED` replaces older input-LUT usage enum style, `TMO_LUT_ALLOWED` appears in window bounds, and `OLUT_ALLOWED`/OLUT control use a newer model. Output resource `EXT_PACKET_WIN` must match the window that supplies extension packets or be `NONE`. CRC controlling channel values include many window IDs plus core, so wrong values can capture the wrong stream.

Test signals: modesets on C57D-class hardware, window initialization for all windows, HDR/TMO or LUT-capability paths where supported, OLUT programming, pixel-clock hopping/configuration, and DRM CRC capture. Regressions show as unsupported-plane validation mismatch, absent LUT effects, wrong CRC source, bad output packets, or display underflow/blanking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57d.h -->
