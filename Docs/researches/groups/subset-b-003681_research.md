# subset-b-003681 Nouveau NVKM graphics and video engine research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/mcp79.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/mcp79.c

Purpose: MCP79 graphics-engine descriptor for NV50-family integrated chipsets. It does not implement new control flow; it binds the common `nv50_gr_init`, `nv50_gr_intr`, `nv50_gr_chan_new`, and `nv50_gr_units` hooks into a chip-specific `nvkm_gr_func`.

Important APIs/types/functions: `mcp79_gr_new()` calls `nv50_gr_new_()`. The static `mcp79_gr` function table exposes object classes `NV_NULL_CLASS`, `NV50_TWOD`, `NV50_MEMORY_TO_MEMORY_FORMAT`, `NV50_COMPUTE`, and `GT200_TESLA`, all using `nv50_gr_object`.

Control flow/state: creation is constructor-only: allocate/initialize common NV50 GR state in `nv50_gr_new_()`, then runtime state is managed by shared NV50 context and interrupt code. No persistent state is local to this file.

Dependencies/integration: depends on `nv50.h` and `nvif/class.h`; selected from chipset dispatch elsewhere in Nouveau. Risks are class-table omissions or wrong class IDs, which would surface as userspace channel/object creation failures. Test signals are successful engine probe, object allocation for the listed classes, and NV50 interrupt/init tests on MCP79 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/mcp79.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/mcp89.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/mcp89.c

Purpose: MCP89 graphics-engine descriptor for a later NV50/GT21x integrated chipset. It reuses the common NV50 engine implementation while adding the MCP89 class exposure and TLB flush behavior.

Important APIs/types/functions: `mcp89_gr_new()` delegates to `nv50_gr_new_()`. `mcp89_gr` uses `nv50_gr_init`, `nv50_gr_intr`, `nv50_gr_chan_new`, `g84_gr_tlb_flush`, and `nv50_gr_units`. Supported classes include `NV50_COMPUTE`, `GT214_COMPUTE`, and `GT21A_TESLA`.

Control flow/state: no local mutable state; all state is owned by `struct nv50_gr` and the shared GR engine. The `tlb_flush` hook is the only behavior difference from MCP79 and integrates with VM/cache maintenance.

Dependencies/integration: depends on `nv50.h`, `nvif/class.h`, and the G84 flush helper declared through NV50 headers. Risks are stale translations if `g84_gr_tlb_flush` is wrong for this chipset, or class exposure mismatches. Test signals include VM fault-free channel execution after buffer remaps and successful object creation for GT214/GT21A classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/mcp89.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv04.c

Purpose: first-generation NV04 PGRAPH implementation. It provides software object binding, manual context save/restore, interrupt decoding, and engine initialization for old GPUs whose hardware lacks later context and validation support.

Important APIs/types/functions: `nv04_gr_new()` constructs the engine via `nvkm_gr_ctor`. `nv04_gr_object_bind()` creates 16-byte graphics object records. `nv04_gr_chan_new()`, `nv04_gr_chan_fini()`, and `nv04_gr_chan_dtor()` manage `struct nv04_gr_chan`, which stores a full MMIO context image in `nv04[]`. `nv04_gr_intr()` handles notify/context-switch interrupts and calls `nv04_gr_mthd()` for software-emulated illegal methods. `nv04_gr_idle()` is exported for later generations.

Control flow/state: channels are indexed in `struct nv04_gr::chan[16]` under `spinlock_t lock`. On context-switch interrupt, FIFO is acknowledged, the current channel context is read from `nv04_gr_ctx_regs`, the target channel is selected from trapped address bits, and its saved register image is written back. Object methods update synthetic valid bits in GPU object memory at `0x700000 + inst`, then mirror relevant values into current PGRAPH context/cache registers.

Dependencies/integration: uses core object/gpuobj helpers, FIFO channel IDs, instmem-style object address space, timer polling, and register definitions from `regs.h`. It exposes many legacy 2D/3D class IDs via `nv04_gr.sclass`.

Risks/test signals: high risk lies in hand-maintained register lists, big-endian object bits, trapped-method decoding, and lock ordering around interrupt/fini paths. Test via NV04/NV05 channel switching, 2D object binding combinations, illegal-method recovery, FIFO progress after context switches, and absence of PGRAPH timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv10.c

Purpose: NV10/NV1x graphics implementation. It extends NV04 with larger register context, software pipe-state save/restore, LMA window method emulation for NV17 Celsius, tile programming, and interrupt handling.

Important APIs/types/functions: `nv10_gr_new_()` is the reusable constructor; `nv10_gr_new()` supplies the base NV10 class table. `nv10_gr_init()`, `nv10_gr_intr()`, `nv10_gr_tile()`, and `nv10_gr_chan_new()` are exported through `nv10.h`. `struct nv10_gr_chan` stores `nv10[]`, optional `nv17[]`, `pipe_state`, and LMA windows. `nv10_gr_load_context()` and `nv10_gr_unload_context()` drive context switching.

Control flow/state: channels live in `chan[32]` under a spinlock. Context switch interrupt pauses through `nv04_gr_idle()`, saves MMIO registers and pipe arrays from `NV10_PGRAPH_PIPE_*`, then loads the next channel based on trapped address chid bits. The DMA vertex buffer state is restored by injecting a synthetic FIFO method because hidden hardware state cannot be rebuilt through MMIO alone.

Dependencies/integration: depends on NV04 objects and nsource bitfields, FIFO, framebuffer tile metadata, and low-level register macros. It publishes many legacy object classes, including Celsius variants.

Risks/test signals: fragile areas are pipe array sizing, restore ordering, method injection, chipset gates for NV17-only registers, and interrupt error suppression. Tests should cover multiple GL channels, NV17 LMA methods, tiling updates under FIFO pause, and context-switch stress with PGRAPH status staying idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv10.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv10.h

Purpose: internal NV10 GR header exposing the common NV10 implementation to NV15/NV17 variant files.

Important APIs/types/functions: declares `nv10_gr_new_`, `nv10_gr_init`, `nv10_gr_intr`, `nv10_gr_tile`, and `nv10_gr_chan_new`. It includes `priv.h`, so users see `struct nvkm_gr_func`, `struct nvkm_gr`, `struct nvkm_fb_tile`, and channel/object types.

