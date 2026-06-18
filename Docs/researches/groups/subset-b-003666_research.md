# subset-b-003666 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec57d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec57d.c

### Purpose
`corec57d.c` defines the GV100/Turing-era display core-channel function table for the C57D core class. It initializes display window usage limits and binds the core channel to the matching head, SOR, notifier, capability, and optional CRC implementations.

### Key APIs And Functions
`corec57d_init()` writes `NVC57D` methods for notifier DMA setup plus per-window format and usage bounds. The exported `corec57d_new()` passes the static `nv50_core_func corec57d` to `core507d_new_()`. The function table reuses C37D notifier/caps/update/window-owner helpers and selects `headc57d`, `sorc37d`, and debugfs `crcc57d`.

### Control Flow And State
Initialization reserves push space, programs all eight windows with packed RGB support, disables rotated formats, sets fetch/scaler restrictions, marks `core->assign_windows`, and kicks the core channel. Persistent state is limited to the core function table choice and the `assign_windows` flag consumed by the atomic commit path.

### Dependencies And Integration
The file depends on Nouveau push macros, `clc57d` register definitions, `core.h`, `head.h`, C37D shared helpers, and NVIF class IDs. It is selected by core-channel class probing and feeds `disp.c` atomic commits through `core->func`.

### Risks And Test Signals
The hard-coded eight-window count and usage bounds are hardware assumptions; wrong bounds can reject otherwise valid plane configurations or permit unsupported ones. Tests should cover initial modeset on GV100/TU-class hardware, window ownership assignment, debugfs CRC availability, and plane format/scaler validation across all advertised windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec57d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/coreca7d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/coreca7d.c

### Purpose
`coreca7d.c` defines the GB202/Blackwell display core-channel implementation. It adapts the C37D/C57D core model to newer `NVCA7D` methods that use physical notifier/surface addresses rather than legacy CTXDMA handles.

### Key APIs And Functions
`coreca7d_update()` optionally programs the core notifier physical address, emits cursor/window interlock flags, issues `UPDATE`, and disables notifier writes afterward. `coreca7d_init()` programs window usage bounds, physical window assignment, head usage bounds, per-head tile masks, and tile sizes. `coreca7d_new()` installs the `coreca7d` function table with `headca7d`, `sorc37d`, `crcca7d`, and `GB202_DISP_CAPS`.

### Control Flow And State
On init, eight windows and four heads are configured before `assign_windows` is set. On update, the notifier offset is derived from the display sync BO, split into high/low physical fields, and used only when the caller requests notification. State persists in `core->assign_windows` and in the active hardware core channel.

### Dependencies And Integration
The file depends on `pushc97b`, `clca7d`, `nouveau_bo`, NVIF class IDs, and the shared core/head abstractions. It is the core-channel endpoint used by `disp.c` for Blackwell atomic commits, CRC context programming, and notifier completion.

### Risks And Test Signals
The switch away from CTXDMA handles makes address alignment and target selection critical. Tests should include core updates with and without notification, suspend/resume reinitialization, window/head assignment on all heads, and CRC plus plane commits on GB202-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/coreca7d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.c

### Purpose
`crc.c` implements DRM debugfs CRC capture for NV50+ display heads when `CONFIG_DEBUG_FS` is enabled. It validates CRC source strings, allocates notifier memory, programs CRC source/context state during atomic commits, drains hardware CRC entries on vblank, and exposes a per-head debugfs flip-threshold control.

### Key APIs And Functions
Public entry points include `nv50_crc_verify_source()`, `nv50_crc_get_sources()`, `nv50_crc_set_source()`, `nv50_crc_handle_vblank()`, the atomic helpers `nv50_crc_atomic_*()`, `nv50_head_crc_late_register()`, and `nv50_crc_init()`. Internal helpers parse source names, map output encoders to CRC source types, initialize/free notifier contexts, wait for context completion, flip double-buffered notifier contexts, and read entries through `nv50_crc_func` callbacks.

### Control Flow And State
CRC capture is started through `set_crc_source`, which builds an atomic state, allocates two VRAM notifier contexts per head, sets `asyh->crc.src`, and commits. The atomic tail stops old reporting, initializes contexts, programs the new source, starts vblank reporting, and later releases contexts. During vblank, `nv50_crc_handle_vblank()` uses a spinlock, checks whether a context flip finished, drains nonzero entries into `drm_crtc_add_crc_entry()`, advances frame and entry counters, resets old contexts, and schedules the next flip via `drm_vblank_work`.

### Dependencies And Integration
The code depends on DRM CRTC CRC hooks, atomic state helpers, `drm_vblank_work`, NVIF memory/object/timer APIs, Nouveau core/head/window/output objects, `handles.h`, and generation-specific CRC function tables from `crc907d.c`, `crcc37d.c`, `crcc57d.c`, and `crcca7d.c`. It integrates with `head.c` vblank handling and with `disp.c` atomic sequencing to avoid CRC disable conflicts with output-resource reprogramming.

### Risks And Test Signals
Races around vblank timing, context flips, display mutex contention, and notifier lifetime are the main risks. The code intentionally accounts for one lost CRC frame on context flips. Tests should cover all source names, enable/disable/re-enable cycles, output modesets while CRC is active, busy flip-threshold writes, notifier overflow logging, suspend/resume, and debugfs-disabled builds where the header stubs must compile out the feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.h

### Purpose
`crc.h` declares the NV50 display CRC abstraction and provides no-op stubs when debugfs support is disabled. It is the contract between the generic CRC state machine in `crc.c`, head atomic state, and generation-specific hardware implementations.

### Key APIs And Types
The enabled path defines `enum nv50_crc_source`, `enum nv50_crc_source_type`, `struct nv50_crc_notifier_ctx`, `struct nv50_crc_atom`, `struct nv50_crc_func`, and `struct nv50_crc`. `nv50_crc_func` supplies `set_src`, `set_ctx`, `get_entry`, `ctx_finished`, `flip_threshold`, `num_entries`, and `notifier_len`. The header declares source validation, source listing, source setting, atomic lifecycle helpers, vblank handling, initialization, and external generation tables.

