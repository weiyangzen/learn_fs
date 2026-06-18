# subset-b-003676 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.h

## Purpose

`ior.h` defines nouveau's display output-resource abstraction. An IOR is the hardware resource that actually drives a connector path: DAC for analog/TV, SOR for LVDS/TMDS/HDMI/DP/eDP, and PIOR for external output resources.

## Important APIs, Types, And Functions

The central type is `struct nvkm_ior`, which stores the display pointer, resource type/id, HDA capability, identity routing flag, armed and assembly states, and protocol-specific DP/TMDS state. `struct nvkm_ior_state` tracks the output path attached to a resource, raster generator divider, EVO protocol, decoded protocol, link selection, and head mask. `struct nvkm_ior_func` is the generation-specific method table for route get/set, state readback, power, load sense, clocking, workarounds, backlight, HDMI, DP, and HDA programming. Helper prototypes expose resource creation/destruction/find and many generation-specific SOR/DAC/PIOR operations from NV50 through TU102/GV100-era hardware.

## Control Flow

The header is a contract rather than an executable unit. Display constructors choose an `nvkm_ior_func` table per chipset, create IORs with `nvkm_ior_new_()`, and later output-path code attaches `struct nvkm_outp` objects to the IOR `asy` state. Supervisor code reads `arm` and `asy` with `func->state`, performs BIOS scripts and link programming, then arms hardware. DP/HDMI/HDA userspace methods reach the generation hooks through the nested function tables.

## State And Persistence Behavior

IOR objects are persistent display-engine objects stored on `disp->iors`. `arm` mirrors hardware state and `asy` is the next assembled modeset state. DP lane count, bandwidth, enhanced framing, MST, and TMDS high-speed flags are kept in the IOR because they affect later supervisor and audio/link callbacks.

## Dependencies And Integration Points

This file ties together `priv.h`, output paths, DP AUX, connector/user wrappers, BIOS display tables, and generation files such as `nv50.c`, `gf119.c`, `gm200.c`, `gv100.c`, and `tu102.c`.

## Risks And Edge Cases

The function table is sparse by generation; callers must check optional hooks before use. `nv50_sor_link()` depends on `asy.link`, so stale assembly state can address the wrong register lane. Route callbacks are only present on later dynamic-routing SORs. Identity-mapped panel outputs must not be reassigned casually because backlight and panel wiring can be tied to a specific SOR.

## Test Signals

Useful signals are correct IOR enumeration in boot logs, successful mode inheritance from firmware, DP/HDMI link training without missing hook failures, HDA audio hotplug/ELD events on HDA-capable SORs, and backlight operations working only on IORs with `bl` hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/ior.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp77.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp77.c

## Purpose

`mcp77.c` supplies the display function table for MCP77-family integrated GPUs. It reuses the NV50 EVO display core while selecting G94-style SOR behavior and GT206 class IDs.

## Important APIs, Types, And Functions

`mcp77_sor` is the SOR method table. It combines `g94_sor_state`, `nv50_sor_power`, `nv50_sor_clock`, NV50 backlight, G84 HDMI, and G94 DP support. `mcp77_sor_new()` wraps that table with `nvkm_ior_new_()`. `mcp77_disp` is the full `nvkm_disp_func` descriptor: NV50 oneinit/init/fini/intr/super, NV50 heads/DAC/PIOR, G94 SOR count, GT206 root class, and G82/GT200/GT206 user channel classes. `mcp77_disp_new()` constructs the engine through `nvkm_disp_new_()`.

## Control Flow

Probe reaches `mcp77_disp_new()`, which installs `mcp77_disp`. During oneinit, shared NV50 code enumerates heads, DACs, SORs, PIORs, outputs, and connectors. SOR creation calls `mcp77_sor_new()`, giving each SOR the MCP77-specific capability mix. Runtime mode changes use the inherited NV50 supervisor and channel paths.

## State And Persistence Behavior

No private state is introduced. Persistent state lives in the generic `nvkm_disp`, `nvkm_ior`, output, connector, and channel objects created by shared constructors.

## Dependencies And Integration Points

The file depends on `priv.h`, `chan.h`, `head.h`, `ior.h`, NVIF display class IDs, NV50 display core helpers, G94 SOR helpers, G84 HDMI, and GT200/G94 user channel descriptors from neighboring display files.

## Risks And Edge Cases

The table must match MCP77 hardware class IDs and SOR capabilities. A wrong SOR count or class mapping would expose unusable channels or miss DP/HDMI features. HDA is not enabled in `nvkm_ior_new_()`, unlike MCP89.

## Test Signals

Boot should report MCP77 display resources, modesets should exercise NV50 supervisor phases, HDMI and DP paths should work through G84/G94 hooks, and user channels should instantiate with the GT206/G82/GT200 class mix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp77.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp89.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp89.c

## Purpose

`mcp89.c` defines the MCP89/GT214 display variant. It reuses NV50 display infrastructure but uses GT215-era SOR features, HDA support, and a lane-reversed DP layout.

## Important APIs, Types, And Functions

`mcp89_sor_dp` supplies DP lane order `{3, 2, 1, 0}`, G94 link/power/pattern/drive/audio-symbol/active-symbol/watermark callbacks, and GT215 DP audio. `mcp89_sor` adds `g94_sor_state`, NV50 power/clock, GT215 backlight/HDMI/HDA, and the MCP89 DP table. `mcp89_sor_new()` creates HDA-capable SORs. `mcp89_disp` binds NV50 display lifecycle helpers with GT214 root/user classes.

## Control Flow

`mcp89_disp_new()` constructs the display engine with `mcp89_disp`. Shared NV50 oneinit enumerates display resources and invokes `mcp89_sor_new()` for each SOR. Later modesets execute through NV50 supervisor code but call MCP89's SOR DP/HDMI/HDA hooks when output methods request audio, link training, or backlight updates.

## State And Persistence Behavior

The file contributes static method tables only. Runtime state is stored in the generic display object graph, especially each SOR's `hda` flag and DP lane mapping in the function table.

## Dependencies And Integration Points

It depends on NV50 display core, G94 SOR DP helpers, GT215 backlight/HDMI/HDA helpers, and GT214/G84 class descriptors used by the NVIF client channel path.

## Risks And Edge Cases

The lane reversal is hardware-specific and affects DP training. Accidentally sharing the MCP77 table would break HDA audio and possibly DP lane ordering. Class IDs must align with userspace's expected GT214 display classes.

## Test Signals

Test signals include DP link training across all lane counts, HDA ELD/HPD changes through output methods, HDMI infoframe/audio behavior, and successful creation of GT214 display channel objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/mcp89.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/nv04.c

## Purpose

`nv04.c` implements the minimal pre-EVO display engine for NV04-era through early legacy chips. It provides CRTC head state/vblank handling and a simple interrupt handler without modern output-resource, channel, or supervisor machinery.

## Important APIs, Types, And Functions

`nv04_head_vblank_get()` and `nv04_head_vblank_put()` enable or disable vblank IRQs per head. `nv04_head_rgpos()` reads scanout position from legacy CRTC registers. `nv04_head_state()` reads timing totals and blanking ranges from VGA/CRTC MMIO. `nv04_disp_intr()` handles head vblank interrupts and logs/acks PVIDEO interrupts for NV10 through NV40-era chips. `nv04_disp_new()` constructs the display object and directly creates two heads.

## Control Flow

Probe calls `nv04_disp_new()`, which builds `nv04_disp` and then creates head 0 and head 1 using `nv04_head_new()`. Runtime interrupt delivery invokes `nv04_disp_intr()`, which checks CRTC interrupt registers, notifies vblank, and acknowledges bits. There is no oneinit resource enumeration and no user display channel table beyond an empty terminator.

## State And Persistence Behavior

Persistent state is just the generic `nvkm_disp` plus two `nvkm_head` objects. Hardware timing state is read on demand into `nvkm_head_state`; the driver does not maintain output-resource arm/asy state in this file.

## Dependencies And Integration Points

The file integrates with generic display construction, head helpers, vblank notification, legacy MMIO access, and NVIF class `NV04_DISP`. It also observes the device chipset to decide whether to process PVIDEO interrupts.

## Risks And Edge Cases

The head-state reader synthesizes blank end values as `total - 1` and has limited timing coverage. Register offsets differ from NV50 and cannot be mixed. PVIDEO interrupt logging ignores expected bits `0x11` and only warns on the rest.

## Test Signals

Useful validation is vblank events on both CRTCs, scanout-position reads returning changing line counters, no unhandled legacy PVIDEO interrupt spam, and DRM timestamp fallback when legacy timing data is insufficient elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/nv50.c

## Purpose

`nv50.c` is the shared NV50 EVO display implementation. It creates and programs DAC/SOR/PIOR output resources, heads, EVO display channels, user channel classes, interrupt handling, supervisor modeset phases, BIOS IED script execution, capability mirroring, and output/connector enumeration from DCB tables.

## Important APIs, Types, And Functions

Output-resource support includes `nv50_dac_*`, `nv50_sor_*`, and `nv50_pior_*` functions for count, construction, state readback, power sequencing, clocking, load sense, backlight, and DP link control. Head support is implemented by `nv50_head_state()`, `nv50_head_rgpos()`, `nv50_head_rgclk()`, and vblank enable/disable helpers. Channel support is split between PIO and DMA channel functions: `nv50_disp_pioc_func`, `nv50_disp_dmac_func`, `nv50_disp_core_func`, `nv50_disp_dmac_push()`, and `nv50_disp_dmac_bind()`. Supervisor helpers `nv50_disp_super_1()`, `nv50_disp_super_1_0()`, `nv50_disp_super_2_0()`, `nv50_disp_super_2_1()`, `nv50_disp_super_2_2()`, and `nv50_disp_super_3_0()` implement the multi-phase modeset sequence. `nv50_disp_intr()` decodes awaken, error, vblank, and supervisor interrupts. `nv50_disp_oneinit()` builds heads, IORs, output paths, connectors, RAMHT, and panel identity routing.