Control flow/state: no runtime state; it is an integration contract. Variant files supply class tables and call `nv10_gr_new_()` while reusing the shared init/interrupt/tile/channel machinery.

Dependencies/integration: depends on the private GR interface and must remain consistent with symbols exported by `nv10.c`. Risks are signature drift or missing prototypes causing build failures. Test signals are compile coverage for all NV10-family variants and successful link of constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv10.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv15.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv15.c

Purpose: NV15 GR variant descriptor that reuses the NV10 engine implementation with an NV15-specific class table.

Important APIs/types/functions: `nv15_gr_new()` calls `nv10_gr_new_(&nv15_gr, ...)`. `nv15_gr` points to `nv10_gr_init`, `nv10_gr_intr`, `nv10_gr_tile`, and `nv10_gr_chan_new`, and exposes legacy object classes through `nv04_gr_object`.

Control flow/state: no local mutable state; channel and pipe context is owned by `nv10.c`. This file only changes which hardware object classes userspace can instantiate.

Dependencies/integration: depends on `nv10.h` and the NV04 object binder. Risks are class-list mismatches relative to NV15 hardware. Test signals are object creation for Celsius and 2D classes plus normal NV10 context-switch behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv15.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv17.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv17.c

Purpose: NV17 GR variant descriptor. It uses shared NV10 runtime logic but exposes NV17/NV1x object classes, including Celsius class IDs that trigger NV17-specific method handling in `nv10.c`.

Important APIs/types/functions: `nv17_gr_new()` delegates to `nv10_gr_new_()`. The `nv17_gr` table binds `nv10_gr_init`, `nv10_gr_intr`, `nv10_gr_tile`, and `nv10_gr_chan_new`.

Control flow/state: runtime state is the common `struct nv10_gr`/`struct nv10_gr_chan`; this file only provides the function table and supported class list.

Dependencies/integration: depends on `nv10.h` and `nv04_gr_object`. Risks center on exposing unsupported class IDs or omitting NV17 classes needed by userspace. Test signals are NV17 channel creation, Celsius object methods including LMA paths, and successful tiled framebuffer updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv17.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv20.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv20.c

Purpose: NV20/NV2x graphics implementation with hardware context-table backed contexts. It replaces NV10 software register arrays with per-channel instance-memory context images and a channel context table.

Important APIs/types/functions: `nv20_gr_new_()` constructs reusable NV20-style engines. `nv20_gr_oneinit()` allocates `ctxtab`; `nv20_gr_chan_new()` allocates and seeds a `0x37f0` instance-memory context; `nv20_gr_chan_init()` writes context pointers into `ctxtab`; `nv20_gr_chan_fini()` unloads current hardware context when needed. `nv20_gr_tile()`, `nv20_gr_intr()`, `nv20_gr_init()`, and `nv20_gr_dtor()` are shared by several variants.

Control flow/state: persistent state lives in `struct nv20_gr::ctxtab` and each `struct nv20_gr_chan::inst`. Init programs RDI tables, interrupt masks, debug registers, VRAM limits, surface defaults, and clipping bounds. Tile updates pause FIFO, idle PGRAPH, write both direct tile registers and RDI mirror registers.

Dependencies/integration: uses `nvkm_memory` for instance memory, FIFO channel IDs, FB tile metadata, timer polling, and NV10/NV20 register macros.

Risks/test signals: risks include context-image magic offsets, current-context unload timeout, chipset-specific RDI programming, and VRAM BAR sizing assumptions. Test with NV20/NV25 channel create/destroy, suspend/fini on active channels, tiled rendering, and PGRAPH interrupt logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv20.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv20.h

Purpose: private NV20 GR family header shared by NV20/NV25/NV2A/NV30/NV34/NV35 variant files.

Important APIs/types/functions: defines `struct nv20_gr` with `struct nvkm_gr base` and `struct nvkm_memory *ctxtab`; defines `struct nv20_gr_chan` with object, GR pointer, chid, and context instance memory. Declares shared constructor, destructor, oneinit, init, interrupt, tile, and channel lifecycle helpers. Also declares `nv30_gr_init()`.

Control flow/state: no executable flow; it documents the state contract between common NV20 code and variants.

Dependencies/integration: includes `priv.h` and core object types. Risks are ABI-like mismatch between header structs and allocation/lifecycle code. Test signals are compile/link coverage across all NV20-family constructors and channel paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv25.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv25.c

Purpose: NV25 GR variant. It uses NV20 common context management but supplies an NV25 context initializer and class table.

Important APIs/types/functions: `nv25_gr_new()` delegates to `nv20_gr_new_()`. The local channel object function table reuses `nv20_gr_chan_dtor/init/fini`; its `chan_new` allocates an NV20 context image and fills NV25-specific defaults. `nv25_gr` reuses `nv20_gr_dtor`, `nv20_gr_oneinit`, `nv20_gr_init`, `nv20_gr_intr`, and `nv20_gr_tile`.

Control flow/state: persistent state is `ctxtab` and per-channel instance memory. This file controls only the initial contents of those contexts and exposed object classes.

Dependencies/integration: depends on NV20 helpers, FIFO channels, GPU object/memory allocation, and `regs.h`. Risks are wrong context offsets/defaults for NV25 hardware. Test signals are accelerated rendering on NV25, context switch across multiple channels, and no unload timeout during channel close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv2a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv2a.c

Purpose: NV2A/Xbox-derived GR variant using NV20 context infrastructure with NV2A-specific context defaults and supported classes.

Important APIs/types/functions: `nv2a_gr_new()` calls `nv20_gr_new_()`. Local `nv2a_gr_chan_new()` allocates and seeds context memory, while lifecycle hooks are the shared `nv20_gr_chan_*` functions. Runtime init/intr/tile paths are inherited from NV20.

Control flow/state: the file initializes per-channel instance-memory state; channel table and hardware context selection are managed by `nv20.c`.

Dependencies/integration: depends on `nv20.h`, `regs.h`, GPU object allocation, and FIFO channel IDs. Risks are platform-specific magic defaults and class exposure mismatches. Test signals are channel construction, Kelvin/Celsius class operation if supported, and stable suspend/resume or channel teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv2a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv30.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv30.c