### Control Flow And State
The header does not execute logic directly, but its structures define persistent per-head CRC state: two notifier contexts, a vblank work item, active source, frame number, entry index, flip threshold, selected context index, and context-changed flag. When debugfs is disabled, matching inline stubs preserve call sites without stateful behavior.

### Dependencies And Integration
It depends on DRM CRTC/vblank work headers, NVIF memory, BIOS/output declarations, and Nouveau encoder/head forward declarations. `head.h` embeds `struct nv50_crc`; `disp.c` and `head.c` call the declared helpers during atomic commits and vblank.

### Risks And Test Signals
Any mismatch between `nv50_crc_func` semantics and generic expectations can corrupt reporting or leak notifier memory. Build tests should cover both `CONFIG_DEBUG_FS=y` and disabled configurations. Runtime tests should validate that each source maps to expected output CRC entries and that per-generation notifier lengths match the hardware layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc907d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc907d.c

### Purpose
`crc907d.c` implements the CRC hardware callback table for the 907D display core class. It programs `NV907D` CRC control methods, binds legacy CTXDMA notifier contexts, reads output CRC entries, and detects notifier completion and overflow.

### Key APIs And Functions
The file defines a packed `crc907d_notifier` with 255 entries and implements `crc907d_set_src()`, `crc907d_set_ctx()`, `crc907d_get_entry()`, and `crc907d_ctx_finished()`. The exported `crc907d` table sets a flip threshold of `CRC907D_MAX_ENTRIES - 10`, `num_entries` to 255, and `notifier_len` to the notifier size.

### Control Flow And State
`set_src` builds `HEAD_SET_CRC_CONTROL` arguments from the generic source type, binds the notifier CTXDMA before enabling CRC, and clears the control before clearing CTXDMA on disable. `get_entry` reads the first output CRC word for an entry. `ctx_finished` waits for the notifier status done bit and logs specific overflow engine names when status bits are set.

### Dependencies And Integration
It depends on `cl907d`, `push507c`, `disp.h`, `core.h`, `head.h`, and the generic CRC abstraction. `crc.c` calls this table for Fermi/Kepler-class heads selected by the core function table.

### Risks And Test Signals
The source switch supports SOR, PIOR, DAC, RG, SF, and none; incorrect OR IDs or source mapping would capture the wrong tap. Tests should exercise all supported output types, notifier overflow paths, context flip timing, and CRC disable ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc907d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.c

### Purpose
`crcc37d.c` implements the Volta-class C37D CRC callback table. It programs `NVC37D` CRC control, reuses a large notifier layout, selects either RG or output CRC data, and reports notifier completion and overflow status.

### Key APIs And Functions
`crcc37d_set_src()` maps generic source types to `PRIMARY_CRC` values for SOR, PIOR, and SF. `crcc37d_set_ctx()` binds or clears the CRC CTXDMA. `crcc37d_get_entry()` returns `rg_crc` for the RG source and `output_crc[0]` otherwise. `crcc37d_ctx_finished()` decodes done and overflow bits. The exported `crcc37d` table uses constants from `crcc37d.h`.

### Control Flow And State
Enable ordering mirrors older classes: set the context DMA, then CRC control. Disable clears CRC control and then the context. The function table itself carries notifier size and entry count; runtime state stays in `struct nv50_crc` from the generic layer.

### Dependencies And Integration
The file depends on `crcc37d.h`, `clc37d`, `pushc37b`, and Nouveau core/head/display helpers. It is selected by C37D-generation core tables and is reused indirectly by later C57D/CA7D files for notifier parsing.

### Risks And Test Signals
Only a subset of generic source types is explicitly mapped; unsupported types fall through to no primary CRC bits. Tests should cover RG vs output source entry selection, overflow bit decoding, DP/SOR source capture, context flips near the threshold, and disable behavior during output reprogramming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.h

### Purpose
`crcc37d.h` defines the shared C37D-style CRC notifier layout and helper declarations used by Volta and newer CRC implementations.

### Key APIs And Types
The header defines `CRCC37D_MAX_ENTRIES` as 2047, `CRCC37D_FLIP_THRESHOLD` as 30 entries before the end, and the packed `crcc37d_notifier` containing a status word, reserved padding, and `crcc37d_entry` records with status, compositor, RG, and output CRC fields. It declares `crcc37d_set_ctx()`, `crcc37d_get_entry()`, and `crcc37d_ctx_finished()`.

### Control Flow And State
The header contains no control flow. Its layout is the persistent memory contract between hardware-written VRAM notifier contexts and `crc.c` readers. The threshold constant controls when the generic double-buffer flip work schedules the next notifier context.

### Dependencies And Integration
It includes Linux integer types and `crc.h`, and is included by `crcc37d.c`, `crcc57d.c`, and `crcca7d.c`.

### Risks And Test Signals
Packed layout accuracy is critical because entries are read with MMIO helpers from mapped VRAM. Tests should validate notifier length against hardware expectations, capture at high refresh rates near 2047 entries, and ensure newer classes that reuse the layout still write compatible fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc57d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc57d.c

### Purpose
`crcc57d.c` provides the C57D CRC source-programming callback while reusing the C37D notifier format and reader/completion helpers.

### Key APIs And Functions
`crcc57d_set_src()` builds `NVC57D_HEAD_SET_CRC_CONTROL` arguments for SOR and SF sources, binds the notifier context DMA on enable, and clears both control and CTXDMA on disable. The exported `crcc57d` table points `set_ctx`, `get_entry`, and `ctx_finished` to C37D helpers and uses C37D entry count, threshold, and notifier size constants.

### Control Flow And State
The class-specific control path is minimal: reserve push space, optionally write context DMA, then write CRC control. Runtime state is owned by `crc.c`; this file only expresses how the class wants source and context methods encoded.

### Dependencies And Integration
It depends on `crcc37d.h`, `clc57d`, `pushc37b`, and the shared core/display/head interfaces. `corec57d.c` exposes this table when debugfs CRC support is built.

### Risks And Test Signals
PIOR, DAC, and RG source types are not explicitly mapped here, so caller source mapping and hardware support need coverage. Tests should include DP/SOR CRC capture, SF source capture, disable/re-enable, notifier overflow reuse from C37D, and C57D-specific push method validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc57d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcca7d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcca7d.c