## Control Flow

Construction starts with `nv50_disp_new()` and `nvkm_disp_new_()`. Oneinit counts heads/DACs/SORs/PIORs from hardware caps, creates IOR/head objects, allocates instance memory and RAMHT, parses DCB outputs, constructs generic or DP output objects, creates connectors from BIOS connector data or I2C heuristics, and marks LVDS/eDP paths identity-mapped to their wired SOR. Init mirrors hardware capabilities into EVO registers, claims display from VBIOS if needed, points the display engine at instance memory, and enables supervisor interrupts. User channel creation then exposes cursor, overlay, base, core, and overlay DMA channel classes. Interrupts queue supervisor work or send channel/vblank events. The supervisor work item serializes with `disp->super.mutex`, reads pending phase bits, executes off/on BIOS scripts, updates PLLs, RG clock, DP active symbols/watermark/audio symbols, OR clocks, and workarounds, then acks completion.

## State And Persistence Behavior

The display object persists heads, IOR lists, output paths, connector lists, RAMHT, instance memory, channels, and supervisor pending bits. Each display channel persists push-memory target selection, suspend put pointer, class/method map, and interrupt state. Head and IOR `arm` state reflects current hardware, while `asy` reflects the next modeset. Backlight level and output routing are hardware state, not separately persisted by this file.

## Dependencies And Integration Points

This file integrates with BIOS DCB/connector/IED tables, BIOS init script execution, PLL programming through devinit, I2C/AUX, RAMHT, MMU memory targets, timer polling, NVIF display classes, output and DP constructors, and generic event/vblank delivery. Later chips reuse much of this code while overriding individual function tables.

## Risks And Edge Cases

Polling timeouts around channel init/fini and OR power sequencing can fail modesets with `-EBUSY`. DCB version expectations require 0x40-style output records. Missing BIOS IED or clock entries are logged and skipped, which may leave board-specific sequencing incomplete. DP watermark/active-symbol calculation is delicate and depends on mode timing, lane count, bpc, and enhanced framing. Boot-time inherited routes are handled conservatively to avoid switching firmware-selected ORs too early. Unsupported DCB output types are skipped.

## Test Signals

Signals include correct head/DAC/SOR/PIOR counts, successful creation of output and connector objects, vblank events on both heads, clean supervisor completion without channel timeout/error logs, working DAC load detection, DP/HDMI/LVDS modesets, backlight get/set on panels, and absence of `ERROR ... chid ... mthd` logs during display channel pushes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.c

## Purpose

`outp.c` implements generic display output-path objects. It maps DCB output records to compatible IOR protocols, inherits firmware routes, acquires/releases output resources for userspace and private operations, performs basic HPD detection, and dispatches backlight operations.

## Important APIs, Types, And Functions

`nvkm_outp_xlat()` maps DCB location/type pairs to IOR type and protocol. `nvkm_outp_acquire_or()`, `nvkm_outp_acquire_ior()`, and `nvkm_outp_acquire_hda()` select an output resource, preferring already armed resources, non-HDA SORs when audio is unnecessary, HDA SORs when requested, and identity-mapped panel SORs when required. `nvkm_outp_route()` applies route changes to dynamic-routing hardware. `nvkm_outp_release_or()` and `nvkm_outp_release()` clear acquisition bits and route state. `nvkm_outp_inherit()` discovers firmware-selected routes. `nvkm_outp_init()` records inherited active outputs and disables stale routed DP links when needed. `nvkm_outp_detect()` handles basic HPD. `nvkm_outp_new_()` and `nvkm_outp_new()` construct output objects.

## Control Flow

Display oneinit creates output paths from DCB entries using `nvkm_outp_new()` or DP-specific constructors. Init calls inherit/readback code so existing firmware modes can be represented. Userspace acquire methods call `func->acquire`, which eventually updates `outp->ior`, `ior->asy.outp`, and acquisition bits, then `nvkm_outp_route()` transitions route hardware. Release clears user state and applies route updates. Private helpers temporarily acquire output resources for load detect or backlight work.

## State And Persistence Behavior

`struct nvkm_outp` persists DCB metadata, I2C bus pointer, connector pointer, identity flag, acquisition bitmask, current IOR pointer, protocol-specific LVDS/DP state, and its user object. `ior->arm.outp` is the current hardware attachment and `ior->asy.outp` is the assembled next attachment.

## Dependencies And Integration Points

The file depends on BIOS DCB data, GPIO HPD, I2C, DP helpers, connector objects, IOR generation hooks, and NVKM object lifetime. It is used by display oneinit, user output wrappers, DP link training, HDMI/HDA methods, load detection, and backlight control.

## Risks And Edge Cases

The acquisition algorithm has many policy branches. Wrong identity handling can break LVDS/eDP panels, and wrong HDA preference can lose audio. `nvkm_outp_detect()` intentionally returns unknown for many non-DP no-HPD cases, leaving DDC probing to DRM. `nvkm_outp_init()` only records inherited modes when protocol and head state match.

## Test Signals

Useful checks are successful mode inheritance after firmware boot, stable OR assignment across modesets, panel backlight working on identity SORs, DP stale-route disable logs only when expected, and HPD/detect results matching physical connector changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.h

## Purpose

`outp.h` defines the private output-path data model and function-table contract for nouveau display outputs, including DCB metadata, acquisition state, LVDS/DP side state, user object embedding, and generic helpers.

## Important APIs, Types, And Functions

`struct nvkm_outp` stores `func`, `disp`, DCB index/info, I2C bus, connector, identity flag, acquisition bits (`NVKM_OUTP_PRIV` and `NVKM_OUTP_USER`), assigned IOR, LVDS flags, DP caps/link-training state, and asynchronous head pointer. `struct nvkm_outp_func` provides optional hooks for destructor/init/fini, detect, EDID, inherit/acquire/release, backlight, and DP AUX/rates/train/drive/MST methods. The header declares constructors, init/fini, detect, IOR acquire/release/inherit, backlight helpers, and output logging macros.

## Control Flow

The generic display code allocates an `nvkm_outp` with `nvkm_outp_new_()` or a specialized DP constructor. User methods and display modeset paths call the function-table hooks through this header's contract. Acquisition state flows from output object to IOR `asy` state and finally into supervisor routing/programming.

## State And Persistence Behavior

The output path persists for the display engine lifetime and caches both topology from VBIOS and dynamic link-training state. DP arrays record advertised rates, DPCD bytes, LTTPR data, AUX power state, MST status, and current training request. The `object` field is installed only while a userspace NVIF object has opened the output.

## Dependencies And Integration Points

The header includes DRM DP definitions and nouveau BIOS DCB/DP structures. It is used by generic output code, DP output implementation, user output methods, connector creation, and generation display files.

## Risks And Edge Cases

DP state in this structure is shared between kernel link management and userspace-facing NVIF methods; validation is needed before trusting userspace-provided rates, DPCD, or LTTPR counts. Acquisition bits allow private and user users to coexist, so release order matters.

## Test Signals

Build coverage catches function-table mismatches. Runtime signals include accurate output masks, DP train/rates calls updating cached state, correct acquire/release behavior, and no stale `object.func` exposure after destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/outp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/priv.h

## Purpose

`priv.h` is the private display-engine contract. It defines `struct nvkm_disp_func`, constructor prototypes, shared supervisor/init/intr helpers, and user object constructors consumed by all display generation files.

## Important APIs, Types, And Functions

`struct nvkm_disp_func` contains lifecycle hooks (`dtor`, `oneinit`, `init`, `fini`, `intr`, `super`), optional interrupt error handling, event function pointer, resource count/new callbacks for windows/heads/DACs/SORs/PIORs, RAMHT size, root class, and a variable user-class table. The file declares `nvkm_disp_ctor()`, `nvkm_disp_new_()`, `r535_disp_new()`, `nvkm_disp_vblank()`, NV50/GF119/GV100/TU102 shared helpers, channel event functions, and user constructors for display/connector/output/head.

## Control Flow

Generation files build static `nvkm_disp_func` tables and pass them to `nvkm_disp_new_()` or `r535_disp_new()`. Generic display construction later calls oneinit/init/fini/intr through this table. `udisp.c` enumerates `func->user[]` to expose generation-specific NVIF classes.

## State And Persistence Behavior

The header does not own state, but its function table determines which resource lists, RAMHT sizes, user classes, event hooks, and supervisor behavior are installed into each `struct nvkm_disp` instance.

## Dependencies And Integration Points

It includes public `engine/disp.h` and enum support, forward declares display private objects, and bridges classic nouveau display implementations with GSP/R535-backed display construction.

## Risks And Edge Cases

The user-class array is open-ended and must be terminated. Missing callbacks are meaningful for older generations, so callers must respect optionality. A generation table that mixes incompatible init/intr/super hooks with resource counts can expose wrong MMIO layouts.

## Test Signals

Test through successful build, display engine probe, root/user class enumeration, vblank events, and correct routing to GSP-backed `r535_disp_new()` on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/tu102.c

## Purpose

`tu102.c` defines the Turing TU102 display variant. It combines GV100-style window/head/display interrupt infrastructure with TU102-specific SOR DP link programming, MST VCPI programming, SOR capability detection, and display init register setup.