Purpose: NV30 GR support layered on NV20 context-table mechanics with an NV30-specific engine init and context template.

Important APIs/types/functions: `nv30_gr_init()` is shared with some later NV3x files. `nv30_gr_new()` uses `nv20_gr_new_()`. The channel constructor creates instance-memory context initialized for NV30 and lifecycle is inherited from `nv20_gr_chan_*`.

Control flow/state: engine initialization programs NV30-era PGRAPH registers and RDI state while common NV20 code owns context-table setup and interrupt handling. Per-channel state persists in instance memory.

Dependencies/integration: depends on `nv20.h`, `regs.h`, FB/tile support, and FIFO channel integration. Risks include chipset-specific register sequences and context image defaults. Test signals are GL channel creation, tile programming, context switch, and absence of PGRAPH/RDI timeout messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv34.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv34.c

Purpose: NV34 GR variant using the NV30 init path and NV20 context lifecycle with NV34-specific context seeds/class table.

Important APIs/types/functions: `nv34_gr_new()` delegates to `nv20_gr_new_(&nv34_gr, ...)`. Shared hooks include `nv20_gr_dtor`, `nv20_gr_oneinit`, `nv30_gr_init`, `nv20_gr_intr`, and `nv20_gr_tile`.

Control flow/state: no independent engine state beyond the inherited `struct nv20_gr`; per-channel context memory is initialized locally and then managed by common NV20 functions.

Dependencies/integration: depends on NV20/NV30 helpers and legacy object binding through `nv04_gr_object`. Risks are mis-seeded context offsets and NV34-specific class mismatches. Test signals are channel creation, GL class instantiation, tiled rendering, and clean channel fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv34.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv35.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv35.c

Purpose: NV35 GR variant, structurally parallel to NV34 but with NV35-specific class/context defaults.

Important APIs/types/functions: `nv35_gr_new()` invokes `nv20_gr_new_()`. It reuses NV20 destructor/oneinit/interrupt/tile and NV30 init, and provides its own channel constructor/object function table backed by `nv20_gr_chan_*`.

Control flow/state: context persistence is in instance memory and context table; this file contributes the initial data image and supported `sclass` entries.

Dependencies/integration: depends on `nv20.h`, `regs.h`, FIFO channel IDs, and object binding via `nv04_gr_object`. Risks are register-template drift and incorrect hardware class exposure. Test signals are NV35 object creation, multi-channel rendering, and no PGRAPH context unload timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv35.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv40.c

Purpose: NV40 graphics implementation introducing generated context programs and list-based channel tracking. It binds NV40 object layout, channel context GPU objects, tile programming, interrupt reporting, and engine init around `nv40_grctx_*` helpers.

Important APIs/types/functions: `nv40_gr_new()`/variant constructors use `nv40_gr_new_()` through `nv40.h`. `nv40_gr_object_bind()` creates 20-byte graphics objects. `nv40_gr_chan_new()`, `nv40_gr_chan_bind()`, `nv40_gr_chan_fini()`, and `nv40_gr_chan_dtor()` manage channel GPU context objects and active/next context registers. `nv40_gr_units()` reads unit masks; `nv40_gr_intr()` maps current context instance to a channel list entry; `nv40_gr_tile()` handles several chipset register layouts.

Control flow/state: `struct nv40_gr` keeps a context size and channel list. Binding allocates a context object, fills it through `nv40_grctx_fill()`, and records its instance. Fini can save the current context by triggering ctxprog transfer unless powering off, then clears current/next loaded bits. Interrupt handling searches by context instance and logs class/method/data.

Dependencies/integration: depends on `nv40.h`, ctxnv40 helpers, FIFO/fb/timer/core object infrastructure, and `regs.h`.

Risks/test signals: fragile areas are ctxprog timeout handling, chipset-specific tile/zcomp registers, list synchronization under engine lock, and object endian bits. Test by channel bind/fini, suspend/resume, tile updates across NV40/NV41/NV47 families, and trap/error log sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv40.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv40.h

Purpose: private NV40 GR header for common NV40 implementation and variants.

Important APIs/types/functions: defines `nv40_gr()` and `nv40_gr_chan()` container helpers, `struct nv40_gr` with base engine, channel list, and context size, and `struct nv40_gr_chan` with object, GR pointer, FIFO pointer, list node, and context instance. Declares `nv40_gr_new_`, `nv40_gr_chan_new`, `nv40_gr_intr`, `nv40_gr_units`, and `nv40_gr_object`.

Control flow/state: no executable flow; it is the shared state contract for NV40 family files.

Dependencies/integration: includes `priv.h` and `ctxnv40.h`. Risks are structure/signature drift breaking variants. Test signals are compile/link coverage and successful channel context binding in NV40 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv44.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv44.c

Purpose: NV44 GR variant descriptor using the shared NV40 implementation with an NV44 class table and context program sizing.

Important APIs/types/functions: `nv44_gr_new()` calls `nv40_gr_new_()` with a local `nv44_gr` function table. Runtime hooks are shared NV40 init/interrupt/tile/channel logic; object classes use `nv40_gr_object`.

Control flow/state: state is inherited from `struct nv40_gr`; this file is a chip binding and class exposure layer.

Dependencies/integration: depends on `nv40.h` and NVIF class definitions. Risks are wrong object class availability or context-size mismatch inherited from the selected ctx generator. Test signals are channel bind/fini, object creation, and rendering on NV44-class devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv50.c

Purpose: NV50/Tesla-generation GR implementation. It handles object/channel creation, context-program initialization, unit reporting, trap decoding, and detailed interrupt diagnostics for dispatch, M2MF, vertex fetch, streamout, code cache, texture, MP, and PROP units.

Important APIs/types/functions: `nv50_gr_new_()` constructs the common engine; `nv50_gr_init()` resets trap state and uploads ctxprog via `nv50_grctx_init`; `nv50_gr_intr()` dispatches data-error and trap handling; `nv50_gr_trap_handler()`, `nv50_gr_tp_trap()`, `nv50_gr_mp_trap()`, and `nv50_gr_prop_trap()` decode unit-specific faults. `nv50_gr_chan_new()` and `nv50_gr_object` are declared for variants.