### Purpose
`crcca7d.c` implements GB202/Blackwell CRC callbacks. It keeps the C37D notifier record format but replaces legacy context-DMA programming with physical CRC surface-address methods.

### Key APIs And Functions
`crcca7d_set_ctx()` enables or disables the CRC surface address by splitting `ctx->mem.addr` into high and low physical fields. `crcca7d_set_src()` disables CRC and context when no source is requested, otherwise maps SOR/SF source types, programs the context, and writes `HEAD_SET_CRC_CONTROL`. The exported `crcca7d` table reuses C37D entry reading and completion callbacks.

### Control Flow And State
Enabling CRC first programs the physical notifier target as `PHYSICAL_NVM`, then emits CRC control with core as controlling channel. Disabling clears control before disabling the surface. Runtime state is generic CRC state plus the VRAM notifier memory allocated by `crc.c`.

### Dependencies And Integration
The file depends on `clca7d`, `pushc97b`, `crcc37d.h`, and head/core abstractions. `coreca7d.c` wires this table into the GB202 core function table under debugfs.

### Risks And Test Signals
`primary_crc` is assigned only for supported nonzero source types; invalid future source mappings would be risky. Tests should cover Blackwell CRC enable/disable, physical address alignment, SOR and SF captures, source rejection paths, and suspend/resume cleanup of mapped notifier memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcca7d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.c

### Purpose
`curs.c` selects and creates the per-head hardware cursor immediate channel for the active display class.

### Key APIs And Functions
`nv50_curs_new()` defines an ordered class table from GB202/GA102/TU102/GV100 down to NV50, uses `nvif_mclass()` to choose the supported cursor class, and dispatches to `cursc37a_new()`, `curs907a_new()`, or `curs507a_new()`.

### Control Flow And State
The function probes the display object's supported classes, logs an error if none match, and delegates object creation to the generation-specific helper. It does not persist state directly; the returned `nv50_wndw` carries the cursor plane, immediate-channel object, and interlock information.

### Dependencies And Integration
It depends on `curs.h`, `disp.h` through `nv50_disp()`, NVIF class IDs, and Nouveau DRM logging. `head.c` calls this during CRTC/head creation after primary and overlay planes are built.