## Important APIs, Types, And Functions

`tu102_sor_dp_vcpi()` programs MST slot/PBN registers per head. `tu102_sor_dp_links()` writes DP link bandwidth, lane enables, MST and enhanced framing bits, and link control registers. `tu102_sor_dp` selects lane order, G94 power, GM107 pattern, GM200 drive, TU102 VCPI, and GV100 audio/watermark hooks. `tu102_sor` uses GM200 dynamic route get/set, GV100 state/HDMI/HDA, NV50 power, GF119 clock, and GT215 backlight. `tu102_sor_new()` reads HDA capability bits. `tu102_disp_init()` claims display ownership, mirrors pin/SOR/head/window/IHUB capabilities, configures instance memory, and programs interrupt masks. `tu102_disp_new()` chooses R535/GSP or classic construction.

## Control Flow

On classic probe, `tu102_disp_new()` installs `tu102_disp`. Shared NV50 oneinit creates topology, while TU102 init performs the generation-specific capability copy and interrupt enable sequence. During DP modeset, output methods and supervisor code call TU102/GV100 SOR hooks for links, audio, VCPI, and infoframes. On GSP-RM systems, construction diverts to `r535_disp_new()`.

## State And Persistence Behavior

Static function tables define behavior. Runtime state lives in common display, SOR, head, window, output, and channel objects. SOR HDA capability is captured per IOR at construction from register `0x08a15c`.

## Dependencies And Integration Points

The file depends on GV100 display/window/head/channel helpers, GM200 route and DP drive helpers, GSP detection, NVIF TU102/GV100 classes, and NVKM memory target selection for instance memory.

## Risks And Edge Cases

TU102 init writes a large interrupt and capability script; wrong masks can lose vblank or supervisor interrupts. The DP link function contains an explicit delay and broad mask writes; sequencing affects link stability. GSP routing must choose the correct backend or duplicate ownership with RM firmware.

## Test Signals

Signals include successful display ownership claim, correct head/window/SOR capability exposure, DP MST VCPI operation, HDMI/DP audio, vblank interrupts, working GSP and non-GSP probe paths, and no supervisor/error interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uconn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uconn.c

## Purpose

`uconn.c` exposes display connectors as NVIF user objects and translates kernel HPD/AUX/GSP events into NVIF connector events.

## Important APIs, Types, And Functions

`nvkm_uconn_uevent_gsp()`, `_aux()`, and `_gpio()` convert source-specific event bits to `NVIF_CONN_EVENT_V0_*` bits. `nvkm_uconn_uevent()` validates event arguments, finds an output on the connector, chooses GSP display events, DP AUX/I2C events, or GPIO HPD events, and registers the uevent. `nvkm_connector_is_dp_dms()` handles a DP DMS IRQ exception. `nvkm_uconn_new()` validates the connector id, maps DCB connector types to NVIF connector types, installs the object under `disp->client.lock`, and rejects duplicate opens.

## Control Flow

Userspace opens a connector object through `udisp.c`. `nvkm_uconn_new()` locates the connector by id and returns its type. Event registration later calls `nvkm_uconn_uevent()`, which selects the proper event backend depending on GSP, DP AUX presence, output location, and HPD GPIO. Destruction clears `conn->object.func` under the display client lock.

## State And Persistence Behavior

The connector object is embedded in `struct nvkm_conn`. Its `object.func` is non-NULL only while opened by a client. Event subscriptions are managed through `nvkm_uevent` and the underlying display/I2C/GPIO event sources.

## Dependencies And Integration Points

It depends on connector/output lists, GSP display resource manager events, I2C/AUX event sources, GPIO HPD events, DCB connector type constants, and NVIF connector ABI structures.

## Risks And Edge Cases

Only one user object can wrap a connector at a time. Some connector types are unimplemented and are reported as VGA while returning `-EINVAL`. DP IRQ over GPIO is rejected except for external/DMS cases. If no output path is found for a connector, event setup fails with `-EINVAL`.

## Test Signals

Test connector open/close, reported connector type, plug/unplug/IRQ delivery over GSP, AUX, and GPIO paths, duplicate open returning `-EBUSY`, and unsupported connector warnings for unusual DCB entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uconn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/udisp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/udisp.c

## Purpose

`udisp.c` exposes the display engine root object to NVIF clients. It reports connector/output/head masks and enumerates generic and generation-specific display child classes.

## Important APIs, Types, And Functions

`nvkm_udisp_sclass()` enumerates `NVIF_CLASS_CONN`, `NVIF_CLASS_OUTP`, `NVIF_CLASS_HEAD`, then the generation-specific `disp->func->user[]` channel/capability classes. `nvkm_udisp_new()` validates ABI arguments, enforces a single display root object per client display instance, constructs the object, and fills masks from `disp->conns`, `disp->outps`, and `disp->heads`. `nvkm_udisp_dtor()` clears the root object function pointer.

## Control Flow

Userspace opens the display engine root. The constructor returns topology masks, then userspace can enumerate child classes and open connectors, outputs, heads, or display channels. Child enumeration is purely table-driven from the generation's display function table.

## State And Persistence Behavior

The object is embedded in `disp->client.object`. `disp->client.lock` serializes open and destroy state. The masks are snapshots of the persistent lists built during display oneinit.

## Dependencies And Integration Points

It depends on `priv.h`, connector/head/output lists, NVIF display ABI `if0010`, and generation `nvkm_disp_func.user` tables.

## Risks And Edge Cases

The `disp->func->user[index]` lookup follows the three generic classes, so user arrays must be correctly terminated and aligned. Only one display root object can exist at a time for this embedded object.

## Test Signals

Signals are correct topology masks, successful enumeration of connector/output/head classes, expected generation channel class IDs, duplicate display opens returning `-EBUSY`, and cleanup allowing reopen after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/udisp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uhead.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uhead.c

## Purpose

`uhead.c` exposes display heads to NVIF clients. It provides vblank event subscription and scanout-position/timing queries for DRM timestamping.

## Important APIs, Types, And Functions

`nvkm_uhead_uevent()` registers vblank events on `head->disp->vblank`. `nvkm_uhead_mthd_scanoutpos()` validates ABI arguments, refreshes armed head state, fills total/blank timing, samples time before and after `head->func->rgpos()`, and returns current hline/vline. `nvkm_uhead_mthd()` dispatches `NVIF_HEAD_V0_SCANOUTPOS`. `nvkm_uhead_new()` finds a head by id and installs its embedded object under `disp->client.lock`.

## Control Flow

Userspace opens a head object through the display root. Event registration is direct to the vblank event source. Method calls route through the object function to scanout position. Destruction clears `head->object.func`.

## State And Persistence Behavior

The user object is embedded in `struct nvkm_head` and is single-open. Scanout data is not persisted; each call reads hardware state through the head function table.

## Dependencies And Integration Points

It depends on head generation hooks, display vblank event dispatch, NVIF head ABI, and kernel time sampling.

## Risks And Edge Cases

Pre-NV50 VGA paths can lack htotal/vtotal reads, so the method returns `-ENOTSUPP` to force DRM fallback. Event ABI validation is intentionally strict. Duplicate opens return `-EBUSY`.

## Test Signals

Test vblank event delivery, scanout-position monotonicity, proper `-ENOTSUPP` on unsupported legacy heads, and no stale object exposure after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uhead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uoutp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uoutp.c

## Purpose

`uoutp.c` exposes display output paths to NVIF clients. It implements methods for acquire/release/inherit, detection/EDID/load detect, backlight, LVDS state, HDMI/SCDC/infoframes/audio, HDA ELD, and DisplayPort AUX/link training/MST programming.

## Important APIs, Types, And Functions

DP methods include `nvkm_uoutp_mthd_dp_aux_pwr()`, `_aux_xfer()`, `_rates()`, `_train()`, `_drive()`, `_sst()`, `_mst_id_get()`, `_mst_id_put()`, and `_mst_vcpi()`. HDMI/audio methods include `nvkm_uoutp_mthd_hdmi()`, `_infoframe()`, and `_hda_eld()`. Output ownership methods include `nvkm_uoutp_mthd_acquire()`, `_release()`, `_inherit()`, and `_acquired()`. Detection helpers include `_detect()`, `_edid_get()`, and `_load_detect()`. `nvkm_uoutp_new()` maps requested output id to an output object and returns capabilities.

## Control Flow

Userspace opens an output, optionally inherits a firmware route or acquires an IOR, then issues protocol-specific methods. Many methods require `outp->ior` and validate the target head. DP training stores DPCD/LTTPR/link parameters into `outp->dp.lt` before invoking the backend train hook. HDMI disable clears infoframes and control before returning. HDA ELD toggles DP or HDMI audio and HDA HPD/ELD state. Release calls the output function's release hook and updates routing.

## State And Persistence Behavior

The file mutates `outp->acquired`, `outp->ior`, `outp->asy.head`, LVDS dual/bpc flags, cached DP DPCD/rates/LT state, MST IDs, AUX power, and audio/ELD hardware state through IOR hooks. The user object is embedded and single-open like other display child objects.

## Dependencies And Integration Points

It depends on output generic functions, DP helpers, head lookup, I2C/AUX backends, IOR HDMI/DP/HDA hooks, and NVIF output ABI structures. It is the main bridge between DRM userspace display management and nvkm display backend functions.

## Risks And Edge Cases

Most methods trust that acquire/inherit established `outp->ior`; callers must not issue acquired-only methods first. ABI size/version checks prevent struct drift. HDA ELD payload is capped at 0x60 bytes. DP rates are capped to the fixed output array. Infoframe sizes derive from `argc - sizeof(*args)` and must only be passed to generation hooks that support the requested type.