Control flow/state: engine init enables hardware context switching, clears trap status for present TPs based on unit masks, sets interrupt enables, initializes context size, and clears current/next context pointers. Interrupt handling resolves channel by context instance, prints data-error enums, may reset wedged subunits, acknowledges status, and restarts PGRAPH command processing.

Dependencies/integration: depends on ctxnv50 helpers, NVKM channel lookup, object/gpuobj helpers, timer polling, and NVIF class IDs. Variant files reuse the function table with different class lists/TLB flush hooks.

Risks/test signals: risks include incomplete trap decoding, resetting units while preserving engine progress, chipset address-stride differences, and interrupt status acknowledgement order. Test via Tesla graphics/compute workloads, MMU fault injection, context switch stress, and checking that trap logs include channel/class/method context without interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv50.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv50.h

Purpose: private NV50 GR header exposing shared Tesla-generation GR helpers to chipset variant files.

Important APIs/types/functions: defines `struct nv50_gr` with base GR and lock/context-size state, declares `nv50_gr_new_`, `nv50_gr_init`, `nv50_gr_intr`, `nv50_gr_units`, `nv50_gr_chan_new`, and object binders including `nv50_gr_object`. It also exposes TLB flush helpers used by later NV50-family descriptors.

Control flow/state: no runtime logic; this is the compile-time contract between `nv50.c`, ctx code, and chip-specific descriptors.

Dependencies/integration: includes `priv.h`, ctxnv50 declarations, and object/channel types through private headers. Risks are prototype drift and missing helper declarations for variants. Test signals are all NV50-family variant files compiling and linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/nv50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/priv.h

Purpose: private base interface for NVKM graphics engines.

Important APIs/types/functions: defines `nvkm_gr()` container helper, declares `nvkm_gr_ctor()` and `nv04_gr_idle()`, and defines `struct nvkm_gr_func`. The function table includes lifecycle hooks (`dtor`, `oneinit`, `init`, `fini` through engine base), interrupt handling, tile updates, channel creation, unit reporting, TLB flush, class lists, and optional method handlers depending on generation.

Control flow/state: no executable logic; it defines the vtable shape consumed by `gr/base.c` and implemented by all GR generations in this subset.

Dependencies/integration: includes public `engine/gr.h` and enum helpers, forward-declares FB tiles and channels. Risks are broad because any vtable contract change affects all GR variants. Test signals are whole-driver build coverage and runtime probe of at least one chip from each GR generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/regs.h

Purpose: register map and bit definitions for legacy Nouveau PGRAPH engines, covering NV03/NV04 through NV50-era context-control, status, trap, tile, DMA, and rendering state registers.

Important APIs/types/functions: this header is macro-only. It defines addresses such as `NV03_PGRAPH_INTR`, `NV04_PGRAPH_CTX_*`, `NV10_PGRAPH_CTX_*`, `NV20_PGRAPH_TILE/TSIZE/TLIMIT`, `NV40_PGRAPH_CTXCTL_*`, `NV50_PGRAPH_CTXCTL_*`, and many status/source bit masks.

Control flow/state: no execution; it names hardware state used by init, interrupt, tiling, and context code. Persistence is in device MMIO registers and GPU context images built by other files.

Dependencies/integration: included by old GR files (`nv04.c`, `nv10.c`, `nv20.c`, `nv40.c`, variants). Risks are incorrect constants causing silent hardware misprogramming, wrong bit decoding, or bad context save/restore. Test signals are compile coverage plus runtime validation of interrupts, context switching, and tile programming on affected chipsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/tu102.c

Purpose: Turing TU10x/TU11x GR descriptor and initialization customizations for the GF100+ GR framework.

Important APIs/types/functions: `tu102_gr_new()` rejects GSP-RM-managed devices and calls `gf100_gr_new_()` with `tu102_gr_fwif`. `tu102_gr` supplies function hooks for tile discovery, SM ID setup, GPC MMU init, zcull, filesystem/topology programming, exception setup, trap handling, rops, ZBC, and class exposure. `tu102_gr_av_to_init_veid()` converts firmware blobs into init packs.

Control flow/state: init is delegated to `gf100_gr_init()` which calls TU102-specific hooks. `tu102_gr_init_fs()` writes SM-to-TPC mappings and topology tables. `tu102_gr_init_zcull()` programs bank/tile distribution per GPC/TPC. `tu102_gr_init_gpc_mmu()` mirrors MMU config registers into GPC MMU state. Firmware module declarations describe required FECS/GPCCS and software init blobs.

Dependencies/integration: depends on `gf100.h`, `ctxgf100.h`, GSP subdevice state, firmware loading, and many GF100/GM/GV/GP helper functions.

Risks/test signals: risks include topology math for disabled units, firmware availability/signature, GSP path gating, and zcull distribution. Test with TU102/TU104/TU106/TU116/TU117 firmware loads, channel creation for Turing graphics/compute classes, and exception/trap handling under shader faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/Kbuild

Purpose: build manifest for legacy PMPEG engine support.

Important APIs/types/functions: adds `nv31.o`, `nv40.o`, `nv44.o`, `nv50.o`, and `g84.o` to `nvkm-y`.

Control flow/state: no runtime behavior; it controls which implementations are compiled into the NVKM driver.

Dependencies/integration: Kbuild integrates with the parent Nouveau build. Risks are omitted objects producing unresolved chipset constructor references or missing engine support. Test signals are kernel build/link and probe paths for NV31/NV40/NV44/NV50/G84 PMPEG chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/g84.c

Purpose: G84 PMPEG descriptor that reuses NV50 PMPEG init/interrupt and exposes the `G82_MPEG` class.

Important APIs/types/functions: `g84_mpeg_new()` calls `nvkm_engine_new_()` with `g84_mpeg`. The function table uses `nv50_mpeg_init`, `nv50_mpeg_intr`, `nv50_mpeg_cclass`, and `nv31_mpeg_object`.

Control flow/state: no local state; runtime engine state is the common `nvkm_engine` plus context class object state.

Dependencies/integration: depends on `priv.h` and `nvif/class.h`. Risks are wrong class ID or context class binding mismatch. Test signals are engine probe, MPEG object creation, and PMPEG interrupt acknowledgement on G84/G82 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv31.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv31.c