### Risks And Test Signals
Class ordering determines which implementation newer hardware receives. Tests should cover cursor creation on each supported display family, no-supported-class failure, and integration with `drm_crtc_init_with_planes()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.h

### Purpose
`curs.h` declares cursor immediate-channel constructors and the common helper used by generation wrappers.

### Key APIs And Functions
The header exposes `curs507a_new()`, `curs507a_new_()`, `curs907a_new()`, `cursc37a_new()`, and `nv50_curs_new()`. `curs507a_new_()` accepts a `nv50_wimm_func` table plus interlock data, allowing later generations to reuse the common cursor plane creation while changing immediate-channel methods.

### Control Flow And State
There is no runtime logic in the header. It defines the construction contract that produces an `nv50_wndw` cursor plane with embedded immediate-channel state.

### Dependencies And Integration
It includes `wndw.h` for `nv50_wndw` and `nv50_wimm_func`. `head.c` uses the public constructor through `nv50_curs_new()`.

### Risks And Test Signals
Signature drift here would affect all head creation paths. Build coverage across NV50, 907A, and C37A cursor implementations is the key signal, with runtime checks for cursor interlock masks on different generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs507a.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs507a.c

### Purpose
`curs507a.c` implements the base NV50 cursor plane and immediate-channel behavior. It validates DRM cursor plane state, writes hotspot/update methods, and constructs the hardware cursor channel.

### Key APIs And Functions
`curs507a_space()` waits for immediate-channel FIFO space. `curs507a_update()` and `curs507a_point()` implement `nv50_wimm_func`. `curs507a_acquire()` validates no scaling, square cursor size, no framebuffer offsets, packed pitch, head-specific layout, and format. `curs507a_prepare()` tracks cursor BO handle/offset in head state and requests a core lock when the backing image changes. `curs507a_new_()` constructs the cursor plane/object; `curs507a_new()` supplies NV50 interlock data.

### Control Flow And State
Atomic acquire writes visibility and image metadata into `nv50_head_atom`. Prepare compares the current cursor handle/offset against the new state and sets `asyh->set.curs` as needed. Channel construction maps the NVIF object and stores the immediate function table in `wndw->immd`.

### Dependencies And Integration
The file depends on DRM atomic plane checks, fourcc formats, NVIF timers/channels, `cl507a`, `head.h`, and `core.h`. It integrates with head-specific cursor layout/format callbacks and with `head_flush_set_wndw()`.

### Risks And Test Signals
Cursor restrictions are strict and user-visible. Tests should cover 32/64-size cursors on old hardware, invalid pitch/offset/format, cursor BO changes without position changes, legacy cursor updates, and FIFO timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs507a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs907a.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs907a.c

### Purpose
`curs907a.c` is a small generation wrapper that creates GF110/GK104 cursor immediate channels using the common 507A cursor implementation with a different interlock-bit layout.

### Key APIs And Functions
`curs907a_new()` calls `curs507a_new_(&curs507a, ...)` and passes `0x00000001 << (head * 4)` as the cursor interlock data.

### Control Flow And State
No independent state is introduced. The common constructor creates the DRM cursor plane, NVIF immediate object, and `wndw->immd` state; this wrapper only supplies the generation-specific class and interlock encoding.

### Dependencies And Integration
It depends on `curs.h` and is selected by `nv50_curs_new()` for GF110/GK104 cursor classes.

### Risks And Test Signals
The interlock shift is the only behavior, so regressions would show as cursor updates not synchronizing correctly with core commits on 907A-class hardware. Tests should include cursor movement/image updates during modesets on GF110/GK104.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs907a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/cursc37a.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/cursc37a.c

### Purpose
`cursc37a.c` implements the Volta-and-newer cursor immediate-channel method variants while reusing common cursor plane validation and construction.

### Key APIs And Functions
`cursc37a_update()` writes `NVC37A UPDATE`. `cursc37a_point()` writes indexed hotspot coordinates with `SET_CURSOR_HOT_SPOT_POINT_OUT(0)`. The static `cursc37a` immediate function table is passed to `curs507a_new_()` by `cursc37a_new()`, using `0x00000001 << head` interlock data.

### Control Flow And State
Channel wait precedes every immediate write. All plane validation, image preparation, and object mapping are inherited from `curs507a_new_()`.

### Dependencies And Integration
The file depends on `clc37a`, `atom.h`, and `curs.h`. `curs.c` selects it for GV100/TU102/GA102/GB202 cursor classes; `headc37d`, `headc57d`, and `headca7d` provide the matching head-side cursor programming.

### Risks And Test Signals
The class uses different method addresses and interlock semantics from 507A/907A. Tests should verify cursor position and image updates on Volta-or-newer heads, including 128/256 cursor layouts supplied by newer head functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/cursc37a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/dac507d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/dac507d.c

### Purpose
`dac507d.c` implements analog DAC output-resource control for the NV507D display class.

### Key APIs And Functions
`dac507d_ctrl()` writes `DAC_SET_CONTROL` and `DAC_SET_POLARITY` methods through the core push channel. It extracts hsync/vsync polarity from `nv50_head_atom` when enabling and leaves polarity zero when disabling. The exported `nv50_outp_func dac507d` exposes this as `.ctrl`.

### Control Flow And State
The helper reserves push space, composes a sync-polarity word, emits control and polarity methods, and returns without kicking; the core commit path performs the update. No file-local state is retained.

### Dependencies And Integration
It depends on `core.h`, `push507c`, and `cl507d`. `disp.c` DAC encoder helpers call the core function table's DAC control callback during atomic enable/disable.

### Risks And Test Signals
Incorrect polarity programming affects analog display sync. Tests should include CRT detection and modeset on NV50-class DAC outputs, disable/re-enable, and negative sync modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/dac507d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/dac907d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/dac907d.c

### Purpose
`dac907d.c` implements analog DAC control for the NV907D-era display class, where sync polarity is no longer programmed in the DAC helper.

### Key APIs And Functions
`dac907d_ctrl()` reserves push space and writes `NV907D DAC_SET_CONTROL(or)` with the caller-supplied owner/protocol control word. The exported `dac907d` function table exposes the helper as `.ctrl`.

### Control Flow And State
No state is retained locally. DAC ownership is updated through the core channel and later synchronized by the surrounding core update.

### Dependencies And Integration
It depends on `core.h`, `push507c`, and `cl907d`. The encoder path in `disp.c` selects it through the generation-specific core output function table.

### Risks And Test Signals
The helper deliberately ignores `asyh`; polarity/depth must be handled elsewhere for this generation. Tests should cover analog enable/disable and ownership assignment for head 0 through later supported head masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/dac907d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.c

### Purpose
`disp.c` is the central NV50+ Nouveau KMS display implementation. It creates EVO/NVD channels, DRM connectors/encoders/CRTCs, audio and HDMI infoframe plumbing, DisplayPort MST management, output-resource programming, atomic state allocation/check/commit, suspend/resume hooks, and display format-modifier lists.

### Key APIs And Functions
Channel helpers include `nv50_chan_create()`, `nv50_dmac_create()`, `nv50_dmac_wait()`, and `nv50_dmac_kick()`. Output helpers include `nv50_dac_create()`, `nv50_sor_create()`, `nv50_pior_create()`, `nv50_outp_atomic_check()`, `nv50_real_outp()`, HDMI/audio helpers, and MST structures/functions (`nv50_mstm`, `nv50_mstc`, `nv50_msto`). Atomic entry points are `nv50_disp_atomic_check()`, `nv50_disp_atomic_commit()`, and `nv50_disp_atomic_commit_tail()`. Lifecycle entry points are `nv50_display_create()`, `nv50_display_init()`, `nv50_display_fini()`, and `nv50_display_destroy()`.

### Control Flow And State
Creation allocates `nv50_disp`, a shared VRAM sync BO, the core channel, capability object, format modifiers, encoder/connector objects from NVIF output info, heads from the display head mask, optional MST encoders, and audio component registration. Atomic check builds output-change records, handles static window mapping, asks DRM helpers and MST helpers to validate state, and resolves CRC conflicts. Atomic commit prepares planes, swaps state, sequences output/head/window disable and enable operations under `disp->mutex` when needed, performs core/window interlocked updates, handles MST payload part1/part2, waits for plane notifiers, sends vblank events, and coordinates CRC notifier contexts.

### Dependencies And Integration
The file depends on DRM atomic, connector, EDID, HDMI, DP, MST, vblank, framebuffer, runtime-PM, component/audio, and Nouveau NVIF output/channel/memory APIs. It integrates every local dispnv50 subsystem: `core`, `head`, `wndw`, `base`, `ovly`, `curs`, `crc`, and output-resource function tables.

### Risks And Test Signals
This file is timing-sensitive and stateful. Risks include push-buffer wrap and VRAM coherency, runtime-PM reference imbalance, MST payload ordering, audio ELD races, CRC/output reprogramming conflicts, initial state readback mismatches, and generation-specific format modifier selection. Tests should cover blocking and nonblocking atomic commits, DP/HDMI/LVDS/DAC/PIOR outputs, MST hotplug and payload changes, suspend/resume, vblank events, plane notifier timeouts, audio ELD notification, and Pascal VRAM push-buffer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.h

### Purpose
`disp.h` declares the shared NV50 display device/channel structures and synchronization-memory offsets used by the dispnv50 implementation.

### Key APIs And Types
`struct nv50_disp` holds the NVIF display object, core channel, caps object, shared sync BO, and display mutex. Macros define offsets for core notifier, window semaphores, and window notifiers. `struct nv50_disp_interlock` describes interlock type/data/wimm state. `struct nv50_chan`, `struct nv50_dmac`, and `struct nv50_outp_atom` define common channel and output-atomic state. The header declares DMA channel creation/destruction, `nv50_real_outp()`, display modifiers, and shared helpers.

### Control Flow And State
There is no control flow in the header. Its definitions persist through the whole KMS lifecycle: `nv50_disp` is stored in `nouveau_display(dev)->priv`, `nv50_dmac` backs core/window push channels, and `nv50_outp_atom` nodes live inside an atomic commit state.

### Dependencies And Integration
It depends on Linux workqueues, NVIF memory/push APIs, and Nouveau display headers. Nearly every dispnv50 file includes it directly or indirectly for sync offsets, channel state, and display-private access.

### Risks And Test Signals
Offset macros are hardware contracts shared by notifiers and semaphores. Tests should validate notifier/semaphore completion for base, overlay, window, and core channels, and build coverage should catch structure users when fields evolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/handles.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/handles.h

### Purpose
`handles.h` centralizes Nouveau-chosen display object handles for sync buffers, VRAM contexts, window contexts, and CRC notifier contexts.

### Key APIs And Macros
It defines `NV50_DISP_HANDLE_SYNCBUF`, `NV50_DISP_HANDLE_VRAM`, `NV50_DISP_HANDLE_WNDW_CTX(kind)`, and `NV50_DISP_HANDLE_CRC_CTX(head, i)`.

### Control Flow And State
The header has no runtime logic. The constants become persistent object identifiers passed to NVIF object constructors. On Blackwell paths without CTXDMAs, fake handles preserve nonzero-handle enable checks in existing code.

### Dependencies And Integration
`disp.c` uses sync/VRAM handles for DMA channel context objects, window code uses window context handles, and `crc.c` uses CRC context handles for per-head notifier DMA objects.

### Risks And Test Signals
Uniqueness is the key invariant. Handle collision would bind methods to the wrong object. Tests should cover simultaneous window and CRC context creation, multi-head CRC setup, and Blackwell paths that rely on fake handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/handles.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.c

### Purpose
`head.c` implements the common DRM CRTC/head layer for NV50 display. It translates DRM atomic CRTC state into `nv50_head_atom`, validates color/scaler/dither/procamp/CRC state, flushes head programming through generation-specific callbacks, creates head planes, and handles vblank/CRC events.

### Key APIs And Functions
Public helpers are `nv50_head_create()`, `nv50_head_flush_set()`, `nv50_head_flush_set_wndw()`, and `nv50_head_flush_clr()`. Atomic helpers compute procamp, dither, viewport/scaler, LUT validity, hardware mode timing, and set/clr masks. DRM CRTC functions duplicate/destroy/reset state, expose vblank callbacks, and register CRC debugfs. `nv50_head_vblank_handler()` bridges NVIF vblank events to DRM and CRC handling.

### Control Flow And State
During atomic check, the file validates LUT sizes, handles output scaling/underscan/aspect/center modes, calculates hardware raster timing with interlace adjustments, derives set/clr masks by comparing old and new head atoms, and requests `disp->mutex` locking when head state changes. During commit, `disp.c` calls flush helpers that dispatch to the selected `nv50_head_func`. Creation selects old or CRC-capable CRTC funcs by display class, creates base/overlay/window/cursor planes, enables color management, allocates OLUT memory when needed, constructs an NVIF head object, and registers vblank events.

### Dependencies And Integration
The file depends on DRM atomic/vblank/color helpers, Nouveau connector/CRTC/display code, NVIF head/event APIs, and local base/core/curs/ovly/crc/lut modules. It is the central integration point between DRM CRTC state and generation files such as `head507d.c`, `head907d.c`, and `headc37d.c`.

### Risks And Test Signals
The set/clr mask logic controls hardware sequencing, so subtle comparisons can cause missed updates or unnecessary modesets. Risks include LUT stealing by indexed-color windows, cursor/core ordering constraints, scaler math edge cases, runtime-PM/vblank pairing, and CRC state transitions. Tests should cover modeset and fastset paths, gamma/degamma sizes, underscan/aspect scaling, cursor-only updates, base/overlay visibility changes, vblank events, and debugfs CRC hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.h

### Purpose
`head.h` defines the NV50 head object and the generation-specific head programming function table used by common CRTC code.

### Key APIs And Types
`struct nv50_head` contains the selected `nv50_head_func`, display pointer, embedded `nouveau_crtc`, CRC state, output LUT memory, and optional MST encoder. `struct nv50_head_func` declares callbacks for view, mode, OLUT, core surface, cursor, base/overlay usage, dither, procamp, output resource, static window mapping, and display ID programming. The header also declares all exported generation helpers and function tables.

### Control Flow And State
The header does not execute logic. Its callback table determines which register methods common `head.c` flushes during atomic commits, while the `nv50_head` structure persists for the lifetime of a DRM CRTC.

### Dependencies And Integration
It includes local `disp.h`, `atom.h`, `crc.h`, and `lut.h`, plus Nouveau CRTC/encoder headers. It is consumed by `head.c`, core function tables, cursor/CRC/output code, and all `head*` generation files.

### Risks And Test Signals
Callback optionality is important: common code checks some function pointers but assumes others for active generations. Build and runtime coverage should include each display class table, including paths with no `or`, no `core_calc`, and Blackwell physical-address callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head507d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head507d.c

### Purpose
`head507d.c` implements the NV507D base head programming table for early NV50 display hardware. It writes raster timing, viewport scaler, core/base/overlay usage, cursor, output LUT, dither, and procamp methods.

### Key APIs And Functions
Exported helpers include `head507d_view()`, `head507d_mode()`, `head507d_olut()`, `head507d_core_calc()`, `head507d_core_clr()`, `head507d_curs_layout()`, `head507d_curs_format()`, `head507d_base()`, `head507d_ovly()`, `head507d_dither()`, and `head507d_procamp()`. Static helpers implement cursor set/clr, core set, and OLUT set/clr/load. The `head507d` table wires all callbacks.

### Control Flow And State
`head507d_core_calc()` derives a dummy or real core surface from base/overlay/cursor visibility and writes pitch-linear A8R8G8B8 defaults. Cursor programming accepts ARGB8888 and 32/64 layouts. OLUT supports 256-entry LUTs and appends a duplicate final entry for interpolation. Mode programming converts `nv50_head_mode` timing into `HEAD_SET_*` methods.

### Dependencies And Integration
It depends on `cl507d`, `push507c`, `head.h`, and `core.h`. Common `head.c` computes atom state and calls this table for old display classes.

### Risks And Test Signals
The core dummy-surface workaround, cursor/core ordering note, and 256-entry-only OLUT are important constraints. Tests should cover old NV50 modesets with base-only, overlay-only, cursor-only, gamma LUT, dither/procamp changes, and 32/64 cursor validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head507d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head827d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head827d.c

### Purpose
`head827d.c` adapts the 507D head table for 827D-era hardware, mainly by adding explicit CTXDMA programming for cursor, core, and LUT resources and using updated method names.

### Key APIs And Functions
Static helpers implement `head827d_curs_clr()`, `head827d_curs_set()`, `head827d_core_set()`, `head827d_olut_clr()`, and `head827d_olut_set()`. The exported `head827d` table reuses 507D view/mode/core-calc/layout/format/base/overlay/dither/procamp logic while replacing the resource-binding callbacks.

### Control Flow And State
Cursor set writes control, offset, and cursor context DMA; clear disables and clears the context. Core set writes offset, size, storage, params, context DMA, and viewport point. OLUT set enables the LUT and binds `HEAD_SET_CONTEXT_DMA_LUT`; clear disables and clears the context. Runtime state remains in `nv50_head_atom`.

### Dependencies And Integration
It depends on `cl827d`, `push507c`, `head.h`, and `core.h`. It is selected by generation-specific core tables for display classes that need 827D resource methods.

### Risks And Test Signals
Handle programming is the key difference from 507D; stale or missing context DMA handles can produce blank scanout, cursor, or LUT output. Tests should cover gamma updates, cursor image changes, framebuffer format changes, and disable/re-enable on 827D-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head827d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head907d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head907d.c

### Purpose
`head907d.c` implements the Fermi/Kepler-era 907D head function table. It updates raster timing, viewport limits, output-resource control, OLUT/ILUT validation, cursor, core surface, base/overlay usage bounds, dither, and procamp programming.

### Key APIs And Functions
Exported callbacks include `head907d_or()`, `head907d_procamp()`, `head907d_ovly()`, `head907d_curs_set()`, `head907d_curs_clr()`, `head907d_core_set()`, `head907d_core_clr()`, `head907d_olut_set()`, `head907d_olut_clr()`, `head907d_olut_load()`, `head907d_olut()`, `head907d_ilut_check()`, `head907d_mode()`, and `head907d_view()`. The `head907d` table reuses 507D cursor layout/format and core calculation.

### Control Flow And State
Mode programming uses Hz pixel-clock methods plus max frequency. Output-resource programming includes CRC raster mode, sync polarity, pixel depth, and control structure. OLUT accepts 256 or 1024 user entries, selects 257/1025 interpolation modes, and stores 14-bit values with a bias. Cursor/core methods bind CTXDMA handles, and usage bounds include 64/32/16/8 bpp variants.

### Dependencies And Integration
It depends on DRM connector/mode/vblank headers, Nouveau BIOS/connector data, `cl907d`, `push507c`, and local core/head/CRC headers. It is used by `head917d.c` and other later files as a base for shared functionality.

### Risks And Test Signals
Pixel depth, CRC raster, and LUT sizing feed multiple subsystems. Tests should cover 6/8/10 bpc DP modes, 256/1024 gamma and degamma, CRC source changes, cursor image updates, overlay usage bounds, interlaced modes, and viewport min/max programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head907d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head917d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head917d.c

### Purpose
`head917d.c` adapts the 907D head implementation for 917D-era hardware with updated dither/base/cursor methods and support for larger cursor layouts.

### Key APIs And Functions
`head917d_dither()` writes `NV917D HEAD_SET_DITHER_CONTROL`. `head917d_base()` programs base usage bounds and advertises 1025-entry base LUT usage. `head917d_curs_set()` writes cursor control, offset, and context DMA. `head917d_curs_layout()` accepts 32, 64, 128, and 256-pixel cursor widths. The exported `head917d` table otherwise reuses 907D view/mode/OLUT/core/overlay/procamp/output-resource callbacks.

### Control Flow And State
The wrapper preserves 907D timing and color behavior but adjusts method encodings for the newer class. Cursor layout is derived from framebuffer width rather than the parsed image width.

### Dependencies And Integration
It depends on `cl917d`, `push507c`, generic push helpers, and shared head/core declarations. It is selected for display classes that sit between 907D and C37D behavior.

### Risks And Test Signals
Cursor size support is broader and must match mode-config cursor limits. Tests should exercise 128/256 cursor images, base LUT usage with gamma, dither property changes, and modeset reuse of inherited 907D callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head917d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc37d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc37d.c

### Purpose
`headc37d.c` implements Volta/Turing-style C37D head programming for static window-channel display hardware. It handles output resource, procamp, dither, cursor, output LUT, raster timing, viewport, and static window ownership.

### Key APIs And Functions
Important callbacks are `headc37d_view()`, `headc37d_curs_format()`, `headc37d_curs_set()`, `headc37d_curs_clr()`, `headc37d_dither()`, and `headc37d_static_wndw_map()`. Static helpers implement `headc37d_or()`, `headc37d_procamp()`, `headc37d_olut_*()`, `headc37d_olut()`, and `headc37d_mode()`. The `headc37d` table omits old core/base/overlay callbacks because newer window channels own scanout more directly.

### Control Flow And State
Static window mapping assigns two windows per head. Mode programming writes raster timing, raw sequence methods for interlace/blank2 fields, pixel clocks, and head usage bounds. OLUT accepts 256 or 1024 entries with unity range and interpolation, using `head907d_olut_load()`. Cursor programming writes control, composition, context DMA, and offset.

### Dependencies And Integration
It depends on `clc37d`, `pushc37b`, `atom.h`, `head.h`, and shared 907D helpers. `disp.c` calls `static_wndw_map` during atomic check when initial window assignment is required.

### Risks And Test Signals
Depth mapping contains a known hack translating older depth encodings. Raw `PUSH_NVSQ` methods and static two-window ownership are fragile. Tests should cover every head/window pair, 256/1024 LUTs, 256 cursor support, interlaced modes, DP depth variants, and initial modeset after firmware-provided state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc37d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc57d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc57d.c

### Purpose
`headc57d.c` provides C57D/GV100+ head programming variants on top of the C37D model. It adds display-ID programming, C57D output-resource/procamp/mode methods, and a VSS-header output LUT format with optional identity LUT support.

### Key APIs And Functions
`headc57d_display_id()` writes a display-id method. `headc57d_or()` programs output resource with CRC/sync/depth and ext-packet window fields. `headc57d_procamp()` writes simplified RGB procamp. `headc57d_olut_set()` and `_clr()` bind OLUT context and control. `headc57d_olut_load_8()`, `headc57d_olut_load()`, and `headc57d_olut()` define 256/1024/identity LUT loading. `headc57d_mode()` writes C57D raster timing and head usage bounds.

### Control Flow And State
The OLUT path writes a 0x20-byte VSS header before entries; 256-entry LUTs are expanded by interpolating four entries per input point. `olut_identity = true` lets common code install an identity LUT when no userspace gamma blob is present. The function table reuses C37D viewport, cursor, dither, static window mapping, and cursor format callbacks.

### Dependencies And Integration
It depends on `clc57d`, `pushc37b`, `atom.h`, and shared head/core code. `corec57d.c` selects this table for GV100/Turing-class core channels, and MST/SOR paths call `display_id` where available.

### Risks And Test Signals
LUT memory format and display-id programming are key differences. Tests should cover identity gamma, 256 and 1024 gamma blobs, MST display-id allocation/release, DP depth mapping, and C57D initial modeset after firmware window assignment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headc57d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headca7d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headca7d.c

### Purpose
`headca7d.c` implements GB202/Blackwell head programming. It follows the C57D/C37D logical model but uses `NVCA7D` methods and physical surface addresses for cursor and output LUT resources.

### Key APIs And Functions
Callbacks include `headca7d_display_id()`, `headca7d_or()`, `headca7d_procamp()`, `headca7d_dither()`, `headca7d_curs_set()`, `headca7d_curs_clr()`, `headca7d_olut_set()`, `headca7d_olut_clr()`, `headca7d_mode()`, and `headca7d_view()`. The `headca7d` table reuses `headc57d_olut()`, `head917d_curs_layout()`, `headc37d_curs_format()`, static window mapping, and 907D ILUT validation.

### Control Flow And State
Cursor and OLUT set paths split buffer offsets into high/low physical address fields, set target `PHYSICAL_NVM`, and enable the corresponding surface. Clear paths disable the low address method. Mode programming writes raster timing, progressive structure, and pixel clock frequency/max; output-resource programming uses explicit `NVCA7D` bpp constants and rejects unknown depth encodings.

### Dependencies And Integration
It depends on `clca7d`, `pushc97b`, `atom.h`, `head.h`, and shared head helpers. `coreca7d.c` selects this table for Blackwell display cores.

### Risks And Test Signals
Physical-address programming increases alignment and lifetime risk for cursor/LUT memory. Tests should cover cursor and gamma updates on GB202, 6/8/10 bpc output depth, display-id use with MST, suspend/resume, and invalid depth handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/headca7d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.c

### Purpose
`lut.c` manages per-head output LUT backing memory and loading. It allocates double-buffered VRAM LUT storage and populates either userspace-provided gamma data or a generated identity ramp.

### Key APIs And Functions
`nv50_lut_init()` allocates and maps two `kmsLut` VRAM buffers sized for 257 or 1025 entries depending on display class. `nv50_lut_load()` selects a buffer, obtains blob data or creates a 1024-entry identity LUT, calls the generation-specific `load()` writer, and returns the GPU address. `nv50_lut_fini()` destroys both memory objects.

### Control Flow And State
LUT state persists in `struct nv50_lut.mem[2]`; common head atomic code toggles buffers to avoid overwriting an active LUT. Identity generation uses `kvmalloc_objs()` and fills a linear 16-bit ramp before invoking the hardware-specific loader.

### Dependencies And Integration
The file depends on DRM color management helpers, NVIF memory mapping, and `disp.h`. `head.c` allocates LUT memory during CRTC creation and loads it from `nv50_head_flush_set_wndw()`.

### Risks And Test Signals
Allocation failure, incorrect size selection, or identity-ramp generation problems affect gamma output. Tests should cover 257-entry old hardware, 1025-entry newer hardware, NULL gamma blob identity behavior, double-buffer flips, and cleanup on head creation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.h

### Purpose
`lut.h` declares the NV50 output LUT memory wrapper and load/init/fini helpers.

### Key APIs And Types
`struct nv50_lut` contains two `nvif_mem` buffers for double-buffered LUT updates. The header declares `nv50_lut_init()`, `nv50_lut_fini()`, and `nv50_lut_load()`, with the load API accepting a generation-specific writer callback.

### Control Flow And State
The header has no executable control flow. Its state contract is embedded in `struct nv50_head` and used by head atomic commits.

### Dependencies And Integration
It includes `nvif/mem.h` and forward-declares DRM property/color LUT and `nv50_disp` types. It is included by `head.h` and implemented by `lut.c`.

### Risks And Test Signals
The double-buffer invariant is shared with head atomic state. Build tests should catch callback signature drift; runtime tests should verify gamma updates do not tear or overwrite active hardware reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.c

### Purpose
`oimm.c` selects and initializes the overlay immediate channel used with pre-GV100 overlay planes.

### Key APIs And Functions
`nv50_oimm_init()` probes a class table for overlay immediate classes from GK104 down to NV50 and dispatches to `oimm507b_init()`. It logs and returns the probe error when no supported class is present.

### Control Flow And State
The function only probes and delegates. The selected initializer attaches an immediate-channel object and function table to an existing overlay `nv50_wndw`.

### Dependencies And Integration
It depends on `oimm.h`, NVIF class IDs, and `nv50_disp()`. `nv50_ovly_new()` calls it after constructing a DMA overlay channel.

### Risks And Test Signals
Overlay immediate channel absence prevents overlay plane creation on old hardware. Tests should cover class selection across NV50/G82/GT214/GF110/GK104 and failure cleanup in `nv50_ovly_new()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.h