## Test Signals

Useful tests cover acquire/release on DAC/SOR/PIOR, inherit from firmware modes, EDID and load detection, backlight get/set, LVDS dual-link flags, HDMI enable/disable/infoframes/SCDC, HDA ELD hotplug, DP AUX transfers, training retries, SST timing, MST ID allocation, and VCPI programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/uoutp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/vga.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/vga.c

## Purpose

`vga.c` provides legacy VGA indexed register access helpers and VGA owner/lock control across pre-NV50 and NV50+ register layouts.

## Important APIs, Types, And Functions

`nvkm_rdport()` and `nvkm_wrport()` translate VGA port numbers to MMIO addresses, considering head selection and card generation. `nvkm_rdvgas()/wrvgas()`, `nvkm_rdvgag()/wrvgag()`, and `nvkm_rdvgac()/wrvgac()` access sequencer, graphics, and CRTC indexed registers. `nvkm_rdvgai()` and `nvkm_wrvgai()` dispatch based on index port. `nvkm_lockvgac()` locks or unlocks CRTC extended registers. `nvkm_rdvgaowner()` and `nvkm_wrvgaowner()` manage CR44-style VGA ownership across heads.

## Control Flow

Callers select a head and VGA port/index. The helper routes accesses through NV50 unified MMIO or legacy PRMVIO/PRMCIO ranges. Owner helpers are used around legacy VGA init/save/restore so the intended head owns shared 8-bit VGA I/O registers.

## State And Persistence Behavior

No software state is stored. The functions directly read and write VGA hardware registers, including lock state and CR44 owner state. `nvkm_lockvgac()` returns the previous lock state.

## Dependencies And Integration Points

The file depends on `subdev/vga.h`, `nvkm_device` MMIO helpers, card type/chipset detection, and legacy display init paths that require VGA register access.

## Risks And Edge Cases

Pre-NV40 head B PRMVIO access may require CR44 owner selection. NV11 has tied-head and lockup workarounds, including special CR reads/writes. Invalid ports return zero or no-op rather than errors. Lock/unlock register differs on NV50+.

## Test Signals

Signals include correct VGA state save/restore, no lockups on NV11, correct head-specific CRTC access on dual-head legacy chips, and stable text/VGA mode behavior around modesets and driver unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/vga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/Kbuild

## Purpose

`dma/Kbuild` lists the nouveau DMA object engine sources built into `nvkm-y`.

## Important APIs, Types, And Functions

It includes the generic engine (`base.o`), generation selectors (`nv04.o`, `nv50.o`, `gf100.o`, `gf119.o`, `gv100.o`), and user DMA object implementations (`user.o`, `usernv04.o`, `usernv50.o`, `usergf100.o`, `usergf119.o`, `usergv100.o`).

## Control Flow

There is no runtime control flow. Kernel build logic includes these objects so chipset constructors and NVIF DMA object classes are linked.

## State And Persistence Behavior

No runtime state is stored. The file controls compilation coverage and therefore which constructors can be referenced by the device table.

## Dependencies And Integration Points

It integrates with the parent nouveau Kbuild and the `nvkm-y` aggregate object list.

## Risks And Edge Cases

Missing one of these objects would cause link failures or unsupported DMA object creation for a GPU generation. Adding a new generation requires both implementation and Kbuild inclusion.

## Test Signals

Build success with all DMA constructors linked is the primary signal. Runtime signals are successful creation of NV_DMA_* classes across supported generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/base.c

## Purpose

`dma/base.c` implements the generic DMA object engine wrapper. It exposes NVIF DMA classes, forwards object construction to generation-specific encoders, and creates the engine.

## Important APIs, Types, And Functions

`nvkm_dma_oclass_new()` calls `dma->func->class_new()` and returns the embedded `nvkm_dmaobj` object. `nvkm_dma_sclass[]` exposes `NV_DMA_FROM_MEMORY`, `NV_DMA_TO_MEMORY`, and `NV_DMA_IN_MEMORY`. `nvkm_dma_oclass_base_get()` enumerates base-device classes, while `nvkm_dma_oclass_fifo_get()` enumerates FIFO child classes. `nvkm_dma_new_()` allocates `struct nvkm_dma`, stores the generation function table, and calls `nvkm_engine_ctor()`.

## Control Flow

Probe selects a generation constructor, which calls `nvkm_dma_new_()`. User/FIFO class enumeration returns DMA classes. A create request reaches `nvkm_dma_oclass_new()`, which invokes the generation `class_new` function to parse arguments and build a DMA object.

## State And Persistence Behavior

Persistent state is the `struct nvkm_dma` engine and its `func` pointer. Individual DMA object state is allocated in the user implementation files and persists as NVKM objects until destroyed.

## Dependencies And Integration Points

It depends on generic engine/object infrastructure, NVIF class IDs, and FIFO integration because DMA objects are commonly bound into channel RAMHT/RAMFC state.

## Risks And Edge Cases

The class arrays are ABI-visible; removing or reordering classes can break clients. `class_new` must set `*pobject` only when an object was successfully allocated enough to return. Enumeration functions return count when index is exhausted.

## Test Signals

Signals include class enumeration showing three DMA classes, successful DMA object creation through base and FIFO paths, and build/link coverage for every generation `class_new` function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gf100.c

## Purpose

`gf100.c` selects the GF100/Fermi DMA object encoder for the generic DMA engine.

## Important APIs, Types, And Functions

`gf100_dma` is a static `nvkm_dma_func` table with `.class_new = gf100_dmaobj_new`. `gf100_dma_new()` passes that table to `nvkm_dma_new_()`.

## Control Flow

Device probe for GF100-class chips calls `gf100_dma_new()`. Subsequent NVIF DMA object creation goes through generic `base.c` and lands in `gf100_dmaobj_new()`.

## State And Persistence Behavior

No extra state is introduced beyond the generic `struct nvkm_dma` function pointer. Per-object state is owned by `usergf100.c`.

## Dependencies And Integration Points

This file depends on `priv.h`, `user.h`, and the GF100 DMA object implementation.

## Risks And Edge Cases

The constructor must match the chipset's expected DMA object layout. Accidentally selecting NV50/GF119 encoders would produce invalid GPU object fields.

## Test Signals

Successful creation and binding of GF100 DMA objects, working push buffers/channels on Fermi, and no RAMFC/DMA-object faults are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gf119.c

## Purpose

`gf119.c` selects the GF119-generation DMA object encoder.

## Important APIs, Types, And Functions

`gf119_dma` sets `.class_new = gf119_dmaobj_new`. `gf119_dma_new()` constructs the generic DMA engine with that table.

## Control Flow

GF119-family probe uses `gf119_dma_new()`. DMA class creation then dispatches through `base.c` into `gf119_dmaobj_new()`.

## State And Persistence Behavior

Only the generation function pointer is persistent in the engine. Object-specific state is in `usergf119.c`.

## Dependencies And Integration Points

It depends on the generic DMA engine and GF119 user object encoder.

## Risks And Edge Cases

GF119 object layout differs from GF100 and later GV100 layouts; selecting the wrong table changes address and flag encoding.

## Test Signals

Look for successful DMA object bind into channels, valid pushbuffer operation, and no invalid target/kind errors during client startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gv100.c

## Purpose

`gv100.c` selects the GV100/Volta DMA object encoder.

## Important APIs, Types, And Functions

`gv100_dma` sets `.class_new = gv100_dmaobj_new`. `gv100_dma_new()` creates the generic DMA engine with the Volta encoder table.

## Control Flow

Volta-class probe calls `gv100_dma_new()`, and all DMA object class creation is forwarded through the generic engine to `gv100_dmaobj_new()`.

## State And Persistence Behavior

The file adds no state except the engine's function table. Per-object address and flag state is handled by `usergv100.c`.

## Dependencies And Integration Points

It integrates `priv.h`, `user.h`, generic DMA construction, and Volta DMA object binding.

## Risks And Edge Cases

GV100's encoder accepts only concrete memory targets in its user implementation. Mismatched generation selection can reject valid client requests or emit unusable descriptors.

## Test Signals

Successful channel setup on Volta/Turing-era paths using DMA objects and absence of `-EINVAL` from DMA target validation are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/nv04.c

## Purpose

`nv04.c` selects the legacy NV04 DMA object encoder.

## Important APIs, Types, And Functions

`nv04_dma` sets `.class_new = nv04_dmaobj_new`. `nv04_dma_new()` constructs the generic DMA engine for NV04-style DMA object descriptors.

## Control Flow

Legacy device probe calls `nv04_dma_new()`. Create requests for NV_DMA classes dispatch through generic DMA code into `nv04_dmaobj_new()`.

## State And Persistence Behavior

No private runtime state exists here. Object state is allocated in `usernv04.c`.

## Dependencies And Integration Points

It depends on the generic DMA engine and legacy user object encoder used by older FIFO/channel code.

## Risks And Edge Cases

Legacy DMA descriptors have special VM clone handling and target/access flag rules in `usernv04.c`; this selector must be paired with that layout only.

## Test Signals

Test by creating legacy DMA objects for VRAM/PCI targets, binding them into NV04/NV10/NV40 channels, and checking for valid memory access by push buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/nv50.c

## Purpose

`nv50.c` selects the NV50 DMA object encoder.

## Important APIs, Types, And Functions

`nv50_dma` sets `.class_new = nv50_dmaobj_new`. `nv50_dma_new()` constructs the generic DMA engine with NV50 descriptor encoding.

## Control Flow