Purpose: NV31 PMPEG engine implementation for early MPEG/VPE hardware. It manages a single MPEG channel, DMA object method emulation, tiling registers, interrupt handling, and PMPEG/VPE initialization.

Important APIs/types/functions: `nv31_mpeg_new_()` is the reusable constructor; `nv31_mpeg_new()` supplies `nv31_mpeg_mthd_dma`. `nv31_mpeg_object_bind()` creates 16-byte MPEG objects. `nv31_mpeg_chan_new()` enforces single-channel ownership. `nv31_mpeg_intr()` handles initial binding interrupts and DMA method traps. `nv31_mpeg_init()` programs VPE/PMPEG registers and waits for ready.

Control flow/state: `struct nv31_mpeg` stores `func`, engine, and one active `chan`. DMA methods read DMA object words from instance memory aperture, validate linear layout, compute base/size, and program command/data/image windows. Interrupt handling masks handled binding/DMA events and logs unhandled status with channel identity.

Dependencies/integration: uses core GPU object helpers, FIFO channel pointers, FB tile updates, timer polling, and NVIF class IDs.

Risks/test signals: risks include single-channel contention, DMA object validation, VRAM-only image DMA restriction, and init timeout. Test with MPEG object bind, DMA_CMD/DMA_DATA/DMA_IMAGE methods, tile updates, and expected `-EBUSY` behavior for concurrent channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv31.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv31.h

Purpose: private NV31 PMPEG header shared by NV31 and NV40 implementations.

Important APIs/types/functions: defines `struct nv31_mpeg`, `struct nv31_mpeg_func` with `mthd_dma`, and `struct nv31_mpeg_chan`. Declares `nv31_mpeg_new_()` and `nv31_mpeg_chan_new()`.

Control flow/state: no executable behavior; it defines the single-channel PMPEG state model and function hook for DMA method handling.

Dependencies/integration: includes `priv.h`, public `engine/mpeg.h`, and core object definitions. Risks are hook/structure mismatch with `nv31.c` and `nv40.c`. Test signals are compile/link coverage and successful NV31/NV40 MPEG engine construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv31.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv40.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv40.c

Purpose: NV40 PMPEG variant that reuses NV31 engine code but supplies an instmem-aware DMA method decoder.

Important APIs/types/functions: `nv40_mpeg_mthd_dma()` reads DMA object words through `nvkm_instmem_rd32()` and programs PMPEG command/data/image windows. `nv40_mpeg_new()` passes a `struct nv31_mpeg_func` into `nv31_mpeg_new_()`.

Control flow/state: no local persistent state; DMA method handling depends on the active `struct nv31_mpeg` reached from `device->mpeg`. It validates linear DMA objects and rejects non-VRAM image DMA.

Dependencies/integration: depends on `nv31.h`, `subdev/instmem.h`, and PMPEG registers. Risks are DMA aperture interpretation, access flags bit shifting, and false rejection/acceptance of DMA objects. Test signals are trapped DMA method recovery and MPEG command/data/image buffers on NV40 PMPEG.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv44.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv44.c

Purpose: NV44 PMPEG implementation with multiple channel objects tracked by context instance rather than NV31's single-channel model.

Important APIs/types/functions: `nv44_mpeg_new()` constructs `struct nv44_mpeg` and initializes `chan` list. `nv44_mpeg_chan_bind()` creates a 264-word context object and seeds register `0x78`. `nv44_mpeg_chan_fini()` clears active context. `nv44_mpeg_intr()` maps current instance to a channel and handles binding/DMA method interrupts using `nv40_mpeg_mthd_dma()`.

Control flow/state: channel state persists as a GPU object instance plus a list node. Interrupt handling rotates a found channel to the list head, acknowledges status, and logs unhandled events with channel ID/name.

Dependencies/integration: uses core gpuobj/object helpers, FIFO channels, NV31 init/tile helpers, NV40 DMA method decoder, and NVIF MPEG class.

Risks/test signals: risks include list synchronization, stale active context during fini, and DMA method decoding shared with NV40. Test multiple MPEG channels, active-channel teardown, initial object binding interrupt, and DMA window programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv44.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv50.c

Purpose: NV50 PMPEG engine implementation with context-class binding, simplified interrupt handling, and engine initialization.

Important APIs/types/functions: `nv50_mpeg_new()` calls `nvkm_engine_new_()`. `nv50_mpeg_cclass_bind()` allocates a 128-word context class object with default words at `0x70` and `0x7c`. `nv50_mpeg_intr()` handles initial binding status and logs unhandled interrupts. `nv50_mpeg_init()` programs PMPEG registers and waits for ready.

Control flow/state: no custom channel list; context state is represented by bound GPU objects and common engine state. Init clears control, configures PMPEG registers, enables, clears/arms interrupts, and waits on status bit.

Dependencies/integration: uses core gpuobj/object helpers, timer polling, and NV31 MPEG object class for software-visible class exposure.

Risks/test signals: risks are magic context defaults, init timeout, and insufficient interrupt decoding. Test engine ready wait, context class binding, initial object bind interrupt clearing, and video decode command submission on NV50/G84-family chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/priv.h

Purpose: private PMPEG declarations shared across MPEG engine implementations.

Important APIs/types/functions: declares `nv31_mpeg_init`, `nv31_mpeg_tile`, `nv31_mpeg_object`, `nv40_mpeg_mthd_dma`, `nv50_mpeg_init`, `nv50_mpeg_intr`, and `nv50_mpeg_cclass`.

Control flow/state: header only; it wires common routines to variant descriptors.

Dependencies/integration: includes public `engine/mpeg.h` and forward-declares `struct nvkm_chan`. Risks are prototype drift. Test signals are build coverage for all MPEG objects listed in Kbuild.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mpeg/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msenc/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msenc/Kbuild

Purpose: placeholder build manifest for MSENC support.

Important APIs/types/functions: contains only the SPDX line and a commented-out `nvkm-y += nvkm/engine/msenc/base.o` entry, so no MSENC object is built from this directory.

Control flow/state: no runtime behavior.

Dependencies/integration: Kbuild-level integration only. Risk is intentional absence being mistaken for enabled support; uncommenting without implementation would affect build/link. Test signal is build output confirming no MSENC object from this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msenc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/Kbuild