### Purpose
`oimm.h` declares overlay immediate-channel initialization helpers.

### Key APIs And Functions
It exposes `oimm507b_init()` for generation-specific construction and `nv50_oimm_init()` for class selection.

### Control Flow And State
The header has no logic. Its functions attach immediate-channel state to an already-created `nv50_wndw` overlay plane.

### Dependencies And Integration
It includes `wndw.h` and is used by `ovly.c` and `oimm507b.c`.

### Risks And Test Signals
The interface is narrow but tied to old overlay support. Build coverage plus overlay plane creation tests on pre-GV100 hardware are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm507b.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm507b.c

### Purpose
`oimm507b.c` constructs the NV50-style overlay immediate-channel object and binds it to a common immediate function table.

### Key APIs And Functions
`oimm507b_init_()` creates and maps a `kmsOvim` NVIF display channel for `wndw->id`, assigns `wndw->immd`, and logs allocation failures. `oimm507b_init()` calls it with the cursor immediate function table `curs507a`, reusing point/update behavior.

### Control Flow And State
The initializer creates the NVIF object under the display object, maps it, and stores the immediate callback pointer in the overlay window. State persists in `wndw->wimm.base.user` and `wndw->immd`.

### Dependencies And Integration
It depends on `oimm.h`, `if0014` display-channel arguments, and `curs507a` from the cursor implementation. It is called by `nv50_oimm_init()` after overlay DMA channel creation.