NV50-generation probe calls `nv50_dma_new()`. DMA class creation dispatches through the generic engine into `nv50_dmaobj_new()`.

## State And Persistence Behavior

The file stores only the generation function table. Per-DMA object flags, limits, and bindings live in `usernv50.c`.

## Dependencies And Integration Points

It depends on `priv.h`, `user.h`, generic engine construction, and NV50 FIFO/channel use of DMA objects.

## Risks And Edge Cases

NV50 supports optional extra class arguments for kind/comp/priv/part; selecting a different encoder would misprogram class descriptors.

## Test Signals

Signals include successful NV50 channel creation, valid RAMHT binding, and DMA object creation with both default and explicit NV50 attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/priv.h

## Purpose

`dma/priv.h` defines private DMA engine and DMA object function-table contracts.

## Important APIs, Types, And Functions

`nvkm_dma(p)` converts an engine pointer to `struct nvkm_dma`. `struct nvkm_dmaobj_func` currently contains the `bind()` callback used to materialize a DMA object into a GPU object under a parent. `struct nvkm_dma_func` contains `class_new()`, the generation-specific NVIF constructor. `nvkm_dma_new_()` is declared for generation selectors.

## Control Flow

Generation constructors create the engine with an `nvkm_dma_func`. User object constructors create `nvkm_dmaobj` instances with an `nvkm_dmaobj_func`. Later object binding routes through `dmaobj->func->bind()`.

## State And Persistence Behavior

This header does not store state, but it defines the function pointers persisted in `struct nvkm_dma` and `struct nvkm_dmaobj`.

## Dependencies And Integration Points

It includes public `engine/dma.h` and is used by `base.c`, generation selectors, and user DMA object encoders.

## Risks And Edge Cases

The bind contract must return a GPU object whose layout matches the target generation and parent alignment requirements. Future fields must preserve all existing constructor call sites.

## Test Signals

Build coverage across all DMA files and successful bind callbacks during FIFO channel construction validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.c

## Purpose

`dma/user.c` implements generic NVIF DMA object parsing, object lifetime, search, and bind dispatch shared by all generation encoders.

## Important APIs, Types, And Functions

`nvkm_dmaobj_search()` looks up a client object by handle and verifies it uses the DMA object function table. `nvkm_dmaobj_bind()` dispatches to the generation `bind` callback. `nvkm_dmaobj_dtor()` returns the embedded object for freeing. `nvkm_dmaobj_ctor()` constructs the object, unpacks `nv_dma_v0`, stores target/access/start/limit, validates range ordering, and maps NVIF target/access enums to internal `NV_MEM_TARGET_*` and `NV_MEM_ACCESS_*`.

## Control Flow

A generation `*_dmaobj_new()` allocates its extended object, calls `nvkm_dmaobj_ctor()`, then parses any generation-specific tail arguments and computes descriptor flags. Later FIFO/channel code searches or binds the object through the generic function table.

## State And Persistence Behavior

The generic fields persisted in `struct nvkm_dmaobj` are `func`, `dma`, `target`, `access`, `start`, and `limit`. Generation files add descriptor-specific fields.

## Dependencies And Integration Points

It depends on NVIF class `cl0002`, unpack helpers, client object lookup, GPU object binding, and framebuffer memory target definitions.

## Risks And Edge Cases

The constructor rejects inverted ranges and unknown target/access values. `NV_DMA_V0_TARGET_VM` and `NV_DMA_V0_ACCESS_VM` are only meaningful for generations that support VM-style objects. Returning partially allocated objects on constructor failure must be cleaned by callers through normal object lifetime.

## Test Signals

Signals include ioctl traces for DMA creation, rejection of bad ranges/enums, successful handle lookup, and generation bind callbacks receiving normalized target/access values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.h

## Purpose

`dma/user.h` declares the shared DMA object constructor and all generation-specific DMA object constructors.

## Important APIs, Types, And Functions

`nvkm_dmaobj(p)` converts an NVKM object to `struct nvkm_dmaobj`. `nvkm_dmaobj_ctor()` performs generic parsing/normalization. `nv04_dmaobj_new()`, `nv50_dmaobj_new()`, `gf100_dmaobj_new()`, `gf119_dmaobj_new()`, and `gv100_dmaobj_new()` are the generation constructors selected by generation files.

## Control Flow

Generic DMA class creation calls a generation `class_new`, which is one of these declared constructors. Each generation constructor calls the shared constructor before adding layout-specific flags and bind behavior.

## State And Persistence Behavior

No state is stored in the header. It declares how generic and generation object state is initialized.

## Dependencies And Integration Points

It includes `priv.h` and is consumed by `base.c`, all generation selector files, and all user object encoders.

## Risks And Edge Cases

Prototype drift would break all generation constructors. The shared constructor mutates the data pointer and size, so generation-specific parsers must use the updated values.

## Test Signals

Build success across all DMA generations and successful parsing of both generic and generation-specific DMA create arguments validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf100.c

## Purpose

`usergf100.c` implements GF100/Fermi DMA object encoding and binding.

## Important APIs, Types, And Functions

`struct gf100_dmaobj` extends the generic DMA object with `flags0` and `flags5`. `gf100_dmaobj_bind()` creates a 24-byte GPU object and writes flags, limit/start low bits, packed high address bits, zero padding, and flags5. `gf100_dmaobj_new()` parses optional `gf100_dma_v0` tail arguments for kind and privilege, supplies defaults for VM or pitch objects, validates privilege, and encodes target/access bits.

## Control Flow

Creation calls the shared constructor first, then consumes optional GF100 arguments if present. With no tail args, non-VM targets default to pitch/user mode and VM targets default to VM/priv mode. Binding later emits the hardware descriptor into a parent GPU object.

## State And Persistence Behavior

Persistent per-object state is the normalized generic range/target/access plus `flags0` and `flags5`. The bound GPU object is separate and owned by the caller.

## Dependencies And Integration Points

It depends on NVIF GF100 DMA argument definitions, GPU object allocation, framebuffer target constants, and FIFO channel bind paths.

## Risks And Edge Cases

The access switch does not explicitly reject unknown access values after the known cases, so correctness relies on the shared constructor's normalization. Kind is not range-checked in this file beyond what userspace provides. The unknown `unkn` field defaults differently for VM and pitch paths.

## Test Signals

Test default VM/pitch object creation, explicit kind/priv arguments, target/access combinations, and correct channel operation after binding the 24-byte descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf119.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf119.c

## Purpose

`usergf119.c` implements GF119-style DMA object encoding.

## Important APIs, Types, And Functions

`struct gf119_dmaobj` stores generic state plus `flags0`. `gf119_dmaobj_bind()` creates a 24-byte descriptor with flags and 256-byte shifted start/limit. `gf119_dmaobj_new()` parses optional `gf119_dma_v0` kind/page fields, supplies pitch/small-page defaults for real targets and VM/large-page defaults for VM targets, validates page, and encodes VRAM target bits.

## Control Flow

Generic parsing normalizes target/access/range. GF119-specific parsing sets kind and page, then target encoding either marks VRAM or leaves VM/PCI/PCI_NOSNOOP as placeholder-style descriptors used mainly for push buffers. Binding materializes the descriptor into channel memory.

## State And Persistence Behavior

The object persists `flags0` and the generic address range. Start and limit are stored in the descriptor shifted by 8 bits.

## Dependencies And Integration Points

It depends on NVIF GF119 DMA arguments, GPU object helpers, and FIFO/channel users that understand GF119 descriptor semantics.

## Risks And Edge Cases

The file explicitly notes that real PCI/VM descriptors are not fully understood and are used as placeholders for push buffers. Access flags are not encoded here the way older generations do, so callers must not expect full access control from this descriptor.

## Test Signals

Signals include successful pushbuffer DMA object creation for VM/PCI targets, VRAM descriptor operation, page validation errors for invalid input, and no channel setup failures on GF119-era GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergf119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergv100.c

## Purpose

`usergv100.c` implements GV100/Volta DMA object encoding and binding.

## Important APIs, Types, And Functions

`struct gv100_dmaobj` stores generic state plus `flags0`. `gv100_dmaobj_bind()` emits a 24-byte descriptor with flags and separate low/high dwords for start and limit, both shifted by 8. `gv100_dmaobj_new()` reuses the GF119 argument shape for kind/page, coerces them to booleans, defaults to small-page pitch-like settings when no tail is provided, sets read/write, and encodes VRAM/PCI/PCI_NOSNOOP targets.

## Control Flow

The shared constructor parses generic arguments. GV100-specific parsing sets optional kind/page bits. Binding creates the GPU object descriptor used by later channel setup.

## State And Persistence Behavior

Persistent state is the normalized address range/target plus `flags0`. Unlike GF119, GV100 requires concrete VRAM or PCI targets and rejects VM.

## Dependencies And Integration Points

It depends on GPU object allocation, NVIF DMA argument structures, and Volta+ FIFO/channel paths.

## Risks And Edge Cases

VM targets are rejected here; clients expecting GF119 placeholder behavior will fail. Kind/page inputs are booleanized rather than preserving full numeric values. Address encoding assumes 256-byte granularity.

## Test Signals

Test VRAM/PCI/PCI_NOSNOOP object creation, rejection of VM targets, descriptor binding, and successful channel pushbuffer operation on GV100-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usergv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv04.c

## Purpose

`usernv04.c` implements legacy NV04 DMA object encoding, including special VM clone behavior for old MMUs.

## Important APIs, Types, And Functions

