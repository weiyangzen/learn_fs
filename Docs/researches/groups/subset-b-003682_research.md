# subset-b-003682 research

Grouped research for Nouveau SEC/SEC2, SW, VP/Xtensa, Falcon, nvfw, ACR, and BAR implementation files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/fuc/g98.fuc0s.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/fuc/g98.fuc0s.h

## Purpose
Embeds the G98 SEC falcon microcode as static `uint32_t` data and code arrays. The data image contains context slots, method dispatch tables, SEC method tables, swap storage, DMA object fields, key/IV fields, and command descriptors. The code image is raw falcon instruction words with labels in comments for interrupt handling, context load, DMA loops, query/condition handling, and SEC operations.

## Important APIs, types, and functions
The file exports only `g98_sec_data[]` and `g98_sec_code[]` for inclusion by `g98.c`. It has no callable C API. The consumer wires the arrays into `struct nvkm_falcon_func.code` and `.data` so `nvkm_falcon_new_()` can upload them to the SEC engine.

## Control flow, state, and persistence
Runtime control flow lives inside the firmware blob, not C. Persistent driver-visible state is the compiled-in image bytes. Firmware execution consumes channel methods and GPU context fields after upload to falcon IMEM/DMEM.

## Dependencies and integration points
Included directly by `engine/sec/g98.c`. It depends on the falcon loader understanding the code/data split and the G98 SEC method ABI.