Purpose: build manifest for MSPDEC Falcon-based video decode engines.

Important APIs/types/functions: adds `base.o`, `g98.o`, `gt215.o`, `gf100.o`, and `gk104.o` to `nvkm-y`.

Control flow/state: no runtime behavior; determines which constructors and init tables are linked.

Dependencies/integration: parent Nouveau Kbuild and chipset constructor references. Risks are missing objects for supported chipsets. Test signals are successful build and probe coverage for G98/GT215/GF100/GK104 MSPDEC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/base.c

Purpose: common constructor for MSPDEC Falcon engines.

Important APIs/types/functions: `nvkm_mspdec_new_()` delegates to `nvkm_falcon_new_()` with `enable=true`, base address `0x085000`, and the chip-specific `nvkm_falcon_func`.

Control flow/state: no local state; all engine state is allocated by the Falcon framework at the supplied MMIO base.

Dependencies/integration: depends on `priv.h` and common Falcon engine support. Risks are wrong MMIO base or enable flag causing all MSPDEC variants to fail. Test signals are Falcon probe/init at `0x085000`, interrupt routing, and class creation for each variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/g98.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/g98.c

Purpose: G98 MSPDEC Falcon descriptor and init sequence.

Important APIs/types/functions: `g98_mspdec_init()` writes `0x085010 = 0x0000ffd2` and `0x08501c = 0x0000fff2`. `g98_mspdec_new()` calls `nvkm_mspdec_new_()` with class `G98_MSPDEC`.

Control flow/state: initialization is two MMIO writes layered onto common Falcon construction. No local persistence.

Dependencies/integration: depends on Falcon base constructor and NVIF class IDs. Risks are incorrect Falcon register magic or class mismatch. Test signals are Falcon boot/init and decode class object creation on G98-family GPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/g98.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gf100.c

Purpose: GF100 MSPDEC Falcon descriptor.

Important APIs/types/functions: `gf100_mspdec_init()` writes `0x0000fff2` to both `0x085010` and `0x08501c`. `gf100_mspdec_new()` constructs the engine with class `GF100_MSPDEC`.

Control flow/state: simple init hook plus common Falcon state at `0x085000`.

Dependencies/integration: uses `nvkm_mspdec_new_()` and `nvif/class.h`. Risks are register-value differences across Fermi variants. Test signals are GF100 class exposure, Falcon init, and video decode command execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gk104.c

Purpose: GK104 MSPDEC descriptor reusing the GF100 init sequence with a Kepler class ID.

Important APIs/types/functions: `gk104_mspdec_new()` passes `gk104_mspdec` to `nvkm_mspdec_new_()`. The function table uses `gf100_mspdec_init` and exposes `GK104_MSPDEC`.

Control flow/state: no local state; common Falcon engine state at `0x085000`.

Dependencies/integration: depends on `priv.h`, `nvif/class.h`, and GF100 init helper declaration. Risks are assuming GF100 register programming remains valid on GK104. Test signals are Kepler MSPDEC probe and class creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gt215.c

Purpose: GT215/GT212 MSPDEC descriptor using G98-era initialization with a GT212 class ID.

Important APIs/types/functions: `gt215_mspdec_new()` constructs through `nvkm_mspdec_new_()`. The function table uses `g98_mspdec_init` and exposes `GT212_MSPDEC`.

Control flow/state: no local persistence; init/register state is common Falcon plus G98 helper writes.

Dependencies/integration: depends on G98 init helper and NVIF class IDs. Risks are GT215-specific register differences not captured by G98 init. Test signals are GT215 MSPDEC class creation and Falcon readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/priv.h

Purpose: private MSPDEC declarations.

Important APIs/types/functions: declares `nvkm_mspdec_new_`, `g98_mspdec_init`, and `gf100_mspdec_init`; includes public `engine/mspdec.h`.

Control flow/state: header-only integration contract for MSPDEC variants.

Dependencies/integration: depends on Falcon function types from public engine headers. Risks are missing prototypes for variant reuse. Test signals are compile/link coverage for all MSPDEC files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/mspdec/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/Kbuild

Purpose: build manifest for MSPPP Falcon-based video post-processing engines.

Important APIs/types/functions: builds `base.o`, `g98.o`, `gt215.o`, and `gf100.o`.

Control flow/state: no runtime behavior.

Dependencies/integration: parent Nouveau Kbuild. Risks are missing linked constructors for chipsets. Test signals are successful build and probe of G98/GT215/GF100 MSPPP support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/base.c

Purpose: common constructor for MSPPP Falcon engines.

Important APIs/types/functions: `nvkm_msppp_new_()` calls `nvkm_falcon_new_()` with MMIO base `0x086000`, enabled, and a chip-specific `nvkm_falcon_func`.

Control flow/state: no local persistence; Falcon framework owns state.

Dependencies/integration: depends on `priv.h` and common Falcon engine support. Risks are incorrect base address affecting all MSPPP variants. Test signals are engine probe at `0x086000` and class availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/g98.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/g98.c

Purpose: G98 MSPPP descriptor and init hook.

Important APIs/types/functions: `g98_msppp_init()` writes `0x086010 = 0x0000ffd2` and `0x08601c = 0x0000fff2`. `g98_msppp_new()` constructs with `nvkm_msppp_new_()` and exposes `G98_MSPPP`.

Control flow/state: common Falcon creation at `0x086000` followed by two MMIO initialization writes; no local persistence beyond the function table.

Dependencies/integration: depends on `priv.h` and `nvif/class.h`. Risks are class/init mismatch. Test signals are class object creation and Falcon initialization for G98 MSPPP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/g98.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/gf100.c

Purpose: GF100 MSPPP descriptor with an inline init hook.

Important APIs/types/functions: `gf100_msppp_init()` writes `0x086010 = 0x0000fff2` and `0x08601c = 0x0000fff2`. `gf100_msppp_new()` exposes `GF100_MSPPP`.

Control flow/state: common Falcon construction followed by two MMIO initialization writes.

Dependencies/integration: depends on `nvkm_msppp_new_()` and NVIF class IDs. Risks are register programming assumptions across Fermi variants. Test signals are Falcon ready state and GF100 MSPPP class creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/gt215.c