`struct nv04_dmaobj` stores generic state, `clone`, `flags0`, and `flags2`. `nv04_dmaobj_bind()` emits a 16-byte descriptor with class/target/access flags, length, and offset; in clone mode it can wrap the legacy page table or read a page-table entry to derive the physical offset. `nv04_dmaobj_new()` normalizes generic arguments, converts VM targets to PCI/RW on NV04 MMU, selects target flags, and encodes access flags.

## Control Flow

Creation calls the shared constructor, handles VM target special cases, computes flags from target/access, and returns the object. Binding later allocates or wraps a GPU object descriptor and writes the legacy DMA object fields.

## State And Persistence Behavior

The object persists clone mode and descriptor flags. In clone mode, binding may depend on the current legacy MMU page table contents.

## Dependencies And Integration Points

It depends on GPU object helpers, framebuffer target constants, legacy MMU/VMM structures, and channel code that consumes 16-byte DMA descriptors.

## Risks And Edge Cases

The length is computed as `limit - start`, matching legacy descriptor expectations; off-by-one assumptions must not be changed without hardware validation. Clone mode reads page table entries and assumes the old MMU layout. Write-only access falls through to set writable bits.

## Test Signals

Signals include successful VRAM/PCI/PCI_NOSNOOP descriptors, VM clone descriptors on NV04 MMU, correct access enforcement, and working legacy FIFO push buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv50.c

## Purpose

`usernv50.c` implements NV50 DMA object encoding and binding.

## Important APIs, Types, And Functions

`struct nv50_dmaobj` stores generic state plus `flags0` and `flags5`. `nv50_dmaobj_bind()` creates a 24-byte descriptor with flags, low start/limit, packed high start/limit, zero padding, and partition flags. `nv50_dmaobj_new()` parses optional `nv50_dma_v0` fields for privilege, partition, compression, and kind; supplies defaults for non-VM and VM targets; validates field ranges; and encodes target/access bits.

## Control Flow

Creation starts with generic parsing, then consumes optional NV50-specific tail data. If no tail exists, defaults depend on whether the target is VM. Binding materializes the descriptor into a parent GPU object, commonly under a channel instance block.

## State And Persistence Behavior

Persistent per-object state is generic target/access/range plus encoded flags. The bound descriptor is transient with the caller's GPU object hierarchy.

## Dependencies And Integration Points

It depends on NVIF `nv50_dma_v0`, GPU object allocation, framebuffer target constants, and NV50 FIFO/channel RAMFC paths.

## Risks And Edge Cases

Field range checks reject priv > 2, part > 2, comp > 3, or kind > 0x7f. Access VM is allowed without extra flags, while RO/WO/RW set specific bits. VM defaults use VM partition/compression/kind values and must match hardware expectations.

## Test Signals

Test default and explicit NV50 DMA object creation, invalid tail field rejection, descriptor bind layout, and successful NV50/G8x channel setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/dma/usernv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/falcon.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/falcon.c

## Purpose

`falcon.c` implements the shared engine wrapper for NVIDIA Falcon microcontroller-based engines. It handles class enumeration, engine context object binding, interrupt handling, firmware discovery/loading, IMEM/DMEM upload, boot, shutdown, and construction.

## Important APIs, Types, And Functions

`nvkm_falcon_oclass_get()` enumerates engine-specific supported classes. `nvkm_falcon_cclass_bind()` allocates a 256-byte context object. `nvkm_falcon_intr()` decodes Falcon interrupt status, looks up the current channel by instance address, dispatches engine-specific interrupts, logs halted microcode, and acks bits. `nvkm_falcon_oneinit()` detects Falcon version, secret level, and code/data limits. `nvkm_falcon_init()` waits for secure halt where needed, loads internal or external firmware, allocates core memory for self-bootstrapping firmware, uploads code/data through old or new Falcon register interfaces, zeros remaining DMEM, starts execution, and calls an optional engine init hook. `nvkm_falcon_fini()` disables FIFO/CHSW and frees poweroff-only resources. `nvkm_falcon_new_()` constructs the engine.

## Control Flow

Engine-specific code calls `nvkm_falcon_new_()` with firmware blobs or empty firmware pointers. Oneinit records hardware caps. Init first handles secure/halt state, disables interrupts, tries a self-bootstrapping firmware file, then split data/code firmware files, copies firmware into memory or Falcon IMEM/DMEM, starts execution, and enables FIFO/CHSW. Interrupts map Falcon instance state back to a FIFO channel and delegate engine-specific work before acking.

## State And Persistence Behavior

`struct nvkm_falcon` persists function pointers, MMIO base, version/secret/cap limits, code/data buffers, external-firmware ownership, and optional core memory. External firmware vmalloc buffers are freed on poweroff. Core memory is also released on poweroff.

## Dependencies And Integration Points

It depends on generic engine construction, firmware loader, GPU object/memory helpers, MC enable checks, timer polling, FIFO channel lookup, and engine-specific Falcon function tables.

## Risks And Edge Cases

Firmware loading has multiple fallback names and can fail with `-ENODEV`. Code/data sizes are checked against hardware limits only for direct upload. External self-bootstrapping images are copied to instance memory and programmed through bootstrap registers. Interrupt handling must tolerate no channel lookup. Poweroff cleanup must only free externally owned buffers.

## Test Signals

Signals include firmware load logs identifying self-bootstrapping or split images, Falcon version/limit debug output, no `ucode exceeds falcon limits` errors, handled engine-specific interrupts, clean halted microcode acks, and successful suspend/resume or poweroff reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/falcon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/Kbuild

## Purpose

`fifo/Kbuild` lists all nouveau FIFO engine sources built into `nvkm-y`.

## Important APIs, Types, And Functions

It includes shared infrastructure (`base.o`, `cgrp.o`, `chan.o`, `chid.o`, `runl.o`, `runq.o`), legacy through modern generation backends (`nv04.o` through `gb202.o`), and user object wrappers (`ucgrp.o`, `uchan.o`).

## Control Flow

There is no runtime control flow. The build system uses this list so all referenced FIFO generation constructors and shared helpers are linked.

## State And Persistence Behavior

No runtime state is stored. The file controls build-time availability.

## Dependencies And Integration Points

It integrates with the parent nouveau Kbuild and the full FIFO subsystem.

## Risks And Edge Cases

Omitting a backend can cause link failures or missing support for a chipset. New generation support must add implementation and Kbuild entries together.

## Test Signals

Kernel build success and successful probe across FIFO generations are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/base.c

## Purpose

`fifo/base.c` implements the generic FIFO engine lifecycle, class exposure, runlist/runqueue setup, interrupt/event registration, USERD allocation, engine info queries, pause/start/fault wrappers, and teardown.

## Important APIs, Types, And Functions

`nvkm_fifo_ctxsw_in_progress()` checks engine context-switch state across runlists. `nvkm_fifo_pause()`, `nvkm_fifo_start()`, and `nvkm_fifo_fault()` dispatch generation callbacks. `nvkm_fifo_class_new()` routes user class creation to channel-group or channel constructors. `nvkm_fifo_info()` answers NV_DEVICE_HOST channel/runlist/engine queries. `nvkm_fifo_oneinit()` creates global or per-runlist CHID allocators, runqueues, runlists, interrupt handlers, nonstall events, and shared USERD BAR1 memory. `nvkm_fifo_init()` initializes PBDMAs, runqueues, runlists, generation state, and enables interrupts. `nvkm_fifo_fini()` blocks interrupts and finalizes runlists. `nvkm_fifo_new_()` initializes the engine object and locks.

## Control Flow

Generation probe calls `nvkm_fifo_new_()`. Oneinit creates scheduler structures and events based on the generation `nvkm_fifo_func`. Runtime init programs runqueues/runlists and enables interrupts. User class enumeration exposes channel-group and channel classes. Teardown frees USERD mappings, runlists, runqueues, CHID/CGID allocators, nonstall events, and generation private state.

## State And Persistence Behavior

Persistent FIFO state includes function table, runqueue/runlist lists, global CHID/CGID allocators, nonstall event, USERD memory and BAR1 VMA, locks, mutex, and timeout defaults. Runlist/channel state persists in child objects.

## Dependencies And Integration Points

It depends on MC interrupts, BAR1 VMM, MMU memory, GPU object helpers, runlist/runqueue/channel/group helpers, NVIF host info constants, and generation FIFO tables.

## Risks And Edge Cases

USERD allocation assumes global `fifo->chid` exists for BAR1-backed USERD generations. `nvkm_fifo_info()` must distinguish global and per-runlist CHID designs. Interrupt registration and nonstall event counts depend on generation callbacks. Teardown must block interrupt sources before freeing runlists.

## Test Signals

Signals include correct NV_DEVICE_HOST query results, successful channel/group class creation, runlist updates after channel insert/remove, nonstall event delivery, no USERD mapping leaks, and clean suspend/resume init/fini cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.c

## Purpose

`cgrp.c` implements FIFO channel-group state: group lifetime, CGID allocation, shared engine contexts, VMM-specific subcontexts, reference management, and recovery state initialization.

## Important APIs, Types, And Functions

`nvkm_cgrp_ectx_get()/put()` manage per-engine group contexts. `nvkm_cgrp_vctx_get()/put()` manage per-engine plus VMM subcontexts, including VMM engine reference counts, instance object allocation, and engine-specific constructor/bind hooks. `nvkm_cgrp_new()` allocates a group, references the VMM, optionally allocates a CGID, and initializes lists/locks. `nvkm_cgrp_ref()`, `nvkm_cgrp_unref()`, and `nvkm_cgrp_put()` manage krefs and IRQ-lock release.

## Control Flow