### Risks And Test Signals
Reusing cursor immediate callbacks for overlay immediate behavior relies on compatible method semantics. Tests should cover overlay point/update immediate operations, allocation failure paths, and object teardown through window destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm507b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.c

### Purpose
`ovly.c` selects and creates pre-GV100 overlay DMA channels and attaches the matching overlay immediate channel.

### Key APIs And Functions
`nv50_ovly_new()` probes overlay DMA/control classes from GK104 down to NV50, dispatches to `ovly917e_new()`, `ovly907e_new()`, `ovly827e_new()`, or `ovly507e_new()`, then calls `nv50_oimm_init()` on the created window.

### Control Flow And State
The function chooses the highest supported class, constructs the overlay `nv50_wndw`, and initializes immediate-channel state. The persistent state is stored in the returned window object.

### Dependencies And Integration
It depends on `ovly.h`, `oimm.h`, NVIF class probing, and `nv50_disp()`. `head.c` calls it while creating old-generation heads.

### Risks And Test Signals
Both DMA and immediate objects must be created successfully for a usable overlay plane. Tests should cover class selection, failure cleanup, overlay plane visibility changes, and old display classes where overlay support differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.h

### Purpose
`ovly.h` declares overlay plane constructors and shared overlay helper callbacks for NV50 display classes.