Purpose: GT215 MSPPP descriptor using the G98 init hook with GT212 class exposure.

Important APIs/types/functions: `gt215_msppp_new()` calls `nvkm_msppp_new_()` with a function table exposing `GT212_MSPPP`.

Control flow/state: no local state; initialization is delegated to `g98_msppp_init`.

Dependencies/integration: depends on `priv.h`, G98 init helper, and NVIF class IDs. Risks are chipset register differences hidden by helper reuse. Test signals are GT215 MSPPP probe and class object creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/priv.h

Purpose: private MSPPP declarations.

Important APIs/types/functions: declares `nvkm_msppp_new_()` and `g98_msppp_init()`; includes public `engine/msppp.h`.

Control flow/state: header-only contract for variants.

Dependencies/integration: depends on Falcon function types. Risks are missing prototypes for reused init helpers. Test signals are compile/link coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msppp/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/Kbuild

Purpose: build manifest for MSVLD Falcon-based video decode engines.

Important APIs/types/functions: builds `base.o`, `g98.o`, `gt215.o`, `mcp89.o`, `gf100.o`, and `gk104.o`.

Control flow/state: no runtime behavior.

Dependencies/integration: parent Nouveau Kbuild. Risks are omitted constructor objects for supported chipsets. Test signals are build/link and probe coverage for listed MSVLD variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/base.c

Purpose: common constructor for MSVLD Falcon engines.

Important APIs/types/functions: `nvkm_msvld_new_()` delegates to `nvkm_falcon_new_()` with MMIO base `0x084000`.

Control flow/state: no local state; common Falcon engine owns memory, interrupt, and lifecycle state.

Dependencies/integration: depends on `priv.h` and Falcon support. Risks are wrong MMIO base or enabled flag. Test signals are Falcon readiness and class creation for all MSVLD variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/g98.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/g98.c

Purpose: G98 MSVLD descriptor and init hook.

Important APIs/types/functions: `g98_msvld_init()` writes `0x084010 = 0x0000ffd2` and `0x08401c = 0x0000fff2`. `g98_msvld_new()` exposes class `G98_MSVLD`.

Control flow/state: common Falcon creation plus two MMIO writes; no local persistence.

Dependencies/integration: depends on `nvkm_msvld_new_()` and NVIF classes. Risks are init magic and class mismatch. Test signals are G98 MSVLD Falcon ready and class object creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/g98.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gf100.c

Purpose: GF100 MSVLD descriptor.

Important APIs/types/functions: `gf100_msvld_init()` writes `0x0000fff2` to `0x084010` and `0x08401c`. `gf100_msvld_new()` exposes `GF100_MSVLD`.

Control flow/state: simple init hook on top of common Falcon construction.

Dependencies/integration: uses `nvkm_msvld_new_()` and NVIF classes. Risks are MMIO value portability across Fermi revisions. Test signals are GF100 MSVLD probe, class creation, and decode firmware/command progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gk104.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gk104.c

Purpose: GK104 MSVLD descriptor reusing GF100 initialization.

Important APIs/types/functions: `gk104_msvld_new()` calls `nvkm_msvld_new_()` with a function table using `gf100_msvld_init` and class `GK104_MSVLD`.

Control flow/state: common Falcon state only; no local persistence.

Dependencies/integration: depends on GF100 init helper and NVIF class IDs. Risks are over-broad reuse of GF100 init for Kepler. Test signals are GK104 MSVLD probe and class object creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gk104.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gt215.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gt215.c

Purpose: GT215/GT212 MSVLD descriptor using G98-style initialization.

Important APIs/types/functions: `gt215_msvld_new()` calls `nvkm_msvld_new_()` with `g98_msvld_init` and class `GT212_MSVLD`.

Control flow/state: no local state; common Falcon at `0x084000`.

Dependencies/integration: depends on G98 helper and NVIF class IDs. Risks are register differences between G98 and GT215. Test signals are GT215 MSVLD class creation and Falcon readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/gt215.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/mcp89.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/mcp89.c

Purpose: MCP89 MSVLD descriptor for integrated GT21x-era hardware.

Important APIs/types/functions: `mcp89_msvld_new()` delegates to `nvkm_msvld_new_()` with `g98_msvld_init` and exposes `GT212_MSVLD`.

Control flow/state: no local mutable state; common Falcon construction and G98 initialization are reused.

Dependencies/integration: depends on `priv.h`, `nvif/class.h`, and G98 init helper. Risks are MCP89-specific init differences not reflected by reuse. Test signals are MCP89 MSVLD probe, Falcon init, and video decode class creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/mcp89.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/priv.h

Purpose: private MSVLD declarations.

Important APIs/types/functions: declares `nvkm_msvld_new_()`, `g98_msvld_init()`, and `gf100_msvld_init()`; includes public `engine/msvld.h`.

Control flow/state: header-only contract.

Dependencies/integration: depends on Falcon function types and public engine API. Risks are prototype drift. Test signals are compile/link coverage for MSVLD variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/msvld/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/Kbuild

Purpose: build manifest for modern NVDEC engines.

Important APIs/types/functions: builds `base.o`, `gm107.o`, `tu102.o`, and `ga102.o`.

Control flow/state: no runtime behavior.

Dependencies/integration: parent Nouveau Kbuild. Risks are missing object files for constructor references. Test signals are build/link and probe coverage for GM107/TU102/GA102 NVDEC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/base.c

Purpose: common NVDEC constructor/destructor for firmware-interface based Falcon engines.

Important APIs/types/functions: `nvkm_nvdec_new_()` selects a supported `nvkm_nvdec_fwif`, calls its `load()` hook, and constructs an engine with `nvkm_engine_ctor()`. `nvkm_nvdec_dtor()` releases firmware with `nvkm_firmware_dtor()`.

Control flow/state: persistent state includes loaded firmware in `struct nvkm_nvdec`. The base engine function table has a destructor and empty software class list; chip files provide firmware/load behavior.

Dependencies/integration: depends on `core/firmware.h`, public NVDEC engine API, and chip-specific fwif arrays. Risks are firmware load failure, unsupported fwif selection, or cleanup leaks. Test signals are firmware request/load/unload and engine construction on supported chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/ga102.c