## Risks and test signals
Any word change can break opaque SEC behavior. Build coverage verifies syntax only; runtime signals are SEC engine creation, class exposure, method completion, and dispatch-error logs from `g98_sec_intr()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/fuc/g98.fuc0s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/g98.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/g98.c

## Purpose
Defines the G98 SEC engine wrapper around the embedded falcon microcode. It exposes the `G98_SEC` class, uploads `g98_sec_code` and `g98_sec_data`, and reports SEC method dispatch failures.

## Important APIs, types, and functions
`g98_sec_new()` constructs the engine via `nvkm_falcon_new_()` at MMIO base `0x087000`. `g98_sec_intr()` decodes dispatch error status from registers `0x087040` and `0x087044`. `g98_sec_isr_error_name[]` maps hardware status codes to names. The local `g98_sec` `nvkm_falcon_func` supplies firmware images, interrupt callback, and supported class table.

## Control flow, state, and persistence
Construction binds the firmware image and class table to a falcon-backed engine. On interrupt, the handler reads status, method address, subchannel, and method data, then logs the channel id, instance address, channel name, method, and data. No long-lived software state is stored beyond the falcon engine object.

## Dependencies and integration points
Depends on `engine/sec.h`, FIFO channel metadata, `core/enum`, GPU object addresses, and the generated `fuc/g98.fuc0s.h`. Integrated through Nouveau's chipset engine table by calling `g98_sec_new()`.

## Risks and test signals
Register layout and method decoding are G98-specific. The primary test signal is a clean SEC class registration and absence of `DISPATCH_ERROR` logs while exercising SEC methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec/g98.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/Kbuild

## Purpose
Adds SEC2 engine objects to the Nouveau nvkm build. It selects the common SEC2 core and per-generation implementations for Pascal, Turing, Ampere, and R535/GSP-backed operation.

## Important APIs, types, and functions
The build entries compile `base.o`, `gp102.o`, `gp108.o`, `tu102.o`, `ga102.o`, and `r535.o` into `nvkm-y`.

## Control flow, state, and persistence
There is no runtime logic. Build inclusion controls which constructors and firmware-interface tables are available to chipset dispatch code.

## Dependencies and integration points
Included by the higher-level Nouveau engine Kbuild. These objects depend on the falcon, ACR, firmware, interrupt, GSP, and SEC2 public headers.

## Risks and test signals
Missing entries cause unresolved constructors or absent SEC2 support on affected GPUs. Build logs and module symbol resolution are the main tests; runtime probe logs confirm the correct generation file was linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/base.c

## Purpose
Implements the common SEC2 engine lifecycle. SEC2 is a falcon-based security processor used for ACR and low-secure falcon bootstrapping on newer NVIDIA GPUs.

## Important APIs, types, and functions
`nvkm_sec2_new_()` allocates `struct nvkm_sec2`, loads a firmware interface with `nvkm_firmware_load()`, constructs the falcon, and creates a queue manager plus command/message queues. Engine callbacks include `nvkm_sec2_oneinit()`, `nvkm_sec2_init()`, `nvkm_sec2_fini()`, and `nvkm_sec2_dtor()`. `nvkm_sec2_finimsg()` handles unload completion.

## Control flow, state, and persistence
Initialization acquires the falcon, clears interrupts, resets `initmsg` and `running`, enables the interrupt handler, and starts firmware. Oneinit registers the SEC2 interrupt, optionally through a generation-specific vector provider. Fini sends an unload command if firmware initialized queues, waits for halt, blocks interrupts, tears down queues, disables falcon, and releases ownership. State is kept in atomics, falcon state, and queue objects.

## Dependencies and integration points
Depends on falcon queue helpers, `nvfw/sec2.h`, firmware loader, MC interrupts, and timer polling. ACR code uses SEC2 command queues for bootstrap commands.

## Risks and test signals
Init-message parsing gates queue readiness. Interrupt blocking and unload timeouts are sensitive during suspend/resume. Signals include init message success, command queue ready completion, unload warnings, halt logs, and successful ACR bootstrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/ga102.c

## Purpose
Provides Ampere GA10x SEC2 support, including updated firmware formats, interrupt routing through VFN, DMA-capable falcon operations, and optional R535/GSP ownership.

## Important APIs, types, and functions
`ga102_sec2_new()` selects either `r535_sec2_new()` under GSP RM or `nvkm_sec2_new_()` at address `0x840000`. `ga102_sec2_initmsg()` parses `nv_sec2_init_msg_v1`. `ga102_sec2_intr_vector()` selects the falcon and reads the vector from `0x8403e0`. `ga102_sec2_acr_bootstrap_falcon()` sends ACR bootstrap commands using the v1 message layout. `ga102_sec2_load()` loads signed image/descriptor v2 low-secure firmware.

## Control flow, state, and persistence
The firmware interface installs GA102 queue offsets, v2 SEC2 unit ids, and a v2 ACR low-secure descriptor writer. Init message parsing initializes command and message queues based on firmware-reported indices, offsets, and sizes. Bootstrap requests are synchronous command-queue exchanges.

## Dependencies and integration points
Depends on `ga102_flcn_dma`, VFN interrupts, GSP detection, ACR LS firmware loading, and SEC2 firmware blobs for GA102-GA107.

## Risks and test signals
TOP reports stale PRI addresses on Turing/Ampere, so the hard-coded address is intentional. Test signals include VFN interrupt delivery, queue init, ACR bootstrap success, and fallback to R535 path when GSP RM is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/gp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/gp102.c

## Purpose
Implements Pascal GP10x SEC2 support and shared SEC2 helpers used by later generations. It handles firmware absence fallback, ACR bootstrap commands, init-message queue setup, interrupts, and low-secure bootloader descriptor creation.

## Important APIs, types, and functions
Exports `gp102_sec2_nofw()`, `gp102_sec2_initmsg()`, `gp102_sec2_intr()`, `gp102_sec2_acr_bld_write_1()`, `gp102_sec2_acr_bld_patch_1()`, `gp102_sec2_load()`, `gp102_sec2_new()`, and the `gp102_sec2` function table. Local ACR helpers build v0/v1 loader descriptors and issue `NV_SEC2_ACR_CMD_BOOTSTRAP_FALCON`.

## Control flow, state, and persistence
Firmware interrupt bit `0x40` triggers one-time init-message parsing and then drains queued messages. Halt bit `0x10` emits tracepc while `running` is set. Init-message parsing assigns command or message queue registers from firmware queue descriptors. ACR bootstrapping sends a command to SEC2 and treats firmware error codes as `-EINVAL`.

## Dependencies and integration points
Depends on `nvfw/sec2.h`, `nvfw/flcn.h`, ACR LSF functions, falcon queue helpers, and GM200/GP102 falcon operations. Firmware declarations cover GP102, GP104, GP106, and GP107 SEC2 blobs.

## Risks and test signals
Interrupt masks and queue format must match firmware. Firmware unavailable returns success but leaves reduced functionality. Signals include init queue logs, halt tracepc, ACR bootstrap messages, and missing-firmware warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/gp108.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/gp108.c

## Purpose
Specializes SEC2 firmware selection for GP108 and GV100 class devices while reusing the GP102 SEC2 implementation.

## Important APIs, types, and functions
`gp108_sec2_new()` calls `nvkm_sec2_new_()` with `gp108_sec2_fwif`. The firmware interface uses `gp102_sec2_load`, the shared `gp102_sec2` function table, and `gp102_sec2_acr_1`.

## Control flow, state, and persistence
Construction follows the common SEC2 path. Runtime queue, interrupt, and ACR behavior are inherited from GP102. This file only changes which firmware blobs and ACR low-secure descriptor format are used.

## Dependencies and integration points
Depends on `subdev/acr.h` and GP102 SEC2 helpers. Registers firmware requirements for `nvidia/gp108/sec2/*` and `nvidia/gv100/sec2/*`.

## Risks and test signals
The risk is firmware table drift: a wrong ACR function or missing MODULE_FIRMWARE entry blocks SEC2 load. Runtime signals mirror GP102: firmware load success, init-message parsing, and ACR bootstrap success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/gp108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/priv.h

## Purpose
Defines SEC2 private function contracts shared by SEC2 generation files and the common core.

## Important APIs, types, and functions
`struct nvkm_sec2_func` describes falcon ops, firmware unit ids, optional interrupt vector lookup, interrupt handler, and init-message parser. `struct nvkm_sec2_fwif` maps firmware versions to load routines, runtime functions, and ACR low-secure functions. It declares constructors and shared GP102 helpers including ACR bootloader write/patch callbacks.

## Control flow, state, and persistence
No runtime code exists. The structs determine how `nvkm_sec2_new_()` chooses firmware, builds a falcon, registers interrupts, sends unload commands, and exposes ACR integration.

## Dependencies and integration points
Includes public `engine/sec2.h` and forward declares ACR low-secure firmware. Used by all SEC2 implementation files and R535 alternate construction.

## Risks and test signals
Signature drift breaks all SEC2 generations at build time. Mis-set unit ids or callback pointers surface as init-message failures, unload failures, or ACR bootstrap errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/r535.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/r535.c

## Purpose
Provides the minimal SEC2 engine object used when NVIDIA's R535 GSP RM owns SEC2 firmware management.

## Important APIs, types, and functions
`r535_sec2_new()` allocates `struct nvkm_sec2`, constructs a stripped-down engine with `r535_sec2` callbacks, and constructs only the falcon wrapper. `r535_sec2_dtor()` destroys the falcon.

## Control flow, state, and persistence
No SEC2 init, fini, queue manager, command queue, message queue, or interrupt handling is installed. The object preserves enough nvkm engine/falcon identity for other code paths without attempting to manage firmware that GSP RM controls.

## Dependencies and integration points
Called by TU102 and GA102 constructors when `nvkm_gsp_rm(device->gsp)` is true. Depends on the generation-provided `nvkm_sec2_func.flcn` table for falcon register behavior.

## Risks and test signals
Callers must not assume command queues exist on this path. Runtime signals are successful probe under GSP RM and absence of legacy SEC2 firmware-load attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/r535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/tu102.c

## Purpose
Implements Turing TU10x/TU11x SEC2 support using the shared GP102 interrupt/init-message logic with Turing queue offsets and v2 SEC2 unit ids.

## Important APIs, types, and functions
`tu102_sec2_new()` selects the R535 path under GSP RM or calls `nvkm_sec2_new_()` at `0x840000`. `tu102_sec2_flcn` defines GM200-style PIO, GP102 EMEM, queue registers at `0xc00/0xc80`, bind support, and falcon v1 start. `tu102_sec2` supplies unit ids `NV_SEC2_UNIT_V2_UNLOAD` and `NV_SEC2_UNIT_V2_ACR`.

## Control flow, state, and persistence
Runtime lifecycle is common SEC2. Firmware loading uses `gp102_sec2_load` and ACR descriptor v1 callbacks. Init-message parsing and interrupt handling are inherited from GP102.

## Dependencies and integration points
Depends on ACR, GSP detection, and TU102-TU117 SEC2 firmware blobs. Integrated with ACR as the RTOS falcon that can bootstrap FECS, GPCCS, and SEC2.

## Risks and test signals
The hard-coded PRI address compensates for inaccurate TOP data. Signals include firmware load, queue init, ACR bootstrap, and correct bypass to `r535_sec2_new()` under GSP RM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sec2/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/Kbuild

## Purpose
Builds the Nouveau software engine implementation and generation-specific software classes.

## Important APIs, types, and functions
Compiles `base.o`, generation files `nv04.o`, `nv10.o`, `nv50.o`, `gf100.o`, plus shared `chan.o` and `nvsw.o`.

## Control flow, state, and persistence
No runtime logic. It determines which software FIFO class constructors and method handlers are present in the module.

## Dependencies and integration points
Included by the engine-level Kbuild. These objects integrate with FIFO, display vblank events, BAR flushes, and NVIF software class APIs.

## Risks and test signals
Omitting a generation file removes software class support for that GPU family. Build success and class enumeration through NVIF are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/base.c

## Purpose
Implements the common Nouveau software engine. It tracks per-FIFO software channels and dispatches software methods to channel-specific handlers.

## Important APIs, types, and functions
`nvkm_sw_new_()` allocates and constructs `struct nvkm_sw`. `nvkm_sw_mthd()` finds a channel by FIFO id and dispatches a method. `nvkm_sw_oclass_get()` exposes software object classes. `nvkm_sw_cclass_get()` creates per-channel software contexts through generation functions.

## Control flow, state, and persistence
The engine owns `sw->chan`, a list of active `nvkm_sw_chan` objects protected by `engine.lock`. Method dispatch scans for the matching channel id, calls `nvkm_sw_chan_mthd()`, and moves the channel to the list head as a locality optimization. State persists for the engine lifetime and per-channel object lifetime.

## Dependencies and integration points
Depends on FIFO channels, the nvkm object/class model, and generation-provided `nvkm_sw_func`. Integrated by FIFO when users create software channel classes.

## Risks and test signals
Wrong locking or stale list entries can misroute methods. Signals include successful software class creation, page-flip event delivery, and handled return values for SW methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/chan.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/chan.c

## Purpose
Provides the common software-channel object, baseline method dispatch, event setup, and destruction logic.

## Important APIs, types, and functions
`nvkm_sw_chan_ctor()` initializes the object, links it into `sw->chan`, and creates a one-type event source. `nvkm_sw_chan_mthd()` handles method `0x0000` as a no-op and method `0x0500` as a page-flip event notification, then delegates other methods to the generation callback. `nvkm_sw_chan_dtor()` calls optional generation cleanup, finalizes events, and unlinks the channel.

## Control flow, state, and persistence
Each channel stores its FIFO pointer, software engine pointer, function table, list node, and event object. Page-flip methods notify `NVKM_SW_CHAN_EVENT_PAGE_FLIP`. State is destroyed when the object is released.

## Dependencies and integration points
Depends on `core/event`, FIFO channels, NVIF event constants, and generation method handlers such as NV50/GF100 vblank semaphore support.

## Risks and test signals
Event finalization must race safely with notification users. Test signals include userspace page-flip events and clean channel teardown without list corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/chan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/chan.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/chan.h

## Purpose
Declares the private software-channel type and method/event hooks shared by SW engine implementations.

## Important APIs, types, and functions
`struct nvkm_sw_chan` contains the nvkm object, parent software engine, FIFO channel, list node, and event object. `struct nvkm_sw_chan_func` provides optional destructor and method callbacks. The header declares `nvkm_sw_chan_ctor()` and `nvkm_sw_chan_mthd()`, and defines `NVKM_SW_CHAN_EVENT_PAGE_FLIP`.

## Control flow, state, and persistence
No code runs here. The declarations define per-channel state persisted while a software channel object is live.

## Dependencies and integration points
Includes core object/event headers and `priv.h`. Used by `chan.c`, generation SW files, and `nvsw.c`.

## Risks and test signals
ABI changes affect all generation files. Build coverage catches most signature drift; runtime page-flip event delivery validates event bit wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/chan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/gf100.c

## Purpose
Implements GF100-class software engine behavior, primarily vblank semaphore release and a small set of performance-monitoring register methods.

## Important APIs, types, and functions
`gf100_sw_new()` constructs the engine. `gf100_sw_chan_new()` creates `nv50_sw_chan`-based channels and registers vblank notifications. `gf100_sw_chan_mthd()` handles high/low 40-bit semaphore address, semaphore value, vblank-head arm, and methods `0x600`, `0x644`, and `0x6ac`. `gf100_sw_chan_vblsem_release()` writes semaphore release registers.

## Control flow, state, and persistence
Users program semaphore address/value through SW methods, then arm a vblank index. On vblank, the notification callback writes the FIFO instance, flushes BAR, writes semaphore address/value registers, and drops the notification. Channel state stores the semaphore offset and value.

## Dependencies and integration points
Depends on display vblank events, BAR flushing, FIFO instance memory, and `NVIF_CLASS_SW_GF100`.

## Risks and test signals
Semaphore writes are hardware-register sensitive, and method validation for `0x644` prevents invalid bits. Signals include vblank semaphore completion, display event registration, and no unhandled SW methods for expected userspace paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv04.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv04.c

## Purpose
Implements NV04 software engine support, including a simple reference value method exposed through the NV04 software object.

## Important APIs, types, and functions
`nv04_sw_new()` constructs the engine. `nv04_sw_chan_new()` allocates a channel with an atomic `ref`. `nv04_sw_chan_mthd()` handles method `0x0150` by setting `ref`. `nv04_nvsw_mthd_get_ref()` implements `NV04_NVSW_GET_REF` and returns the current value through NVIF unpacked arguments.

## Control flow, state, and persistence
The channel's `ref` starts at zero, is set by pushbuffer method `0x0150`, and is queried through an object method. State persists for the channel lifetime in `atomic_t ref`.

## Dependencies and integration points
Depends on NVIF class `NVIF_CLASS_SW_NV04`, `if0004` argument layouts, ioctl/unpack helpers, and generic software channel construction.

## Risks and test signals
The query ABI must match userspace. Signals include successful `GET_REF` ioctl/object method calls and correct values after SW method submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv10.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv10.c

## Purpose
Implements NV10 software engine support as a thin wrapper around the generic software channel and generic NVSW object.

## Important APIs, types, and functions
`nv10_sw_new()` constructs the engine. `nv10_sw_chan_new()` allocates a plain `nvkm_sw_chan` and calls `nvkm_sw_chan_ctor()`. The `nv10_sw` function table exposes `NVIF_CLASS_SW_NV10` through `nvkm_nvsw_new`.

## Control flow, state, and persistence
Runtime behavior is inherited from `chan.c` and `nvsw.c`: no-op method handling, page-flip event notification, and generic object event registration. No generation-specific per-channel fields are added.

## Dependencies and integration points
Depends on NVIF class registration and common SW object/channel helpers. Integrated through FIFO channel software class creation.

## Risks and test signals
Low risk compared with later generations. Build and class-enumeration coverage verify the constructor; runtime page-flip event delivery verifies generic dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv50.c

## Purpose
Implements NV50 software engine support, including vblank semaphore programming through software methods.

## Important APIs, types, and functions
`nv50_sw_new()` constructs the engine. `nv50_sw_chan_new()` creates an `nv50_sw_chan` and registers display vblank notifications. `nv50_sw_chan_mthd()` handles context DMA, semaphore offset/value, and vblank-head arm methods. `nv50_sw_chan_vblsem_release()` writes the semaphore release sequence. `nv50_sw_chan_dtor()` unregisters notifications.

## Control flow, state, and persistence
Userspace programs `ctxdma`, `offset`, and `value`, then arms a display head. On vblank, the callback writes FIFO instance and context DMA, flushes BAR, and writes the semaphore location/value using chipset-specific registers for NV50 versus later NV50-family chips.

## Dependencies and integration points
Depends on display vblank events, FIFO instance memory, BAR flushing, GPU object support, and `NVIF_CLASS_SW_NV50`.

## Risks and test signals
Register differences for chipset `0x50` are compatibility-sensitive. Signals include vblank semaphore updates, notification add/delete balance, and correct page-flip synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv50.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv50.h

## Purpose
Defines the shared NV50/GF100 software-channel extension used for vblank semaphore handling.

## Important APIs, types, and functions
`struct nv50_sw_chan` embeds `struct nvkm_sw_chan` and a `vblank` substructure with four notification slots, context DMA, semaphore offset, and value. It declares `nv50_sw_chan_dtor()` for notification cleanup.

## Control flow, state, and persistence
No code runs here. The structure holds per-channel semaphore state programmed by generation method handlers and consumed by vblank callbacks.

## Dependencies and integration points
Includes software private headers, `chan.h`, `nvsw.h`, and core event support. Shared by `nv50.c` and `gf100.c`.

## Risks and test signals
The fixed notification array assumes up to four heads. Runtime testing should cover all display heads supported by the device and cleanup under channel destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nv50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nvsw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nvsw.c

## Purpose
Implements the generic NVSW software object attached to a software channel. It provides object methods and uevent registration.

## Important APIs, types, and functions
`nvkm_nvsw_new_()` and `nvkm_nvsw_new()` allocate objects. `nvkm_nvsw_mthd()` delegates object methods to an optional `nvkm_nvsw_func`. `nvkm_nvsw_uevent()` subscribes userspace uevents to the channel page-flip event.

## Control flow, state, and persistence
Object creation stores the function table and owning `nvkm_sw_chan`. Method calls are forwarded if a generation-specific handler exists, otherwise return `-ENODEV`. Uevent setup validates argument size and adds a listener for `NVKM_SW_CHAN_EVENT_PAGE_FLIP`.

## Dependencies and integration points
Depends on `if0004` event argument ABI, `nvkm_uevent_add()`, and channel events from `chan.c`. Used by NV10, NV50, GF100, and by NV04 through a custom method table.

## Risks and test signals
Argument-size mismatch returns `-ENOSYS`; method absence returns `-ENODEV`. Test signals are page-flip event delivery and NV04 custom method forwarding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nvsw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nvsw.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nvsw.h

## Purpose
Declares the private NVSW object used by software-channel classes.

## Important APIs, types, and functions
`struct nvkm_nvsw` embeds `struct nvkm_object`, a function table, and the owning software channel. `struct nvkm_nvsw_func` provides an optional object-method callback. The header declares generic and custom constructors.

## Control flow, state, and persistence
No runtime logic exists in the header. The object persists as a child of a software channel and uses the channel for events and generation state.

## Dependencies and integration points
Includes core object support and is used by SW generation files plus `nvsw.c`.

## Risks and test signals
Any signature change affects all software class constructors. Build coverage and userspace SW object creation are the main validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nvsw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/priv.h

## Purpose
Defines the private software-engine function table and constructor shared by all Nouveau SW engine implementations.

## Important APIs, types, and functions
`struct nvkm_sw_func` contains a per-channel constructor and an array of software object classes. `struct nvkm_sw_chan_sclass` pairs a channel object constructor with an `nvkm_sclass`. `nvkm_sw_new_()` constructs a software engine from a function table.

## Control flow, state, and persistence
No code runs here. The structures drive class enumeration, per-FIFO channel creation, and SW object construction in `base.c`.

## Dependencies and integration points
Includes public `engine/sw.h` and forward declares `nvkm_sw_chan`. Used by all files in `engine/sw`.

## Risks and test signals
Incorrect class arrays or constructors surface as missing NVIF software classes. Build coverage catches structural signature drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vic/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vic/Kbuild

## Purpose
Documents the disabled build hook for the Nouveau VIC engine.

## Important APIs, types, and functions
The only object entry, `nvkm/engine/vic/base.o`, is commented out.

## Control flow, state, and persistence
No runtime code is compiled from this directory in the current configuration.

## Dependencies and integration points
Included by the engine Kbuild, but it contributes no objects. It indicates an intended or historical VIC engine slot.

## Risks and test signals
Because the entry is disabled, no VIC nvkm engine support is built here. Build output should not include `engine/vic/base.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vic/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vp/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vp/Kbuild

## Purpose
Builds the Nouveau VP engine implementation for G84-era video processing hardware.

## Important APIs, types, and functions
Adds `nvkm/engine/vp/g84.o` to `nvkm-y`.

## Control flow, state, and persistence
No runtime logic. Build inclusion makes the G84 VP constructor and Xtensa configuration available.

## Dependencies and integration points
Included by engine-level Kbuild. The object depends on the generic Xtensa engine and VP public header.

## Risks and test signals
Omitting the entry removes VP engine support. Build logs and class exposure for `NV74_VP2` validate inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vp/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vp/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vp/g84.c

## Purpose
Defines G84 VP2 video processor support as a configuration of the generic Xtensa engine.

## Important APIs, types, and functions
`g84_vp_new()` calls `nvkm_xtensa_new_()` with `g84_vp`, enabling the engine at base `0x00f000`. The `g84_vp` function table sets `fifo_val`, `unkd28`, and exposes class `NV74_VP2`.

## Control flow, state, and persistence
Runtime lifecycle is inherited from `xtensa.c`: firmware load, region setup, interrupts, and FIFO control. This file only provides chip-specific constants and class information.

## Dependencies and integration points
Depends on `engine/vp.h`, `engine/xtensa.h`, and NVIF class definitions. Integrated by chipset engine tables for G84-family VP hardware.

## Risks and test signals
The magic register constants must match the VP2 engine. Signals include firmware request name derived from the Xtensa address, successful init, and VP2 class creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/vp/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/xtensa.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/xtensa.c

## Purpose
Implements a generic Xtensa-backed engine wrapper used by VP-like engines. It loads firmware into instance memory, programs engine memory regions, handles interrupts, and exposes engine classes.

## Important APIs, types, and functions
`nvkm_xtensa_new_()` constructs the engine. `nvkm_xtensa_init()` loads `nouveau/nv84_xuc%03x`, allocates firmware memory, writes firmware words, and programs region registers. `nvkm_xtensa_fini()` disables interrupts/FIFO and frees firmware on poweroff. `nvkm_xtensa_intr()` clears interrupts and enables FIFO control after a specific engine-ready state. `nvkm_xtensa_cclass_bind()` allocates channel context objects.

## Control flow, state, and persistence
The firmware image is cached in `xtensa->gpu_fw` until poweroff. Init programs interrupt masks, region base/limit/setup, scratch state, and engine constants. Interrupt handling reports watchdog hangs and toggles FIFO control when readiness registers match expected values.

## Dependencies and integration points
Depends on firmware loading, instance memory, GPU objects, FIFO class binding, and chip-specific `nvkm_xtensa_func`. Used by `engine/vp/g84.c`.

## Risks and test signals
Firmware size is capped at `0x40000`; missing firmware prevents init. Signals include firmware load warnings, watchdog interrupt logs, FIFO_CTRL enable debug logs, and successful class/context binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/xtensa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/Kbuild

## Purpose
Builds the shared Nouveau falcon support library and generation-specific falcon operations.

## Important APIs, types, and functions
Compiles common objects `base.o`, `cmdq.o`, `fw.o`, `msgq.o`, `qmgr.o`, `v1.o` and generation files `gm200.o`, `gp102.o`, `tu102.o`, `ga100.o`, `ga102.o`.

## Control flow, state, and persistence
No runtime logic. Build inclusion makes generic falcon access, firmware boot, queues, and generation-specific register helpers available to SEC2, ACR, PMU, GSP, and other falcon users.

## Dependencies and integration points
Included by nvkm Kbuild. These files depend on core falcon structures, firmware parsers, memory/VMM, MC, timer, and subdev owners.

## Risks and test signals
Missing objects cause broad link or runtime failures. Build success plus SEC2/ACR/PMU firmware boot validate coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/base.c

## Purpose
Provides generic falcon ownership, memory transfer, start/reset, and discovery helpers. Falcon is NVIDIA's small embedded controller core used by SEC2, PMU, GSP, and other units.

## Important APIs, types, and functions
Key APIs include `nvkm_falcon_get()`, `nvkm_falcon_put()`, `nvkm_falcon_ctor()`, `nvkm_falcon_dma_wr()`, `nvkm_falcon_pio_rd()`, `nvkm_falcon_pio_wr()`, `nvkm_falcon_load_imem()`, `nvkm_falcon_load_dmem()`, `nvkm_falcon_start()`, `nvkm_falcon_reset()`, `nvkm_falcon_intr_retrigger()`, and `nvkm_falcon_riscv_active()`.

## Control flow, state, and persistence
`get()` serializes ownership, performs one-time discovery from TOP/MMIO, records version, secret capability, port counts, IMEM/DMEM limits, and optional debug state. DMA and PIO helpers select memory backends, validate alignment, transfer chunks, poll completion, and optionally trace data. DMEM loads are protected by `dmem_mutex`.

## Dependencies and integration points
Depends on generation `nvkm_falcon_func`, TOP, MC/timer helpers, and register access. Used by firmware boot, SEC2 queues, ACR WPR building, and all falcon-backed engines.

## Risks and test signals
Ownership misuse returns `-EBUSY`; alignment/length mistakes trigger warnings. Signals include falcon acquisition logs, transfer timeouts, and successful firmware start/boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/cmdq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/cmdq.c

## Purpose
Implements host-to-falcon command queues used by firmware RTOS interfaces such as SEC2 ACR commands and unload requests.

## Important APIs, types, and functions
`nvkm_falcon_cmdq_new()`, `nvkm_falcon_cmdq_init()`, `nvkm_falcon_cmdq_send()`, `nvkm_falcon_cmdq_fini()`, and `nvkm_falcon_cmdq_del()` manage command queues. Internal helpers check room, open/close the ring, push data to DMEM, and insert rewind commands.

## Control flow, state, and persistence
Queue readiness is completion-based and established from firmware init messages. Send waits for readiness, acquires a sequence, stamps `seq_id` and status/interrupt flags, writes the command ring, and either waits for a reply completion or leaves an async sequence. Ring space is computed from firmware head/tail registers with 4-byte alignment and rewind support.

## Dependencies and integration points
Depends on falcon DMEM PIO writes, queue manager sequence tracking, `nvfw_falcon_cmd`, completions, mutexes, and firmware message queues.

## Risks and test signals
Queue full or reply timeout returns errors. Signals include queue init debug logs, timeout waiting for queue space/ready/reply, and successful SEC2 command callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/cmdq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/fw.c

## Purpose
Implements falcon firmware object construction, signature patching, VMM mapping, high-secure firmware parsing, loading, booting, and cleanup.

## Important APIs, types, and functions
Key APIs include `nvkm_falcon_fw_ctor()`, `nvkm_falcon_fw_ctor_hs()`, `nvkm_falcon_fw_ctor_hs_v2()`, `nvkm_falcon_fw_oneinit()`, `nvkm_falcon_fw_boot()`, `nvkm_falcon_fw_sign()`, `nvkm_falcon_fw_patch()`, and `nvkm_falcon_fw_dtor()`.

## Control flow, state, and persistence
Constructors parse NVIDIA firmware headers, copy firmware images, capture bootloader code when separate, derive IMEM/DMEM/non-secure ranges, and store production/debug signatures. Boot acquires the falcon, patches the selected signature, resets, optionally runs setup, syncs DMA mappings, loads code/data, and waits for boot mailbox status. Oneinit maps firmware memory into a VMM when needed.

## Dependencies and integration points
Depends on `nvfw/fw.h`, `nvfw/hs.h`, firmware loader, DMA mapping, VMM, instance memory, and generation `nvkm_falcon_fw_func`. Used heavily by ACR high-secure firmware.

## Risks and test signals
Signature selection, patch offsets, and mailbox expected values are security-critical. Signals include boot mailbox logs, firmware parsing debug, patch trace, and boot failure errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/ga100.c

## Purpose
Provides GA100-family helpers for interrupt retriggering and production signature selection based on fuse versions.

## Important APIs, types, and functions
`ga100_flcn_intr_retrigger()` writes falcon register `0x3e8` to retrigger interrupts. `ga100_flcn_fw_signature()` chooses a signature index using firmware engine id, ucode id, firmware fuse version, and hardware fuse registers.

## Control flow, state, and persistence
Signature selection reads one of several fuse-register banks based on engine id bits, converts a nonzero fuse mask to `fls()` version, verifies firmware fuse version is high enough, and returns the offset index. If no fuse bits are set, it chooses the last signature.

## Dependencies and integration points
Depends on falcon firmware metadata filled by HS v2 parsing and device MMIO. Used by GA102 falcon firmware and GA102 ACR LS secure-bootloader signature patching.

## Risks and test signals
Wrong signature selection prevents secure firmware boot. Signals include fuse/debug logs and boot failures from later firmware validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/ga102.c

## Purpose
Implements GA102-generation falcon DMA, selection/reset quirks, RISC-V activity detection, and HS firmware load/boot operations.

## Important APIs, types, and functions
Exports `ga102_flcn_dma`, `ga102_flcn_riscv_active()`, `ga102_flcn_reset_wait_mem_scrubbing()`, `ga102_flcn_reset_prep()`, `ga102_flcn_select()`, `ga102_flcn_fw_load()`, `ga102_flcn_fw_boot()`, and `ga102_flcn_fw`.

## Control flow, state, and persistence
DMA init programs source address and command bits for IMEM/DMEM and secure transfers; DMA writes poll bit `0x2` in register `0x118`. Selection clears a falcon select bit and waits for ready. Firmware load enables DMA path, then transfers IMEM securely and DMEM normally. Boot writes signature, engine id, ucode id, and a start flag in the secondary register window before using GM200 mailbox boot.

## Dependencies and integration points
Depends on generic falcon DMA helpers, GM200 firmware reset/boot, GA100 signature selection, and generation-specific secondary register window `addr2`.

## Risks and test signals
DMA alignment and select handshakes can timeout. Signals include firmware load/boot success, RISC-V active bit checks, and reset memory-scrubbing timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/gm200.c

## Purpose
Provides Maxwell GM200-era falcon operations used as the base for many SEC2/ACR/PMU firmware paths.

## Important APIs, types, and functions
Defines DMEM/IMEM PIO functions, `gm200_flcn_tracepc()`, bind helpers, memory-scrubbing wait, `gm200_flcn_enable()`, `gm200_flcn_disable()`, `gm200_flcn_fw_reset()`, `gm200_flcn_fw_load()`, `gm200_flcn_fw_boot()`, and `gm200_flcn_fw_signature()`.

## Control flow, state, and persistence
Enable optionally resets engine, selects the falcon, enables MC gating, waits for scrubbing, and writes a scratch register. Disable clears control/interrupts and may disable MC. Firmware boot writes mailboxes, boot address, starts execution, waits for halt/done, validates mailbox status, and clears requested interrupts. Firmware load handles either virtual instance mapping or direct PIO bootloader/IMEM/DMEM writes.

## Dependencies and integration points
Depends on memory target mapping, MC control, timers, falcon PIO helpers, and firmware metadata. Reused by SEC2, ACR, and later falcon variants.

## Risks and test signals
Mailbox status mismatch and scrubbing timeouts are common failure points. Signals include TRACEPC on halt, boot mailbox logs, and firmware load/boot return codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/gp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/gp102.c

## Purpose
Adds GP102 falcon extensions for EMEM PIO access and engine reset.

## Important APIs, types, and functions
`gp102_flcn_emem_pio` provides EMEM read/write operations through registers `0xac0/0xac4`. `gp102_flcn_reset_eng()` asserts and deasserts the engine reset bit at `0x3c0`, with optional reset preparation and memory-scrubbing wait.

## Control flow, state, and persistence
EMEM PIO initializes read/write ports with bit 25 or bit 24 plus the EMEM base, then transfers 32-bit words. Engine reset calls generation `reset_prep`, toggles reset for 10 microseconds, and waits for memory scrubbing.

## Dependencies and integration points
Used by GP102/TU102 SEC2 falcon function tables for extended memory access and engine reset. Depends on generic falcon register access and generation reset-wait callbacks.

## Risks and test signals
EMEM operations require 4-byte alignment. Reset timeouts indicate hardware or select sequencing problems. Signals include SEC2 queue memory access success and reset timeout logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/msgq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/msgq.c

## Purpose
Implements falcon-to-host message queues and response dispatch for firmware command sequences.

## Important APIs, types, and functions
`nvkm_falcon_msgq_new()`, `nvkm_falcon_msgq_init()`, `nvkm_falcon_msgq_empty()`, `nvkm_falcon_msgq_recv()`, `nvkm_falcon_msgq_recv_initmsg()`, and `nvkm_falcon_msgq_del()` manage message queues. Internal helpers open/close the ring, pop data from DMEM, read complete messages, and execute sequence callbacks.

## Control flow, state, and persistence
Message receive locks the queue, reads head/tail, handles wraparound, validates available bytes and maximum message size, then commits the tail. Normal messages are matched by `seq_id` to queue-manager sequences, invoke callbacks, release async sequences, or complete synchronous waits. Init messages use initial registers before the firmware reports final queue indices.

## Dependencies and integration points
Depends on falcon DMEM PIO reads, queue manager sequence state, firmware message layouts, spinlocks, and completions. SEC2 interrupt handlers call into this path.

## Risks and test signals
Oversized messages, unknown sequences, or bad size accounting break command completion. Signals include message-too-big, unknown-sequence, init-size mismatch, and successful SEC2 command replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/msgq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/priv.h

## Purpose
Provides a private inline wrapper for enabling a falcon through its function table.

## Important APIs, types, and functions
`nvkm_falcon_enable()` calls `falcon->func->enable` when present and otherwise succeeds with zero.

## Control flow, state, and persistence
No persistent state is declared. The wrapper centralizes optional enable handling for reset and boot paths.

## Dependencies and integration points
Includes public `core/falcon.h`. Used by generic falcon reset and generation code.

## Risks and test signals
If a falcon requires enable logic but its function pointer is missing, this wrapper silently succeeds. Runtime firmware boot and register access are the validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/qmgr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/qmgr.c

## Purpose
Provides sequence-id allocation and lifetime management for falcon command/message queue pairs.

## Important APIs, types, and functions
`nvkm_falcon_qmgr_new()` allocates a queue manager and initializes 16 sequence completions. `nvkm_falcon_qmgr_seq_acquire()` finds a free sequence bit, marks it pending, and returns the sequence. `nvkm_falcon_qmgr_seq_release()` clears callback state, reinitializes completion, and frees the sequence bit.

## Control flow, state, and persistence
Sequence allocation is protected by a mutex and a bitmap. Release uses atomic `clear_bit()` without taking the mutex. Sequence records persist for the queue manager lifetime and are reused across commands.

## Dependencies and integration points
Used by `cmdq.c` and `msgq.c`. Depends on completions, bitmap helpers, mutexes, and falcon owner logging.

## Risks and test signals
Only 16 simultaneous sequences are supported; exhaustion returns `-EAGAIN`. Signals include "no free sequence available" logs and successful command/reply correlation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/qmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/qmgr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/qmgr.h

## Purpose
Declares falcon queue manager, command queue, message queue, and sequence tracking structures.

## Important APIs, types, and functions
Defines `HDR_SIZE`, `QUEUE_ALIGNMENT`, `MSG_BUF_SIZE`, `NVKM_FALCON_QMGR_SEQ_NUM`, `struct nvkm_falcon_qmgr_seq`, `struct nvkm_falcon_qmgr`, `struct nvkm_falcon_cmdq`, and `struct nvkm_falcon_msgq`. It declares sequence acquire/release and queue logging macros.

## Control flow, state, and persistence
No code runs here. Sequence states include free, pending, used, and cancelled; each sequence has callback, private data, completion, async flag, and result.

## Dependencies and integration points
Includes `core/falcon.h` for firmware command/message callback types. Shared by command, message, and queue-manager implementations.

## Risks and test signals
Message buffer size is fixed at 128 bytes; larger firmware messages fail. Build coverage catches structural drift; runtime SEC2 command completion validates queue state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/qmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/tu102.c

## Purpose
Provides TU102-specific detection for whether the falcon is running RISC-V firmware.

## Important APIs, types, and functions
`tu102_flcn_riscv_active()` reads bit `0x1` from `falcon->addr2 + 0x240`.

## Control flow, state, and persistence
There is no state mutation. The helper returns a boolean used by higher-level code to distinguish firmware execution mode.

## Dependencies and integration points
Depends on the secondary falcon register window being set in the function table. Used through `nvkm_falcon_riscv_active()`.

## Risks and test signals
Wrong `addr2` configuration makes the active check meaningless. Runtime validation is platform-specific logging or paths that branch on RISC-V mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/v1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/v1.c

## Purpose
Implements legacy falcon v1 direct IMEM/DMEM loading and start behavior.

## Important APIs, types, and functions
`nvkm_falcon_v1_load_imem()` writes IMEM through port registers, handles secure tag bits, updates tags every 256 bytes, masks a trailing partial word, and pads code to 0x40 words. `nvkm_falcon_v1_load_dmem()` writes DMEM similarly without tags. `nvkm_falcon_v1_start()` starts execution through either `0x130` or `0x100` depending on a control bit.

## Control flow, state, and persistence
The functions program falcon memory and start registers directly. No driver state persists except hardware IMEM/DMEM contents and execution state.

## Dependencies and integration points
Used by SEC and SEC2 function tables that rely on v1 falcon loading. Depends on generic falcon register access.

## Risks and test signals
Padding and partial-word masking prevent garbage code/data writes. Signals include successful microcode start and absence of falcon halt/trace errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/Kbuild

## Purpose
Builds Nouveau firmware-format parser/debug helpers for NVIDIA binary firmware structures.

## Important APIs, types, and functions
Compiles `fw.o`, `hs.o`, `ls.o`, `acr.o`, and `flcn.o`.

## Control flow, state, and persistence
No runtime logic in the Kbuild file. It controls availability of parsers and dump helpers used by falcon and ACR code.

## Dependencies and integration points
Included by nvkm build logic. Parser users include `falcon/fw.c`, `subdev/acr/*`, and `engine/sec2/*`.

## Risks and test signals
Missing parser objects break firmware construction and ACR WPR handling. Build and firmware-load paths validate inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/acr.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/acr.c

## Purpose
Provides debug dump helpers for ACR WPR, LSB, and ACR descriptor structures across multiple firmware generations.

## Important APIs, types, and functions
Functions include `wpr_header_dump()`, `wpr_header_v1_dump()`, `wpr_header_v2_dump()`, `lsb_header_dump()`, `lsb_header_v1_dump()`, `lsb_header_v2_dump()`, `flcn_acr_desc_dump()`, and `flcn_acr_desc_v1_dump()`.

## Control flow, state, and persistence
All functions are read-only formatters: they accept parsed structure pointers and log fields with `nvkm_debug()`. They do not validate ranges or mutate state.

## Dependencies and integration points
Depends on `nvfw/acr.h` structure definitions and `core/subdev` logging. Used by ACR WPR parse/build/patch and HS firmware setup code.

## Risks and test signals
Debug output can reveal bad offsets, WPR ranges, signatures, and region masks. Since the functions do not enforce correctness, validation comes from downstream boot and WPR comparison failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/acr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/flcn.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/flcn.c

## Purpose
Provides debug dump helpers for falcon bootloader and loader descriptor formats.

## Important APIs, types, and functions
Functions include `loader_config_dump()`, `loader_config_v1_dump()`, `flcn_bl_dmem_desc_dump()`, `flcn_bl_dmem_desc_v1_dump()`, and `flcn_bl_dmem_desc_v2_dump()`.

## Control flow, state, and persistence
The helpers log DMA indices, code/data bases, code sizes, entry points, signatures, non-secure/secure code regions, and arguments. They do not mutate firmware data.

## Dependencies and integration points
Depends on `nvfw/flcn.h` and subdev logging. Used by SEC2 ACR low-secure descriptor writers and ACR high-secure bootloader setup.

## Risks and test signals
Formatting mistakes affect diagnostics, not runtime behavior. The dump output is a key test signal when secure firmware fails to load or WPR bootloader data appears wrong.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/flcn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/fw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/fw.c

## Purpose
Parses and logs generic NVIDIA firmware binary and bootloader descriptor headers.

## Important APIs, types, and functions
`nvfw_bin_hdr()` returns a `struct nvfw_bin_hdr` after logging magic, version, size, header offset, data offset, and data size. `nvfw_bl_desc()` returns a `struct nvfw_bl_desc` after logging bootloader start tag, DMEM load offset, code/data offsets, and sizes.

## Control flow, state, and persistence
Both functions are pointer-cast parsers and debug dumpers. They do not allocate, validate bounds, or persist state.

## Dependencies and integration points
Used by `falcon/fw.c` HS constructors and ACR low-secure firmware loaders. Depends on `nvfw/fw.h` definitions and subdev debug logging.

## Risks and test signals
Callers must ensure input buffers are large enough. Debug logs help diagnose firmware format mismatch, wrong offsets, and missing bootloader regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/hs.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/hs.c

## Purpose
Parses and logs high-secure falcon firmware headers and load headers.

## Important APIs, types, and functions
`nvfw_hs_header()` and `nvfw_hs_header_v2()` expose signature offsets/sizes, patch locations, metadata offsets, signature count, and header offsets. `nvfw_hs_load_header()` and `_v2()` expose non-secure/OS code/data ranges and app ranges.

## Control flow, state, and persistence
The functions only cast input bytes to known structures, emit debug fields, and return the typed pointer. No allocation or mutation is done.

## Dependencies and integration points
Used by `nvkm_falcon_fw_ctor_hs()` and `_hs_v2()` to derive signature patching and IMEM/DMEM layout. Depends on `nvfw/hs.h`.

## Risks and test signals
No bounds checking is performed here, so firmware loader callers must trust loaded blobs. Debug output is central for HS firmware layout mismatch investigations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/hs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/ls.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/ls.c

## Purpose
Parses and logs low-secure firmware descriptors and secure bootloader signature headers used in ACR WPR images.

## Important APIs, types, and functions
`nvfw_ls_desc()`, `_v1()`, and `_v2()` expose bootloader/app offsets, sizes, resident code/data layout, overlay counts, secure bootloader metadata, and app IMEM/DMEM offsets. `nvfw_ls_hsbl_bin_hdr()` and `nvfw_ls_hsbl_hdr()` parse HS bootloader signature containers.

## Control flow, state, and persistence
The helpers log descriptor fields and return typed pointers. They allocate only temporary strings for dates and free them immediately. No firmware state is persisted here.

## Dependencies and integration points
Used by `subdev/acr/lsfw.c` to convert firmware descriptors into `nvkm_acr_lsfw` layout. Depends on `nvfw/ls.h` and subdev logging.

## Risks and test signals
Descriptor interpretation feeds WPR layout and secure signature patching. Test signals include debug dumps, WPR comparison output, and successful low-secure falcon bootstrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/nvfw/ls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/Kbuild

## Purpose
Aggregates Nouveau nvkm subdevice build fragments.

## Important APIs, types, and functions
Includes Kbuild files for ACR, BAR, BIOS, bus, clock, devinit, fault, FB, fuse, GPIO, FSP, GSP, I2C, instance memory, LTC, MC, MMU, MXM, PCI, PMU, privring, therm, timer, TOP, VFN, and volt.

## Control flow, state, and persistence
There is no runtime logic. Build ordering and inclusion determine available subdevice constructors.

## Dependencies and integration points
This file is the integration point from top-level nvkm build logic into individual subdev directories, including the ACR and BAR subdirectories researched in this group.

## Risks and test signals
Missing includes remove entire subdevice families. Build logs and module link success are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/Kbuild

## Purpose
Builds the Nouveau ACR subdevice core, low-secure firmware loader, and generation-specific ACR implementations.

## Important APIs, types, and functions
Compiles `base.o`, `lsfw.o`, `gm200.o`, `gm20b.o`, `gp102.o`, `gp108.o`, `gv100.o`, `gp10b.o`, `tu102.o`, `ga100.o`, and `ga102.o`.

## Control flow, state, and persistence
No runtime logic. It determines which WPR builders, HS firmware loaders, and chipset constructors are linked.

## Dependencies and integration points
Included by `nvkm/subdev/Kbuild`. Objects depend on falcon firmware support, SEC2/PMU/GSP, memory/VMM, and firmware parsers.

## Risks and test signals
Omitting generation files breaks secure boot on those chips. Build success and ACR subdev probe/firmware boot validate inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/base.c

## Purpose
Implements the common ACR subdevice. ACR prepares protected WPR firmware images, boots high-secure firmware, tracks low-secure falcons, and brokers falcon bootstrapping.

## Important APIs, types, and functions
Exports `nvkm_acr_bootstrap_falcons()`, `nvkm_acr_managed_falcon()`, `nvkm_acr_hsfw_boot()`, and `nvkm_acr_new_()`. Core callbacks include oneinit/load/fini/dtor paths, WPR firmware parsing via `nvkm_acr_ctor_wpr()`, and cleanup helpers.

## Control flow, state, and persistence
Oneinit loads/filters low-secure firmware records, orders the RTOS falcon first, culls unbootstrappable falcons, computes or imports WPR layout, allocates WPR memory, builds/patches the WPR image, creates ACR instance/VMM state, maps HS firmware, and discards temporary blobs. Init boots ACR if an RTOS LSF exists. Fini unloads via HS firmware and drops RTOS references.

## Dependencies and integration points
Depends on firmware loader, options `NvAcrWpr*`, memory/VMM, SEC2/PMU/GSP falcons, ACR generation function tables, and falcon firmware boot.

## Risks and test signals
WPR range mismatch, unsupported bootstrap masks, or bad patch adjustment can leave secure engines unusable. Signals include WPR debug ranges, comparison warnings, ACR boot errors, and successful bootstrap requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/ga100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/ga100.c

## Purpose
Provides Ampere GA100-style ACR helper functions for WPR range checking and HS firmware construction using HS v2 firmware format.

## Important APIs, types, and functions
`ga100_acr_wpr_check()` reads WPR start/limit from registers `0x1fa81c` and `0x1fa820`. `ga100_acr_hsfw_ctor()` allocates an HS firmware record and constructs it through `nvkm_falcon_fw_ctor_hs_v2()`.

## Control flow, state, and persistence
The constructor records HS falcon id, boot mailbox, interrupt-clear mask, links the record to `acr->hsfw`, and parses the named HS firmware image. WPR check returns a half-open region with an added `0x20000` limit granularity.

## Dependencies and integration points
Used by GA102 ACR firmware tables. Depends on falcon HS v2 constructor, ACR private structures, and device MMIO.

## Risks and test signals
Incorrect WPR range reads cause ACR load rejection. Signals include WPR configured-as-expected checks and HS v2 firmware parse/boot success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/ga100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/ga102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/ga102.c

## Purpose
Implements GA10x ACR support using WPR header v2, GSPLITE bootstrap ownership, HS v2 firmware, and optional secure low-secure bootloader signatures.

## Important APIs, types, and functions
Key functions are `ga102_acr_wpr_layout()`, `ga102_acr_wpr_build()`, `ga102_acr_wpr_build_lsb()`, `ga102_acr_wpr_patch()`, `ga102_acr_wpr_parse()`, `ga102_acr_load()`, and `ga102_acr_new()`. The `ga102_acr` function table uses `tu102_acr_init`, `ga100_acr_wpr_check`, and `gp102_acr_wpr_alloc`.

## Control flow, state, and persistence
Load collects AHESASC, ASB, and unload HS firmware. Layout reserves v2 WPR headers, shared sub-WPR terminator, LSB headers, images, and bootloader data. Build emits v2 WPR headers, v2 LSB headers, low-secure images, and bootloader descriptors. Secure bootloader LSBs patch PKC signatures using GA100 fuse selection.

## Dependencies and integration points
Depends on GSP detection, GA102 falcon firmware ops, ACR/LS/FLCN nvfw structures, SEC2/GSP HS firmware, and ACR LS firmware records.

## Risks and test signals
GSP RM disables this path. v2 header offsets and secure signature metadata are fragile. Signals include HS firmware load, WPR comparison, AHESASC/ASB boot, and bootstrap success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/ga102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gm200.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gm200.c

## Purpose
Implements GM200/GM20x/GP100 ACR support and common v0 WPR helpers used by later implementations.

## Important APIs, types, and functions
Defines empty fallback `gm200_acr`, `gm200_acr_nofw()`, `gm200_acr_init()`, WPR parse/layout/build/patch/check helpers, `gm200_acr_hsfw_ctor()`, `gm200_acr_hsfw_load_bld()`, and firmware functions for load/unload HS firmware.

## Control flow, state, and persistence
WPR layout reserves fixed WPR headers, per-LSF LSB headers, images, and bootloader data. Build writes each WPR header with PMU bootstrap ownership, emits LSBs and images, then terminates. Init boots the "load" HS firmware. Setup writes WPR region permissions into the ACR descriptor. Unload firmware is registered separately.

## Dependencies and integration points
Depends on PMU falcon HS firmware, memory allocation, nvfw ACR/FLCN dump helpers, and firmware blobs for GM200/GM204/GM206/GP100.

## Risks and test signals
WPR permissions and region registers are security-sensitive. Signals include WPR range readback, ACR descriptor debug, load/unload mailbox success, and FECS/GPCCS bootstrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gm200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gm20b.c

## Purpose
Implements Tegra GM20B ACR support, where WPR is preconfigured by firmware/registers and the driver allocates only the ucode blob.

## Important APIs, types, and functions
`gm20b_acr_wpr_alloc()` checks existing WPR bounds and allocates instance memory for the image. `gm20b_acr_hsfw_load_bld()` writes a v0 bootloader descriptor with shifted DMA bases. `gm20b_acr_load_setup()` fills `ucode_blob_base` and `ucode_blob_size`. `gm20b_acr_load()` loads only the load HS firmware.

## Control flow, state, and persistence
The function table reuses GM200 WPR parse/layout/build/patch/check and init. Load setup points the ACR firmware at the allocated ucode blob rather than programming WPR region properties.

## Dependencies and integration points
Depends on Tegra firmware declarations guarded by `CONFIG_ARCH_TEGRA_210_SOC`, PMU falcon HS firmware, and GM200 common WPR helpers.

## Risks and test signals
If the existing WPR is too small, init returns `-ENOSPC`. Signals include "WPR image too big" logs, ACR descriptor dump, and successful load firmware boot on Tegra.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp102.c

## Purpose
Implements Pascal GP10x ACR support using SEC2 as the HS load falcon, WPR header v1, shadow WPR memory, and updated descriptors.

## Important APIs, types, and functions
Exports `gp102_acr_wpr_parse()`, `gp102_acr_wpr_layout()`, `gp102_acr_wpr_alloc()`, `gp102_acr_wpr_build()`, `gp102_acr_wpr_build_lsb()`, `gp102_acr_wpr_patch()`, `gp102_acr_load_setup()`, `gp102_acr_load()`, and `gp102_acr_new()`.

## Control flow, state, and persistence
Allocation creates a double-sized instance memory block, using the first half as shadow and second half as WPR. Build writes v1 WPR headers with SEC2 bootstrap ownership and firmware version from signatures. Setup fills an ACR descriptor v1 with WPR and shadow start addresses. Load registers load and unload HS firmware blobs, with unload boot mailbox `0x1d`.

## Dependencies and integration points
Depends on SEC2, ACR nvfw descriptors, GM200 common load/unload helpers, and GP102-GP107 ACR firmware blobs.

## Risks and test signals
Shadow/WPR address adjustment is critical for patching. Signals include descriptor dumps with shadow address, WPR readback, and SEC2-based ACR load/unload success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp108.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp108.c

## Purpose
Specializes ACR support for GP108 with v2 falcon bootloader descriptors while reusing the GP102 WPR model.

## Important APIs, types, and functions
`gp108_acr_hsfw_load_bld()` writes `flcn_bl_dmem_desc_v2`. `gp108_acr_hsfw_0` and `gp108_acr_load_0` provide unload/load HS firmware functions. `gp108_acr_new()` constructs the ACR subdev with GP108 firmware tables.

## Control flow, state, and persistence
The function table reuses GP102 WPR parse/layout/alloc/build/patch/check and GM200 init. Load uses `gp102_acr_load()` but with GP108-specific load/unload firmware paths and bootloader descriptor writer.

## Dependencies and integration points
Depends on GP102 ACR setup, GM200 falcon firmware reset/load/boot, and firmware blobs under `nvidia/gp108/acr`.

## Risks and test signals
Descriptor v2 field widths and argument fields must match firmware. Signals include bootloader descriptor debug dumps and successful ACR load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp10b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp10b.c

## Purpose
Implements Tegra GP10B ACR support as a variant of GM20B with GP10B firmware names.

## Important APIs, types, and functions
`gp10b_acr_new()` constructs the ACR subdev using `gp10b_acr_fwif`. The function table uses GM20B load firmware functions and GM200 WPR helpers, with Tegra guarded MODULE_FIRMWARE declarations.

## Control flow, state, and persistence
Runtime behavior follows GM20B: use existing WPR bounds, build GM200-style WPR structures, boot load HS firmware, and do not register unload firmware.

## Dependencies and integration points
Depends on `CONFIG_ARCH_TEGRA_186_SOC` firmware availability, GM20B load setup, and GM200 WPR helpers.

## Risks and test signals
Firmware is only declared for Tegra 186 builds. Signals include WPR-size checks, firmware load success, and ACR load boot on GP10B platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gp10b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gv100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gv100.c

## Purpose
Defines GV100 ACR firmware tables while reusing GP102 WPR mechanics and GP108 v2 bootloader descriptor functions.

## Important APIs, types, and functions
`gv100_acr_new()` constructs the ACR subdev. `gv100_acr` uses GP102 WPR parse/layout/alloc/build/patch/check and GM200 init, with load/unload firmware function arrays referencing `gp108_acr_load_0` and `gp108_acr_hsfw_0`.

## Control flow, state, and persistence
Load is delegated to `gp102_acr_load()` using GV100 firmware paths. The runtime ACR lifecycle remains the common base path plus GP102 WPR image construction.

## Dependencies and integration points
Depends on GV100 firmware blobs, GP102 ACR helpers, and GP108 HS firmware descriptor writer.

## Risks and test signals
Wrong reuse of bootloader descriptor format would fail HS firmware boot. Signals include GV100 ACR firmware load, descriptor debug output, and bootstrap success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/gv100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/lsfw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/lsfw.c

## Purpose
Loads and tracks low-secure firmware records that ACR places into WPR and later bootstraps on falcons.

## Important APIs, types, and functions
Exports `nvkm_acr_lsfw_add()`, `nvkm_acr_lsfw_del()`, `nvkm_acr_lsfw_del_all()`, `nvkm_acr_lsfw_load_sig_image_desc()`, `_v1()`, `_v2()`, `nvkm_acr_lsfw_load_bl_inst_data_sig()`, and `nvkm_acr_lsfw_load_bl_sig_net()`.

## Control flow, state, and persistence
`add()` creates or updates one LSF record per falcon id, rejecting redefinition. Loader variants fetch signature/image/descriptor blobs or assemble images from bootloader/inst/data inputs, align bootloader/app sizes, fill resident code/data offsets, and optionally capture secure-bootloader signature metadata. Records persist on `acr->lsfw` until WPR construction cleanup or error.

## Dependencies and integration points
Depends on firmware loader, nvfw LS/HSBL parsers, falcon metadata, ACR private records, and blob lifetime helpers. SEC2/NVDEC/PMU code registers firmware through these APIs.

## Risks and test signals
Alignment and descriptor interpretation feed WPR offsets directly. Signals include LS descriptor debug dumps, duplicate LSF errors, missing firmware cleanup, and WPR comparison/bootstrap success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/lsfw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/priv.h

## Purpose
Defines private ACR function tables, firmware-interface records, HS firmware records, and LSF runtime records.

## Important APIs, types, and functions
`struct nvkm_acr_func` defines firmware load arrays, WPR parse/layout/alloc/build/patch/check hooks, init/fini hooks, and HS bootstrap masks. `struct nvkm_acr_hsfw` and `struct nvkm_acr_hsf_fwif` describe high-secure firmware. `struct nvkm_acr_lsf` records bootstrappable low-secure falcons. The header declares generation helpers and `nvkm_acr_new_()`.

## Control flow, state, and persistence
No code runs here. The contracts determine how `base.c` builds WPR images, boots load/unload firmware, and validates bootstrap capabilities.

## Dependencies and integration points
Includes public `subdev/acr.h` and references falcon firmware functions, SEC2/GSP/PMU owners, and nvfw ACR structures.

## Risks and test signals
Incorrect function pointers cause generation-specific ACR failure. Build coverage catches signature drift; runtime WPR load/bootstrap validates table wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/tu102.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/tu102.c

## Purpose
Implements Turing TU10x/TU11x ACR support using AHESASC and ASB HS firmware phases, GSPLITE ownership, and GP102-style WPR headers.

## Important APIs, types, and functions
`tu102_acr_init()` boots "AHESASC" then "ASB". `tu102_acr_wpr_build()` emits v1 WPR headers with GSPLITE bootstrap owner and shared sub-WPR terminator. `tu102_acr_load()` loads AHESASC, ASB, and unload firmware. `tu102_acr_new()` disables this path under GSP RM.

## Control flow, state, and persistence
WPR build iterates LSF firmware, writes headers/LSBs/images/bootloader data, and terminates. HS firmware arrays include no-firmware fallback entries for optional paths. Init requires both ACR phases to boot successfully.

## Dependencies and integration points
Depends on GP102 WPR allocation/patch/check, GP108 HS firmware functions, GSP detection, and TU102-TU117 firmware blobs.

## Risks and test signals
GSP RM returns `-ENODEV` intentionally. AHESASC/ASB sequencing is critical. Signals include phase boot logs, WPR comparison, and secure falcon bootstrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/acr/tu102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/Kbuild -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/Kbuild

## Purpose
Builds Nouveau BAR subdevice implementations for NV50 through GM20B-era hardware.

## Important APIs, types, and functions
Compiles `base.o`, `nv50.o`, `g84.o`, `gf100.o`, `gk20a.o`, `gm107.o`, `gm20b.o`, and `tu102.o`.

## Control flow, state, and persistence
No runtime logic. It selects the BAR management implementations available to chipset constructors.

## Dependencies and integration points
Included by `nvkm/subdev/Kbuild`. BAR objects depend on memory, VMM, FB, MMU, timer, and device resource-size hooks.

## Risks and test signals
Missing BAR objects break BAR1/BAR2 mapping setup. Build output and BAR subdev init logs validate inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/base.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/base.c

## Purpose
Implements common BAR subdevice lifecycle and public helpers for BAR1/BAR2 VMM access, reset, init/fini, and flush.

## Important APIs, types, and functions
Exports `nvkm_bar_flush()`, `nvkm_bar_bar1_vmm()`, `nvkm_bar_bar1_reset()`, `nvkm_bar_bar2_vmm()`, `nvkm_bar_bar2_init()`, `nvkm_bar_bar2_fini()`, `nvkm_bar_bar2_reset()`, and `nvkm_bar_ctor()`. Subdev callbacks call generation `oneinit`, `init`, `fini`, and `dtor`.

## Control flow, state, and persistence
Init programs BAR1 then optional generation init. BAR2 is initialized lazily only after oneinit and tracked by `bar->bar2`; fini disables BAR1 and, outside suspend, BAR2. Public VMM helpers deny BAR2 before initialization so instmem can fall back to BAR0.

## Dependencies and integration points
Depends on generation `nvkm_bar_func`, subdev lifecycle, and device-level `device->bar`. Used by memory managers, instmem, and SW semaphore paths.

## Risks and test signals
BAR2 lifetime is shared with instmem, so suspend/fini ordering matters. Signals include successful BAR1/BAR2 VMM retrieval, flush completion, and absence of mapping faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/g84.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/g84.c

## Purpose
Specializes NV50 BAR support for G84 by changing the BAR flush register.

## Important APIs, types, and functions
`g84_bar_flush()` writes `0x070000`, waits for the busy bit to clear, and serializes with `bar->lock`. `g84_bar_new()` constructs an NV50-style BAR with PGD address `0x200` and the G84 function table.

## Control flow, state, and persistence
BAR1/BAR2 setup, VMMs, and teardown are inherited from NV50. Flush state is transient hardware state protected by a spinlock.

## Dependencies and integration points
Depends on `nv50_bar_*` helpers and timer polling. Used by G84-family chipset BAR constructors.

## Risks and test signals
Flush timeouts are not returned but can stall for up to 2 seconds. Signals include correct BAR flush behavior for semaphore writes and VMM updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/g84.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gf100.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gf100.c

## Purpose
Implements Fermi GF100-style BAR1/BAR2 VMM construction and register programming.

## Important APIs, types, and functions
Defines `gf100_bar_new_()`, `gf100_bar_new()`, `gf100_bar_oneinit()`, `gf100_bar_dtor()`, BAR1/BAR2 init/fini/VMM helpers, and `gf100_bar_bar1_wait()`. `gf100_bar_oneinit_bar()` allocates an instance block, creates a VMM sized from device BAR resources, boots BAR2 page tables, and joins the VMM to the instance memory.

## Control flow, state, and persistence
Oneinit sets up BAR2 first when supported, initializes it immediately, then sets up BAR1. BAR2 size can be halved by the `NvBar2Halve` option. Init writes BAR instance addresses to `0x001704/0x001714`; fini clears enable bits; dtor parts VMMs and releases memory.

## Dependencies and integration points
Depends on device resource sizes, memory allocation, VMM join/boot, option parsing, and G84 flush. Used by later BAR variants.

## Risks and test signals
Resource size zero returns `-ENOMEM`; BAR2 halve changes address programming. Signals include BAR VMM creation, BAR2 boot success, and mapping/flush correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gf100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gf100.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gf100.h

## Purpose
Declares GF100 BAR private structures and helper prototypes shared by GF100-derived BAR implementations.

## Important APIs, types, and functions
`struct gf100_barN` stores an instance memory object and VMM. `struct gf100_bar` embeds `nvkm_bar`, the `bar2_halve` option, and two BAR slots. The header declares constructor, destructor, oneinit, BAR1/BAR2 init/VMM helpers, and BAR1 wait.

## Control flow, state, and persistence
No code runs here. The structures define persistent BAR1/BAR2 mapping state for GF100-style devices.

## Dependencies and integration points
Includes BAR private header and is used by GF100, GK20A, GM107, GM20B, and TU102-style BAR files.

## Risks and test signals
Structure layout changes affect all derived implementations. Build coverage and BAR VMM init validate compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gf100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gk20a.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gk20a.c

## Purpose
Implements GK20A BAR support as a GF100-derived BAR1-only, uncached-iomap variant.

## Important APIs, types, and functions
`gk20a_bar_new()` calls `gf100_bar_new_()` with a function table that omits BAR2 hooks and sets `(*pbar)->iomap_uncached = true` on success.

## Control flow, state, and persistence
Oneinit creates only BAR1 state through shared GF100 helpers. The uncached iomap flag persists on the BAR object for mapping behavior.

## Dependencies and integration points
Depends on GF100 BAR helpers and G84 flush. Used on Tegra GK20A-class devices.

## Risks and test signals
BAR2 is intentionally absent. Signals include successful BAR1 VMM creation and correct uncached CPU mapping behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gk20a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gm107.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gm107.c

## Purpose
Specializes GF100 BAR support for GM107 wait conditions.

## Important APIs, types, and functions
`gm107_bar_bar1_wait()` waits for bits `0x3` in register `0x001710` to clear. `gm107_bar_bar2_wait()` waits for bits `0xc`. `gm107_bar_new()` constructs a GF100-derived BAR with these waits and G84 flush.

## Control flow, state, and persistence
All VMM allocation and BAR register programming are inherited from GF100. Wait helpers poll hardware after BAR1/BAR2 init/reset operations.

## Dependencies and integration points
Depends on GF100 BAR helpers and timer polling. Used by Maxwell GM107-class devices.

## Risks and test signals
Polling does not return timeout status to callers. Signals include stable BAR mappings after reset and absence of stale BAR busy bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gm107.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gm20b.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gm20b.c

## Purpose
Implements GM20B BAR support as a GM107/GF100-derived BAR1-only, uncached-iomap variant.

## Important APIs, types, and functions
`gm20b_bar_new()` calls `gf100_bar_new_()` with a function table containing BAR1 init/wait/VMM and G84 flush, then sets `iomap_uncached`.

## Control flow, state, and persistence
BAR1 VMM setup and teardown are inherited from GF100. No BAR2 hooks are provided. The uncached mapping flag persists for CPU BAR access semantics.

## Dependencies and integration points
Depends on `gm107_bar_bar1_wait()`, GF100 helpers, and G84 flush. Used on Tegra GM20B devices.

## Risks and test signals
No BAR2 means callers must tolerate `nvkm_bar_bar2_vmm()` returning NULL. Signals include successful BAR1 mapping and correct uncached iomap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/gm20b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/nv50.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/nv50.c

## Purpose
Implements NV50 BAR1/BAR2 virtual memory setup, GPU object page-directory state, register programming, and flush behavior.

## Important APIs, types, and functions
Defines `nv50_bar_new_()`, `nv50_bar_new()`, `nv50_bar_oneinit()`, `nv50_bar_init()`, `nv50_bar_dtor()`, `nv50_bar_flush()`, and BAR1/BAR2 init/fini/wait/VMM helpers.

## Control flow, state, and persistence
Oneinit allocates a backing GPU object, pad, PGD, BAR2 VMM starting at `0x0100000000`, boots BAR2, joins memory, creates BAR2 descriptor object, initializes BAR2, then creates BAR1 VMM and descriptor object. Init clears eight BAR-related registers. BAR init writes descriptor offsets into `0x001708/0x00170c`; BAR2 also programs memory base at `0x001704`. Dtor unwinds VMMs and GPU objects.

## Dependencies and integration points
Depends on GPU objects, VMM, FB/MMU resource sizing, timers, and BAR base lifecycle. Used directly by NV50 and by G84-derived BAR.

## Risks and test signals
Descriptor object fields encode address limits and must match hardware expectations. Signals include BAR VMM join/boot success, flush register completion, and working BAR1/BAR2 memory access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/nv50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/nv50.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/nv50.h

## Purpose
Declares NV50 BAR private structures and helper prototypes for NV50/G84 BAR implementations.

## Important APIs, types, and functions
`struct nv50_bar` embeds `nvkm_bar` and stores PGD address, backing GPU objects, BAR1/BAR2 VMMs, and BAR descriptor objects. The header declares constructors, destructor, oneinit, init, and BAR1/BAR2 init/wait/VMM helpers.

## Control flow, state, and persistence
No runtime code exists. The structure defines all persistent NV50 BAR mapping state.

## Dependencies and integration points
Includes BAR private header and is used by `nv50.c` and `g84.c`.

## Risks and test signals
State layout must match destructor assumptions. Build coverage and BAR oneinit/fini testing validate usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/nv50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/priv.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/priv.h

## Purpose
Defines BAR private function-table contracts and shared helper prototypes.

## Important APIs, types, and functions
`struct nvkm_bar_func` provides destructor, oneinit, optional init, BAR1/BAR2 init/fini/wait/VMM hooks, and flush. The header declares `nvkm_bar_ctor()`, R535 constructor, NV50/GF100 fini helpers, G84 flush, and GM107 wait helpers.

## Control flow, state, and persistence
No code runs here. The function table drives BAR base lifecycle and public BAR helper behavior.

## Dependencies and integration points
Includes public `subdev/bar.h`. Used by all BAR generation files and BAR base.

## Risks and test signals
Missing hooks alter public behavior, especially BAR2 initialization. Build coverage plus BAR1/BAR2 reset/init tests validate table completeness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/priv.h -->