### Key APIs And Functions
It exposes constructors for `ovly507e`, `ovly827e`, `ovly907e`, `ovly917e`, the shared `ovly507e_new_()`, acquire/release/scale helpers, 827E notifier helpers, `ovly827e_format`, `ovly907e`, and the public `nv50_ovly_new()`.

### Control Flow And State
The header has no executable logic. Its declarations define the shared construction and function-table contracts for overlay windows.

### Dependencies And Integration
It includes `wndw.h` and is used by overlay generation files, `ovly.c`, and head creation in `head.c`.

### Risks And Test Signals
The shared helper signatures affect multiple overlay generations. Build tests across enabled generations and runtime overlay tests on 507E/827E/907E/917E classes are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly507e.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly507e.c

### Purpose
`ovly507e.c` implements the base NV50 overlay DMA plane. It validates overlay plane state, programs image and scaling methods, and constructs the overlay DMA channel with notifier/semaphore offsets.

### Key APIs And Functions
`ovly507e_scale_set()` writes source point, input size, and output width. `ovly507e_image_set()` writes present control, ISO context, composition mode, surface offset/size/storage/params. `ovly507e_acquire()` validates no scaling via DRM helpers and stores bytes-per-pixel in head overlay state. `ovly507e_release()` clears overlay cpp. `ovly507e_new_()` constructs the DRM overlay plane and DMA channel; `ovly507e_new()` supplies NV50 formats and interlock data.