Channel creation either joins an existing group or creates a private group. When a channel needs an engine context, it asks the group for a vctx; the group reuses an existing engine/VMM context or creates ectx then vctx, invoking engine callbacks to allocate hardware context. Destruction unwinds vctx, ectx, VMM refs, instance objects, and CGID allocation.

## State And Persistence Behavior

Persistent group state includes name, runlist, VMM reference, hardware-group flag, id, channel list/count, ectx/vctx lists, mutex, IRQ lookup lock, recovery atomic state, and kref. Vctx objects persist VMM refs, GPU object instance/VMA, ectx references, and VMM engine reference increments.

## Dependencies And Integration Points

It depends on runlist CHID/CGID allocators, channel code, engine context constructors, MMU/VMM reference tracking, GPU object binding, and channel-group user objects.

## Risks And Edge Cases

Reference balance is subtle across cctx/vctx/ectx layers. Failure after list insertion must call the matching put path. CGID allocation can fail with `-ENOSPC`. VMM engine reference counts must be decremented exactly once to keep TLB invalidation logic correct.

## Test Signals

Signals include successful channel-group creation, shared context reuse across channels in a group, VMM-specific context separation, CGID exhaustion handling, and no leaked VMM engrefs or GPU objects after channel/group destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.h

## Purpose

`cgrp.h` defines FIFO channel-group, engine-context, and VMM-context data structures plus group helper prototypes.

## Important APIs, Types, And Functions

`struct nvkm_vctx` tracks a VMM-specific subcontext, instance GPU object, VMA, and ectx reference. `struct nvkm_ectx` tracks an engine-level group context and backing object. `struct nvkm_cgrp` stores function table, name, runlist, VMM, hardware group flag, id, kref, channel list/count, lookup lock, context lists, mutex, recovery state, and runlist list node. The header declares group creation/ref/unref, vctx get/put, IRQ lock put, channel iteration macros, and logging macros.

## Control Flow

Channel creation and engine bind paths use these structures to share contexts across channels. Recovery and preemption paths consult the group function table and `rc` state.

## State And Persistence Behavior

The header defines all persistent group state. `rc` tracks none/pending/running recovery states. `chans`, `ectxs`, and `vctxs` are lifetime-managed lists.

## Dependencies And Integration Points

It includes core OS helpers and is used by FIFO channel, runlist, generation backends, and user channel-group code.

## Risks And Edge Cases

The `lock` protects IRQ handler channel/group lookup, while `mutex` protects context lists; mixing them incorrectly risks deadlock or stale lookups. Group `id` may be a CGID or fall back to a channel id depending on hardware.

## Test Signals

Build integration plus runtime context reuse, group preemption, recovery state transitions, and correct logs with group ids validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/cgrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.c

## Purpose

`chan.c` implements FIFO channel lifetime, context binding, preemption, runlist insertion/removal, error/block/allow state, channel lookup by instance or CHID, USERD setup, RAMFC setup, and resource teardown.

## Important APIs, Types, And Functions

`nvkm_chan_cctx_get()/put()` manage per-channel context references to group vctxs. `nvkm_chan_cctx_bind()` blocks scheduling, preempts, updates engine binding, and resumes scheduling. `nvkm_chan_preempt()` and `_locked()` call generation preempt hooks and optionally wait. `nvkm_chan_insert()` and `nvkm_chan_remove()` maintain runlist/channel-group lists and trigger runlist updates. `nvkm_chan_error()` marks a channel errored, blocks it, optionally preempts, and notifies CHID events. `nvkm_chan_allow()` and `nvkm_chan_block()` maintain a block refcount. `nvkm_chan_get_inst()` and `nvkm_chan_get_chid()` locate channels for IRQ handlers. `nvkm_chan_new_()` validates arguments, creates or joins a group, allocates instance memory, joins VMM, binds push DMA objects, allocates CHID/USERD, clears USERD, and writes RAMFC.

## Control Flow

User channel creation calls a generation wrapper that ends in `nvkm_chan_new_()`. The channel starts blocked until inserted and allowed. When inserted, runlist state is updated under the runlist mutex. Engine context binding safely removes the channel or group from scheduling, preempts, updates context pointers, and allows scheduling. Errors from runqueue/runlist interrupts mark the channel disabled and notify clients.

## State And Persistence Behavior

`struct nvkm_chan` persists function table, name, runqueue, CHID, block/error atomics, context list, group reference, instance object, optional VMM reference, push object, RAMFC/cache/eng/pgd/RAMHT objects, USERD memory/base, and runlist membership. USERD may be caller-supplied or FIFO-managed.

## Dependencies And Integration Points

It depends on channel-group context management, CHID allocators, runlist update/preempt helpers, DMA object binding, MMU/VMM join/part, GPU object and RAMHT helpers, NVIF channel ABI, and generation `nvkm_chan_func` tables.

## Risks And Edge Cases

Argument validation is dense and generation-dependent. Partial creation failures rely on caller cleanup through `nvkm_chan_del()`. USERD bounds checks must prevent mapping past supplied memory. Blocking uses a refcount, so unmatched allow/block calls can leave channels stopped or running too early. Error notification requires holding the right lookup locks.

## Test Signals

Signals include successful channel creation for private and grouped channels, correct CHID allocation/release, USERD writes visible to clients, runlist updates after insert/remove, preemption wait success, channel error events on injected faults, and no leaked VMM joins or GPU objects after destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.h

## Purpose

`chan.h` defines FIFO channel and channel-context function-table contracts and helper prototypes.

## Important APIs, Types, And Functions

`struct nvkm_cctx` tracks a channel's reference to a group/VMM engine context. `struct nvkm_chan_func` describes generation-specific instance block, USERD, RAMFC, bind/unbind/start/stop/preempt, and doorbell behavior. Nested structs describe instance memory size/zero/VMM requirements, USERD BAR/base/size/clear hook, and RAMFC layout/write/clear/ctxdma/devm/priv requirements. The header declares channel creation/destruction, allow/block/error, insert/remove, preempt, context get/put/bind, and logging macros.

## Control Flow

Generation backends fill an `nvkm_chan_func`; user channel constructors pass it to `nvkm_chan_new_()`. Runtime scheduling, error, and context paths call the optional hooks according to this contract.

## State And Persistence Behavior

The header defines how persistent channel state is initialized and what hardware resources it owns: instance, USERD, RAMFC, optional push DMA, and context objects.

## Dependencies And Integration Points

It includes public FIFO engine definitions and is consumed by shared channel code, generation FIFO files, runlist code, and user channel wrappers.

## Risks And Edge Cases

Boolean requirements in `nvkm_chan_new_()` are driven by these nested fields; inconsistent generation tables reject valid channels or accept invalid ones. Optional `preempt` and `doorbell_handle` must be checked by callers.

## Test Signals

Build coverage and successful channel creation across generations validate the prototypes. Runtime tests should cover both ctxdma and non-ctxdma RAMFC paths, BAR1 and supplied USERD, and privileged channel rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.c

## Purpose

`chid.c` implements the CHID/CGID allocator used by FIFO runlists and channel groups, including event initialization and id-to-data lookup storage.

## Important APIs, Types, And Functions

`nvkm_chid_new()` allocates the flexible bitmap structure, initializes kref, mask, lock, data array, reserves ids outside the allowed range, and initializes an event source. `nvkm_chid_get()` finds the first free id, marks it used, and stores caller data. `nvkm_chid_put()` clears data under the caller's data lock and releases the bit. `nvkm_chid_ref()` and `nvkm_chid_unref()` manage lifetime; the destructor finalizes events and frees arrays.

## Control Flow

FIFO oneinit creates allocators globally or per runlist. Channel and group constructors call get. Destructors call put. Interrupt handlers use the stored data arrays through runlist helpers while respecting locks. Event notification, such as channel error, uses the allocator's event source.

## State And Persistence Behavior

The allocator persists a bitmap of used ids, a data pointer per id, a mask usually `nr - 1`, a spinlock, kref, and event object. Ids before `first` and after `first + count` are permanently reserved.

## Dependencies And Integration Points

It depends on core event helpers and is used by FIFO base, runlist, channel, channel-group, and event notification paths.

## Risks And Edge Cases

`mask = nr - 1` assumes hardware-friendly id counts, commonly powers of two. `nvkm_chid_put()` takes both allocator and data locks; callers must pass the correct lookup lock. Exhaustion returns `-1` and must become `-ENOSPC` in callers.

## Test Signals

Signals include correct id exhaustion/reuse, reserved range enforcement, channel error event delivery, no stale data pointer after put, and no use-after-free under interrupt lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.h

## Purpose

`chid.h` defines the FIFO channel-id allocator structure and API.

## Important APIs, Types, And Functions

`struct nvkm_chid` contains a kref, id count, mask, event source, id-to-data array, spinlock, and flexible used bitmap. The header declares create/ref/unref/get/put helpers.

## Control Flow

FIFO setup creates allocators. Channel/group creation gets ids, interrupt lookup reads data, and destruction puts ids. Event users subscribe to `chid->event`.

## State And Persistence Behavior

Persistent state is the used bitmap, data array, event object, and kref. The mask is used by hardware status decoding paths to bound CHID values.

## Dependencies And Integration Points

It includes `core/event.h` and is consumed by FIFO base, runlists, channels, and groups.

## Risks And Edge Cases

The flexible array allocation must match `nr`. Callers must not use an id after `put` clears its data pointer. Non-power-of-two `nr` values may make `mask` unsuitable for some hardware decodes.

## Test Signals

Build coverage, CHID allocation/release, event delivery, and interrupt lookup correctness validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/chid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/g84.c