Purpose: GA102/Ampere NVDEC descriptor for the newer Falcon control path.

Important APIs/types/functions: `ga102_nvdec_flcn` supplies GM200/GA102 Falcon operations including enable/disable, PMC reset, memory-scrubbing wait, and DMA descriptors. `ga102_nvdec_nofw()` is a no-firmware load hook, and `ga102_nvdec_new()` calls `nvkm_nvdec_new_()` with MMIO base `0x848000` unless GSP-RM owns the device.

Control flow/state: runtime state is base NVDEC plus Falcon engine state; there is no firmware payload to retain on this path. The file supplies chip-specific Falcon reset/DMA behavior and GSP gating.

Dependencies/integration: depends on `priv.h`, GA102 Falcon helpers, and `subdev/gsp.h`. Risks are reset/DMA setup, the nonzero base address, and incorrect GSP bypass. Test signals are GA102 NVDEC construction without firmware requests, no construction under GSP-RM where expected, and Falcon boot/reset progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/gm107.c

Purpose: GM107/Maxwell NVDEC descriptor.

Important APIs/types/functions: defines an empty chip-specific Falcon function table, `gm107_nvdec`, `gm107_nvdec_nofw()` returning success, exported `gm107_nvdec_fwif`, and `gm107_nvdec_new()` delegating to `nvkm_nvdec_new_()` with base address `0`.

Control flow/state: no independent state and no firmware payload on this path; base NVDEC/Falcon code owns engine lifecycle.

Dependencies/integration: depends on `priv.h` and the base fwif selector even though the selected loader is no-firmware. Risks are missing Falcon setup if hardware requires more than the empty table. Test signals are GM107 NVDEC engine creation and video decode channel operation without firmware load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/priv.h

Purpose: private NVDEC definitions for firmware-interface based constructors.

Important APIs/types/functions: defines `struct nvkm_nvdec_func` with firmware/Falcon behavior, `struct nvkm_nvdec_fwif` with version/load/function pointers, and declares `nvkm_nvdec_new_()`.

Control flow/state: header-only state contract; base code uses these tables to select and load firmware.

Dependencies/integration: includes public `engine/nvdec.h`. Risks are fwif ABI drift. Test signals are compile/link coverage plus firmware selection for GM107/TU102/GA102.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/tu102.c

Purpose: TU102/Turing NVDEC descriptor.

Important APIs/types/functions: provides TU102 firmware interface tables and `tu102_nvdec_new()`, with GSP-RM gating via `nvkm_gsp_rm()`.

Control flow/state: chip-specific firmware metadata feeds the base `nvkm_nvdec_new_()` path; no local persistent state.

Dependencies/integration: depends on `priv.h` and `subdev/gsp.h`. Risks are firmware availability and correct behavior when GSP owns NVDEC. Test signals are Turing NVDEC firmware load, engine probe skip under GSP-RM, and decode command execution without Falcon faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvdec/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/Kbuild

Purpose: build manifest for NVENC engines.

Important APIs/types/functions: builds `base.o`, `gm107.o`, and `tu102.o`.

Control flow/state: no runtime behavior.

Dependencies/integration: parent Kbuild. Risks are missing constructor objects for supported encoder hardware. Test signals are build/link and probe coverage for GM107/TU102 NVENC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/base.c

Purpose: common NVENC constructor/destructor for firmware-interface based encoder engines.

Important APIs/types/functions: `nvkm_nvenc_new_()` selects an `nvkm_nvenc_fwif`, calls its load hook, and constructs the engine. `nvkm_nvenc_dtor()` releases firmware through `nvkm_firmware_dtor()`.

Control flow/state: persistent state is loaded firmware in `struct nvkm_nvenc`; class exposure is empty in the base table unless chip-specific layers add it elsewhere.

Dependencies/integration: depends on `core/firmware.h` and chip-specific fwif arrays. Risks are firmware load/cleanup failures and unsupported fwif selection. Test signals are firmware request success, engine construction, destructor cleanup, and encoder Falcon boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/gm107.c

Purpose: GM107 NVENC descriptor.

Important APIs/types/functions: defines an empty Falcon function table, `gm107_nvenc`, `gm107_nvenc_nofw()` returning success, exported `gm107_nvenc_fwif`, and `gm107_nvenc_new()` delegating to `nvkm_nvenc_new_()`.

Control flow/state: no local mutable state and no firmware payload on this path; base NVENC owns engine lifecycle.

Dependencies/integration: depends on `priv.h` and the base fwif selector. Risks are missing Falcon setup if hardware needs more than the empty table. Test signals are GM107 NVENC engine probe and encode command/Falcon progress where userspace exposes it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/priv.h

Purpose: private NVENC definitions for firmware-interface based engines.

Important APIs/types/functions: defines `struct nvkm_nvenc_func`, `struct nvkm_nvenc_fwif`, and declares `nvkm_nvenc_new_()`.

Control flow/state: header-only contract consumed by base and chip files.

Dependencies/integration: includes public `engine/nvenc.h`. Risks are firmware-interface signature drift. Test signals are compile/link coverage for GM107/TU102 NVENC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/tu102.c

Purpose: TU102/Turing NVENC descriptor.

Important APIs/types/functions: provides TU102 firmware interface data and `tu102_nvenc_new()`, which gates construction off when `nvkm_gsp_rm(device->gsp)` indicates GSP ownership.

Control flow/state: chip-specific firmware metadata is fed into common `nvkm_nvenc_new_()`; no local persistence beyond static tables.

Dependencies/integration: depends on `priv.h` and `subdev/gsp.h`. Risks are GSP ownership mismatches and firmware availability. Test signals are Turing NVENC probe skip under GSP-RM, firmware load otherwise, and encoder Falcon boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/nvenc/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/Kbuild

Purpose: build manifest for SEC Falcon engine support.

Important APIs/types/functions: builds `nvkm/engine/sec/g98.o`.

Control flow/state: no runtime behavior; it selects the G98 SEC implementation for compilation.

Dependencies/integration: parent Nouveau Kbuild and SEC constructor references. Risks are missing SEC object support if this line is altered. Test signals are successful build/link and SEC engine probe on G98-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/Kbuild -->