### Control Flow And State
Acquire/release update `asyh->ovly.cpp`, which common head code turns into usage-bound updates. Image and scale programming write into the overlay DMA push buffer; update and notifier callbacks are inherited from base channel helpers. The constructed window stores `ntfy`, `sema`, and initial notifier data offsets.

### Dependencies And Integration
It depends on DRM atomic/fourcc helpers, `cl507e`, `if0014`, `push507c`, `atom.h`, `ovly.h`, and `nv50_dmac_create()`. `ovly.c` selects it for NV50 overlay class support.

### Risks And Test Signals
Surface storage programming includes pitch/block fields and a duplicated `PITCH` macro use for blocks, so format/layout tests matter. Tests should cover supported YUYV/UYVY/XRGB formats, overlay enable/disable, notifier completion, no-scaling validation, and semaphore offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly507e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly827e.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly827e.c

### Purpose
`ovly827e.c` adapts the base overlay plane to 827E-era hardware. It changes image method encoding, adds 10-bit XBGR format support, and provides notifier reset/wait helpers for the newer notification layout.

### Key APIs And Functions
`ovly827e_image_set()` writes `NV827E` present, context, composition, surface offset/size/storage/params methods. `ovly827e_ntfy_wait_begun()` polls the notification status for `BEGUN` with a 2-second timeout. `ovly827e_ntfy_reset()` clears timestamp/status fields. The `ovly827e` function table reuses 507E acquire/release/scale/update and base notifier set/clear. `ovly827e_new()` calls `ovly507e_new_()`.

### Control Flow And State
The 827E window uses the same DMA-channel lifetime as 507E but with class-specific image methods and notification status handling. Supported formats add `DRM_FORMAT_XBGR2101010`.

### Dependencies And Integration
It depends on `cl827e`, `push507c`, NVIF timers, `nouveau_bo`, `atom.h`, and shared overlay/base helpers. `ovly.c` selects it for GT200/G82/GT214 overlay DMA classes.

### Risks And Test Signals
Notifier polling is timeout-sensitive, and image method fields must match the class layout. Tests should cover notification reset/wait, 10-bit overlay formats, enable/disable cycles, and timeout logging under stalled hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly827e.c -->