## Purpose

`g84.c` implements the G84/G82 FIFO backend: channel RAMFC construction, engine context binding, nonstall interrupt event control, runlist composition, and the generation FIFO function table.

## Important APIs, Types, And Functions

`g84_chan_bind()` writes a channel RAMFC pointer into the channel table. `g84_chan_ramfc_write()` allocates engine, page-directory, cache, RAMFC, and RAMHT GPU objects, then writes the G84 RAMFC fields including push offset/limit, device mask, RAMHT pointer, cache pointer, and instance pointer. `g84_chan` combines NV50 instance/USERD helpers with G84 RAMFC and NV50 start/stop/unbind. `g84_ectx_bind()` updates per-engine context pointers in the channel engine object and can kick hardware to unbind. `g84_fifo_nonstall` masks/unmasks the nonstall bit. `g84_fifo_runl_ctor()` creates one runlist and adds SW, DMAOBJ, GR, MPEG, ME, VP, CIPHER, and BSP engines. `g84_fifo_new()` constructs the backend.

## Control Flow

Probe installs `g84_fifo`. FIFO oneinit creates CHIDs and the single runlist. Channel creation uses `g84_chan_ramfc_write()` and then insertion updates the runlist. Engine context binding blocks/preempts through shared channel code, then `g84_ectx_bind()` rewrites context descriptors.

## State And Persistence Behavior

G84 channels persist allocated RAMFC/RAMHT/cache/PGD/engine objects under the channel instance. Nonstall event state is controlled by a hardware mask bit. Runlist topology is static.

## Dependencies And Integration Points

It depends on NV50 channel helpers, NV04 interrupt/pause/start, NV50 runlist and engine object RAMHT helpers, timer polling, RAMHT allocation, and NVIF `G82_CHANNEL_GPFIFO`.

## Risks And Edge Cases

`ilog2(length / 8)` assumes valid pushbuffer length. Engine type mapping in `g84_ectx_bind()` must match hardware pointer slots. The unbind path polls a register but does not error on timeout in this snippet. Nonstall masking is protected by `fifo->lock`.

## Test Signals

Signals include successful G82 channel creation, valid RAMHT entries, context switches across GR/video engines, nonstall event delivery, and no FIFO interrupt errors under G84 workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/g98.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/g98.c

## Purpose

`g98.c` defines the G98 FIFO variant, mainly changing runlist engine composition while reusing the G84 channel and engine machinery.

## Important APIs, Types, And Functions

`g98_fifo_runl_ctor()` creates one runlist with SW, DMAOBJ, GR, MSPPP, CE, MSPDEC, SEC, and MSVLD engines. `g98_fifo` reuses NV50 CHID/init/runlist helpers, NV04 interrupt/pause/start, G84 nonstall, G84 engine binding, NV50 software engine handling, NV04 channel-group behavior, and G84 channel functions. `g98_fifo_new()` constructs the backend.

## Control Flow

Probe installs `g98_fifo`. Oneinit creates the G98-specific runlist. Channel creation and scheduling use the reused G84/NV50 helpers.

## State And Persistence Behavior

No private state beyond the generic FIFO/runlist/channel objects. The static runlist topology differs from G84.

## Dependencies And Integration Points

It depends on `priv.h`, `chan.h`, `runl.h`, G84 exported helpers, NV50 common helpers, and NVIF `G82_CHANNEL_GPFIFO`.

## Risks And Edge Cases

Wrong engine mapping would route contexts to the wrong video/copy engines. Reused G84 channel functions must remain compatible with G98 RAMFC hardware.

## Test Signals

Signals include successful channel creation, GR/CE/video engine scheduling on G98, correct NV_DEVICE_HOST_RUNLIST_ENGINES reporting, and no context bind errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/g98.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ga100.c

## Purpose

`ga100.c` implements the Ampere GA100 FIFO backend. It provides channel doorbells and RAMFC setup, forced hardware channel groups, engine context support, runqueue interrupt handling, runlist MMIO programming and interrupts, nonstall event wiring through VFN vectors, runlist discovery from TOP, and optional GSP/R535 construction.

## Important APIs, Types, And Functions

Channel functions include `ga100_chan_doorbell_handle()`, `ga100_chan_start()`, `ga100_chan_stop()`, `ga100_chan_unbind()`, `ga100_chan_ramfc_write()`, and `ga100_chan`. Group support is `ga100_cgrp_preempt()` and `ga100_cgrp`. Engine functions `ga100_engn` and `ga100_engn_ce` provide nonstall vector lookup, current context id decoding, constructors, and GV100 bind hooks. Runqueue support includes `ga100_runq_init()`, `ga100_runq_intr_0()`, `ga100_runq_intr_1()`, `ga100_runq_intr()`, and `ga100_runq_idle()`. Runlist support includes preempt/block/allow/pending/commit/init/fini callbacks, `ga100_runl_intr()`, and `ga100_runl_new()`. Nonstall support is handled by `ga100_fifo_nonstall_ctor()` and `_dtor()`. `ga100_fifo_runl_ctor()` discovers runlists from TOP. `ga100_fifo_new()` chooses R535/GSP or classic construction.

## Control Flow

Probe installs `ga100_fifo` or diverts to `r535_fifo_new()` under GSP-RM. Oneinit discovers runlists by TOP runlist address; each runlist reads channel config, runqueue config, doorbell config, interrupt vector, and engine membership. Nonstall construction queries the first engine in each runlist and registers vector interrupts. Runtime init submits a NULL runlist, preempts, enables doorbells, configures runlist and runqueue interrupt masks, and allows runlist interrupts. Channel creation writes RAMFC data directly into the instance block and uses internal doorbells to start. Interrupts decode runlist status, context-switch timeout info, runqueue faults, CTXNOTVALID, and channel errors.

## State And Persistence Behavior

Persistent state lives in generic FIFO/runlist/runqueue/channel/group objects. GA100 fills runlist MMIO base, channel table base, doorbell id, nonstall vector, runqueue list, and engine list from hardware discovery. Channels persist instance RAMFC fields including nonstall vector, device mask, privilege, and CHID. Channel groups are forced even for clients not explicitly using TSGs.

## Dependencies And Integration Points

It depends on TOP device enumeration, VFN interrupt vectors, GSP detection, TU102 MMU fault handling, GK110 preempt, GK104/GV100 engine context constructors/binders, GV100 runlist insertion helpers, runqueue infrastructure, and NVIF Ampere/Kepler channel-group classes.

## Risks And Edge Cases

TOP discovery can skip invalid runlists but must still leave a coherent FIFO. Runqueue interrupt masks are broad and many statuses result in channel disable/preempt. Current-context decoding depends on hardware status state and `nvkm_engine_chsw_load()`. Nonstall vector `-1` means absent, while other negatives are fatal. Doorbell programming assumes GFID 0 in this code. Runlist deletion after partial construction must clean registered interrupts.

## Test Signals

Signals include discovered runlists/engines, successful channel-group and channel creation, valid doorbell handles, runqueue idle detection, nonstall events per runlist, context-switch timeout logs with engine info, channel error events on fault injection, and working classic and GSP-backed probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ga102.c

## Purpose

`ga102.c` defines the GA102 FIFO variant by reusing GA100 Ampere FIFO machinery with a separate function table and GSP-aware constructor.

## Important APIs, Types, And Functions

`ga102_fifo` uses `ga100_fifo_runl_ctor`, TU102 MMU fault handling, GA100 nonstall ctor/dtor/event, GA100 runlist/runqueue functions, GA100 engine and copy-engine functions, forced GA100 channel groups, and GA100 Ampere GPFIFO channels. `ga102_fifo_new()` chooses R535/GSP construction when needed or classic `nvkm_fifo_new_()`.

## Control Flow

Probe calls `ga102_fifo_new()`. The remainder of oneinit/init/channel/interrupt flow is inherited from GA100 helper functions.

## State And Persistence Behavior

No private state is added. Generic FIFO structures are populated by GA100 discovery and callbacks.

## Dependencies And Integration Points

It depends on GA100 exported helpers, TU102 fault handling, GSP detection, and NVIF Ampere classes.

## Risks And Edge Cases

Although GA102 shares GA100 logic here, hardware differences must still be compatible with TOP discovery, runlist MMIO layout, and channel RAMFC fields. Wrong GSP selection would conflict with RM-managed FIFO.

## Test Signals

Signals include successful GA102 probe in GSP and non-GSP modes, channel creation, runlist interrupts, nonstall events, and fault recovery through TU102 fault hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gb202.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gb202.c

## Purpose

`gb202.c` provides a GB202-specific channel doorbell handle format.

## Important APIs, Types, And Functions

`gb202_chan_doorbell_handle()` returns `BIT(30) | (runlist id << 16) | channel id`, using the channel's group runlist id and CHID.

## Control Flow

Generation channel function tables can use this callback when exposing a doorbell handle to clients or channel setup code. It does not construct an engine by itself.

## State And Persistence Behavior

No state is stored. The function derives its value from persistent channel, channel-group, and runlist state.

## Dependencies And Integration Points

It depends on channel, channel-group, and runlist structures from FIFO private headers. It is intended for newer Blackwell-family FIFO code that needs a different doorbell namespace from GA100.

## Risks And Edge Cases

The format assumes runlist id and CHID fit in the encoded fields and that bit 30 selects the correct doorbell address space. Using GA100's format on GB202 or vice versa would ring the wrong doorbell.

## Test Signals

Signals include correct userspace-visible doorbell handles, successful channel kick through doorbells, and no scheduling stalls due to wrong runlist/channel encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/fifo/gb202.c -->
