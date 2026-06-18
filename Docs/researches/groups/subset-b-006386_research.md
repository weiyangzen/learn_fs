# subset-b-006386 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpifunc.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpifunc.c

## Purpose
This file is the public AudioScience HPI convenience API used by kernel and ALSA-facing code. It turns typed helper calls for adapters, streams, mixers, and controls into initialized `struct hpi_message` requests and dispatches them through `hpi_send_recv()`.

## Important APIs, Types, And Functions
Key local types are `struct hpi_handle` and `union handle_word`, which pack adapter index, object type, object index, and flags into 32-bit HPI handles. Important helpers include `hpi_indexes_to_handle()`, `hpi_handle_indexes()`, `hpi_format_create()`, `hpi_format_to_msg()`, stream open/close/read/write/start/stop calls, mixer control lookup calls, and many control-specific wrappers for AES/EBU, CobraNet, compander, meter, sample clock, tuner, PAD, volume, and VOX controls.

## Control Flow
Most functions allocate stack message/response objects, call `hpi_init_message_response()` with an object and function code, fill adapter/object indexes and union payload fields, call `hpi_send_recv()`, then copy response fields back to caller pointers. Stream and mixer open calls synthesize handles on success. Close paths free host buffers and reset stream groups before closing. Control helpers are factored through `hpi_control_param_set()`, `hpi_control_param_get()`, `hpi_control_query()`, log-value helpers, and string chunk reads.

## State, Persistence, And Dependencies
The file owns no persistent hardware state. State lives in firmware/hardware and the lower message layer. It depends on `hpi_internal.h` layouts, `hpimsginit.h`, `hpidebug.h`, HPI constants, and the external `hpi_send_recv()` implementation in the ioctl/message layer.

## Integration Points
This is the typed facade used by ALSA driver logic and other kernel users, including `radio-asihpi`. It integrates with HPI message routing in `hpimsgx.c`, userspace/kernel dispatch in `hpioctl.c`, and firmware-specific handlers reached through `HPI_MESSAGE_LOWER_LAYER`.

## Risks
The handle bitfield layout is compiler and endian sensitive but is used as an ABI-like token inside the driver. Several getters write to output pointers without checking for NULL, while others are defensive. Ancillary frame count multiplication can overflow before the buffer-size check. `hpi_instream_group_get_map()` initializes `HPI_ISTREAM_HOSTBUFFER_FREE`, which is suspicious for a get-map helper. Packed V1 CobraNet HMI requests depend on exact message sizes and manual byte swapping.

## Test Signals
Useful signals are successful adapter enumeration/open/close, correct handle round trips, valid and invalid format creation cases, stream open/read/write/start/stop with host buffers, group rejection across adapters, control get/set/query coverage, CobraNet HMI bounds failures, and absence of kernel warnings from NULL or invalid handle paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpifunc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsginit.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsginit.c

## Purpose
This file initializes HPI message and response buffers with the correct size, type, object, function, version, adapter index, and default error values before dispatch.

## Important APIs, Types, And Functions
The exported functions are `hpi_init_response()`, `hpi_init_message_response()`, `hpi_init_responseV1()`, and `hpi_init_message_responseV1()`. Static helpers `hpi_init_message()` and `hpi_init_messageV1()` do the request side. `msg_size[]` and `res_size[]` derive object-specific sizes from `HPI_MESSAGE_SIZE_BY_OBJECT` and `HPI_RESPONSE_SIZE_BY_OBJECT`.

## Control Flow
For normal messages, object indexes in range are masked with `array_index_nospec()` before indexing the size arrays; invalid objects fall back to the full generic structure size. Message buffers are zeroed only to the selected message size, while responses are zeroed across `sizeof(*phr)` and then record the selected response size. Paired initializers create a request and a response whose default error is `HPI_ERROR_PROCESSING_MESSAGE`.

## State, Persistence, And Dependencies
Persistent state is limited to static size tables and `gwSSX2_bypass`, which selects `HPI_TYPE_SSX2BYPASS_MESSAGE` instead of `HPI_TYPE_REQUEST`. The code depends on `hpi_internal.h`, `hpimsginit.h`, and Linux `nospec` helpers.

## Integration Points
Every HPI API wrapper, ioctl request, probe path, and message router uses these initializers to guarantee predictable headers and safe default failure responses.

## Risks
The bypass flag is file-static and has no setter in this file, so behavior is effectively fixed unless changed elsewhere at link time. V1 message initialization silently leaves fields zeroed if the object is out of range. The request zero length follows per-object size, so incorrect size tables could leave stale bytes in larger unions if callers later use the wrong object payload.

## Test Signals
Tests should validate header fields for normal and V1 requests, invalid object fallback behavior, default error propagation when lower layers do not fill a response, and nospec-protected object indexes at bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsginit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsginit.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsginit.h

## Purpose
This header declares the HPI message/response initialization functions shared across the AudioScience HPI driver.

## Important APIs, Types, And Functions
It declares normal-buffer initializers `hpi_init_response()` and `hpi_init_message_response()`, plus V1 header-sized variants `hpi_init_responseV1()` and `hpi_init_message_responseV1()`.

## Control Flow
The header has no executable flow. It documents that response-only initialization is valid for lower layers, while send paths must prepare matching request and response buffers.

## State, Persistence, And Dependencies
No state is declared here. The prototypes require HPI message and response types from previously included HPI internal headers.

## Integration Points
Included by API wrappers, ioctl/probe code, and the message router so every HPI request follows common header and default-error setup.

## Risks
There are no include-time type guards beyond the include guard. Callers must include the HPI type definitions before this header, and must pass buffers large enough for the selected initializer sizes.

## Test Signals
Build coverage is the main signal: all HPI translation units should compile with these prototypes, and runtime tests should verify response defaults set by the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsginit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsgx.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsgx.c

## Purpose
This file implements the extended HPI message dispatcher, adapter entry-point lookup, cached open responses, and per-owner stream open tracking.

## Important APIs, Types, And Functions
The exported entry is `hpi_send_recv_ex()`. Important internals include `hpi_lookup_entry_point_function()`, `hw_entry_point()`, `subsys_message()`, object-specific routers, `adapter_prepare()`, `HPIMSGX__init()`, `HPIMSGX__reset()`, and `HPIMSGX__cleanup()`. Static caches include adapter, mixer, ostream, and istream open responses plus `asi_open_state` arrays guarded by `msgx_lock`.

## Control Flow
`hpi_send_recv_ex()` validates request type and adapter index, logs messages, then switches by HPI object. Subsystem load initializes locks, entry points, and cached failure responses. Create-adapter finds a handler from the PCI ID table, calls it, stores the handler by adapter index, and pre-opens adapter, streams, and mixer to cache open responses. User stream open checks cached errors and ownership, resets the stream in hardware, then records owner. Close validates owner, resets hardware, and clears the open slot. Cleanup closes streams owned by a file or all adapters during subsystem close/unload.

## State, Persistence, And Dependencies
The dispatcher persists adapter handler mappings, cached open responses, adapter stream counts, and per-owner open flags until delete/unload/reset. It depends on `hpipcida.h`, `hpicmn.h`, HPI common subsystem handling, HPI debug, and OS spinlock wrappers from `hpios.h`.

## Integration Points
It is the lower layer behind `hpi_send_recv()` and the ioctl path. Hardware-specific HPI handlers are selected through PCI `driver_data` and reached by `hw_entry_point()`.

## Risks
Most state is global and indexed by adapter and stream bounds, so probe/remove races or bad adapter counts could corrupt behavior. `HPIMSGX__cleanup()` returns early for NULL owners, which is intentional for kernel owner handling but means ownerless cleanup does nothing. Logging disables itself after DSP communication errors, hiding later traces. Cached open responses can become stale if hardware state changes outside the expected lifecycle.

## Test Signals
Probe/create/delete, subsystem load/unload, repeated stream open/close from the same and different file owners, invalid object index handling, and forced DSP errors should show correct cache, lock, cleanup, and logging behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsgx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsgx.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsgx.h

## Purpose
This header exposes the extended HPI message entry point and aliases it as the lower-layer message implementation.

## Important APIs, Types, And Functions
It defines `HPIMSGX_ALLADAPTERS` as `0xFFFF`, declares `hpi_send_recv_ex(struct hpi_message *, struct hpi_response *, void *h_owner)`, and maps `HPI_MESSAGE_LOWER_LAYER` to that function.

## Control Flow
There is no runtime flow in the header. Including files call `hpi_send_recv_ex()` directly or through the macro.

## State, Persistence, And Dependencies
The header stores no state. It depends on `hpi_internal.h` for HPI message and response structures.

## Integration Points
Used by `hpioctl.c`, `hpimsgx.c`, and lower common HPI code to bind the generic HPI message path to the Linux extended router.

## Risks
The macro alias can hide the true dispatch target in call graphs and makes replacement require preprocessor coordination. The owner argument is untyped, so misuse is only detected by conventions in `hpimsgx.c`.

## Test Signals
Builds should verify that generic lower-layer calls resolve to `hpi_send_recv_ex()`, and open/cleanup tests should pass distinct file-owner pointers through this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpimsgx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpioctl.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpioctl.c

## Purpose
This file implements the Linux userspace ioctl boundary for HPI messages plus PCI probe/remove and module init/exit support for AudioScience adapters.

## Important APIs, Types, And Functions
Key APIs are `asihpi_hpi_ioctl()`, `asihpi_hpi_release()`, `hpi_send_recv()`, `asihpi_adapter_probe()`, `asihpi_adapter_remove()`, `asihpi_init()`, and `asihpi_exit()`. The static `adapters[]` array stores per-adapter kernel state, stream bounce buffers, mutexes, IRQ callbacks, and HPI adapter pointers.

## Control Flow
The ioctl handler validates `HPI_IOCTL_LINUX`, allocates kernel message/response buffers, copies user pointers and message data, clamps message and response sizes, blocks userspace create/delete adapter operations, and dispatches subsystem or adapter messages. Stream read/write requests extract embedded user data pointers, resize a per-adapter vmalloc buffer under the adapter mutex, copy data in for playback, send the message, then copy data out for capture. Probe enables PCI, maps BAR memory, creates the HPI adapter, opens it, checks low-latency and IRQ support, registers optional threaded IRQs, and records driver data. Remove disables IRQ generation, deletes the adapter, unmaps memory, frees IRQ and buffers, and clears state.

## State, Persistence, And Dependencies
State persists in `adapters[]`, module parameters `prealloc_stream_buf` and `hpi_debug_level`, PCI drvdata, vmalloc stream buffers, and IRQ callback fields. Dependencies include Linux PCI, uaccess, vmalloc, module firmware declarations, HPI init/router/common code, and `hpios.h` structures.

## Integration Points
This is both the character-device ioctl implementation and the PCI lifecycle bridge into `hpimsgx.c`. `hpi_send_recv()` is exported for in-kernel HPI callers using `HOWNER_KERNEL`.

## Risks
The ioctl path handles user-controlled sizes and embedded pointers, making bounds and copy handling critical. Partial stream-buffer copies are logged but do not necessarily fail the ioctl. Probe error unwinding only unmaps BARs through the current index loop, and adapter deletion is skipped on some early failure paths after create. Shared per-adapter bounce buffers serialize ioctl stream traffic and may be large.

## Test Signals
Signals include invalid command rejection, small response-size rejection, userspace create/delete denial, stream read/write copy fault behavior, PCI probe/remove with and without IRQ support, low-latency IRQ callbacks, firmware load paths, and clean subsystem close on file release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpioctl.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpioctl.h

## Purpose
This header declares the Linux ioctl, PCI lifecycle, module lifecycle, and in-kernel message dispatch functions for the AudioScience HPI driver.

## Important APIs, Types, And Functions
It declares `asihpi_adapter_probe()`, `asihpi_adapter_remove()`, `asihpi_init()`, `asihpi_exit()`, `asihpi_hpi_release()`, `asihpi_hpi_ioctl()`, and `hpi_send_recv()`. It also defines `HOWNER_KERNEL` as `(void *)-1`.

## Control Flow
There is no executable flow. The comments clarify that `hpi_send_recv()` is used by ALSA or other kernel callers when no file descriptor owner exists.

## State, Persistence, And Dependencies
No state is defined here. Callers must have `struct pci_dev`, `struct pci_device_id`, `struct file`, and HPI message/response types available.

## Integration Points
Included by the HPI Linux module glue and any in-kernel user that needs the exported HPI send/receive helper.

## Risks
`HOWNER_KERNEL` is a sentinel pointer and must never collide with a real file owner in owner-tracking code. The header has no include guard in this excerpt, so repeated inclusion depends on compiler tolerance for duplicate prototypes.

## Test Signals
Build coverage should ensure prototypes match implementation and kernel owner paths do not trigger user-owner cleanup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpios.c -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpios.c

## Purpose
This file implements Linux-specific HPI OS services for delays and coherent DMA memory allocation.

## Important APIs, Types, And Functions
It defines `hpios_delay_micro_seconds()`, `hpios_locked_mem_alloc()`, and `hpios_locked_mem_free()`. The DMA routines operate on `struct consistent_dma_area` from `hpios.h`.

## Control Flow
Delay selection uses `schedule_timeout_uninterruptible()` for longer sleeps when not in interrupt context, `udelay()` for up to 2000 microseconds, and `mdelay()` for longer interrupt-context delays. DMA allocation calls `dma_alloc_coherent()`, records virtual address, DMA handle, device, and size on success, and clears size on failure. Free only releases memory when size is nonzero.

## State, Persistence, And Dependencies
No global state is stored. Allocated DMA state persists in the caller-provided `consistent_dma_area`. Dependencies include Linux delay, scheduler, DMA mapping through included HPI internals, and HPI debug logging.

## Integration Points
Hardware-specific HPI code uses these wrappers to sleep/poll safely and allocate bus-master buffers without embedding Linux APIs throughout firmware-facing code.

## Risks
Long interrupt-context delays fall back to busy `mdelay()`, which can hurt latency. Physical addresses are later narrowed to `u32` by the inline getter in the header, so platforms requiring wider DMA addresses need scrutiny. Free returns error on double-free but leaves stale pointers.

## Test Signals
Signals include successful coherent allocation/free, failed allocation reporting size zero, no scheduling while in interrupt context, and DMA address compatibility with supported adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpios.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpios.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpios.h

## Purpose
This header defines the Linux kernel OS abstraction layer used by AudioScience HPI code.

## Important APIs, Types, And Functions
Important definitions include `HPI_OS_LINUX_KERNEL`, `HPI_BUILD_KERNEL_MODE`, `struct consistent_dma_area`, inline DMA address/valid helpers, `struct hpi_ioctl_linux`, `HPI_IOCTL_LINUX`, debug-level printk mappings, `struct hpios_spinlock`, conditional lock helpers, and `struct hpi_adapter`.

## Control Flow
Inline lock flow chooses `spin_lock()` when IRQs are already disabled and `spin_lock_bh()` otherwise, storing the context for matching unlock. DMA getter helpers directly expose saved virtual and DMA addresses.

## State, Persistence, And Dependencies
State lives in caller-owned structures: DMA area metadata, spinlock context, and per-adapter PCI/ALSA/ioctl data. The header depends on Linux IO, ioctl, device, firmware, interrupt, PCI, mutex, and spinlock headers.

## Integration Points
It is included by HPI core, ioctl, and hardware-specific code to unify kernel APIs, locking, debug flags, and adapter state. `struct hpi_adapter` is the PCI drvdata shape used by `hpioctl.c`.

## Risks
`hpios_locked_mem_get_phys_addr()` truncates `dma_addr_t` into `u32`. `hpios_spinlock.lock_context` is shared per lock, so nested or cross-CPU misuse would unlock with the wrong primitive. The ioctl command uses a historically chosen command number that could conflict outside this driver.

## Test Signals
Build and runtime coverage should exercise HPI message paths from atomic and process contexts, coherent DMA address retrieval, ioctl ABI structure layout, and adapter mutex/buffer fields under concurrent user opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpios.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpipcida.h -->
# sources/distributed-fs/ceph-client/sound/pci/asihpi/hpipcida.h

## Purpose
This header is an initializer fragment for the AudioScience HPI PCI device table.

## Important APIs, Types, And Functions
It contributes `struct pci_device_id` entries for TI DSP6205 devices mapped to `HPI_6205` and TI PCI2040 devices mapped to `HPI_6000`, both with AudioScience subvendor matching and wildcard subdevice.

## Control Flow
There is no standalone control flow. `hpimsgx.c` includes the fragment inside a static PCI ID array and later scans it to select the hardware handler from `driver_data`.

## State, Persistence, And Dependencies
The table data is static and read-only after compilation. It depends on PCI vendor/device constants and HPI handler symbols being defined by included HPI internals.

## Integration Points
`hpi_lookup_entry_point_function()` uses these entries during `HPI_SUBSYS_CREATE_ADAPTER` to bind a probed PCI device to the correct HPI implementation.

## Risks
Because this is a raw initializer fragment, syntax and ordering depend on the includer. The comment requires grouping by HPI entry point; violating that could make maintenance harder. Missing device IDs mean probe can map PCI memory but fail adapter creation.

## Test Signals
PCI probe tests should verify supported AudioScience cards match the expected handler, unsupported cards fail cleanly, and wildcard subdevice matching does not bind unintended hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/asihpi/hpipcida.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/atiixp.c -->
# sources/distributed-fs/ceph-client/sound/pci/atiixp.c

## Purpose
This file is the ALSA PCI driver for ATI IXP AC97 audio controllers, covering analog playback/capture, optional S/PDIF, AC97 codec control, DMA rings, interrupts, power management, and proc register dumps.

## Important APIs, Types, And Functions
Core state is `struct atiixp`, with per-stream `struct atiixp_dma`, descriptor `struct atiixp_dma_desc`, and per-DMA `struct atiixp_dma_ops`. Important functions include `snd_atiixp_init()`, `__snd_atiixp_probe()`, `snd_atiixp_aclink_reset()`, codec read/write helpers, `atiixp_build_dma_packets()`, PCM open/close/hw_params/trigger/pointer callbacks, `snd_atiixp_interrupt()`, mixer/PCM creation, and suspend/resume handlers.

## Control Flow
Probe creates an ALSA card, maps MMIO BAR0, requests IRQ, resets AC-link, detects codecs through not-ready interrupts, builds AC97 mixers, creates analog and digital PCM devices, starts the chip, and registers the card. PCM hw_params allocates a coherent descriptor ring and links period descriptors in a loop. Trigger callbacks enable or disable DMA transfer bits under `reg_lock`, flush FIFOs on stop, and maintain running/suspended state. IRQs report period elapsed or xrun per DMA and collect codec-detection bits. Resume resets AC-link, restarts the chip, resumes codecs, and restores descriptors for suspended streams.

## State, Persistence, And Dependencies
State persists in `struct atiixp`: MMIO base, IRQ, AC97 bus/codecs, PCM devices, descriptor buffers, DMA flags, codec detection bits, max channel count, S/PDIF mode, and mutex/spinlock state. Dependencies include ALSA core/PCM/AC97/info APIs, Linux PCI/MMIO/IRQ/PM, and module parameters for index, id, AC97 clock, quirks, codec override, and S/PDIF transport.

## Integration Points
The driver registers as a PCI module for SB200/SB300/SB400/SB600 AC97 IDs and exposes ALSA PCM, mixer, chmap, and proc interfaces.

## Risks
Descriptor and buffer DMA addresses are cast to `u32`, requiring effective 32-bit DMA addressing. Codec detection relies on interrupts and timing. SPDIF over AC-link shares playback DMA and is serialized with `open_mutex`. Partial or invalid DMA pointer reads return zero, which can cause audible artifacts. Some known codec rates are forced to 48 kHz due hardware limitations.

## Test Signals
Signals include successful probe on each PCI ID, AC97 codec detection with and without quirks, analog 2/4/6/8 channel playback, capture, S/PDIF AC-link and direct modes, xrun recovery, suspend/resume with active streams, proc register output, and clean card removal through devm resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/atiixp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/atiixp_modem.c -->
# sources/distributed-fs/ceph-client/sound/pci/atiixp_modem.c

## Purpose
This file is the ALSA PCI driver for ATI IXP MC97 modem controllers, exposing modem-class playback and capture over AC97 modem codecs.

## Important APIs, Types, And Functions
It mirrors the audio driver with `struct atiixp_modem`, `struct atiixp_dma`, `struct atiixp_dma_desc`, and `struct atiixp_dma_ops`. Key functions include AC97 codec access, AC-link reset/down, codec detection, chip start/stop, descriptor ring build/clear, PCM callbacks, IRQ handler, mixer creation, PM handlers, proc dump setup, and PCI probe.

## Control Flow
Probe creates a card, enables PCI/MMIO/IRQ, resets the AC-link, detects modem codecs, creates an AC97 bus with `AC97_SCAP_SKIP_AUDIO`, registers one modem-class PCM device, starts interrupts, and registers the card. PCM open applies modem rate constraints of 8000, 9600, 12000, and 16000 Hz, enables DMA, and records the stream. hw_params builds the descriptor ring and programs modem codec line rate and level. Trigger toggles modem send/receive bits and flushes FIFOs on stop. IRQ handles playback/capture period and xrun events plus codec-detection interrupts.

## State, Persistence, And Dependencies
Persistent state includes MMIO/IRQ data, AC97 modem codecs, descriptor buffers, PCM devices, codec-not-ready bits, and open serialization. Dependencies are ALSA PCM/AC97/core/info APIs, Linux PCI/MMIO/IRQ/PM, and module parameters for index, id, and AC97 clock.

## Integration Points
The PCI table binds SB200 and SB400 modem controller IDs. ALSA sees a modem PCM device named `ATI IXP MC97`, and `/proc/asound` can expose the `atiixp-modem` register dump.

## Risks
Much code is duplicated from `atiixp.c`, so fixes can diverge. DMA addresses are narrowed to `u32`. GPIO writes special-case `AC97_GPIO_STATUS`, so normal codec write assumptions do not always apply. Resume does not rebuild active DMA descriptors like the audio driver does. Codec detection depends on interrupt timing.

## Test Signals
Test signals include modem PCI probe, AC97 modem codec creation, constrained-rate playback and capture, GPIO status writes, xrun and period IRQs, suspend/resume, proc register dump, and clean behavior when no modem codec is detected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/atiixp_modem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/Makefile

## Purpose
This Makefile builds the three Aureal Vortex ALSA PCI modules for AU8810, AU8820, and AU8830 variants.

## Important APIs, Types, And Functions
It defines `snd-au8810-y`, `snd-au8820-y`, and `snd-au8830-y` object lists and attaches them to `CONFIG_SND_AU8810`, `CONFIG_SND_AU8820`, and `CONFIG_SND_AU8830`.

## Control Flow
There is no runtime flow. Kbuild compiles each chip wrapper object, and each wrapper includes the shared implementation `.c` files after selecting chip-specific headers and macros.

## State, Persistence, And Dependencies
Build state depends on kernel configuration symbols and the wrapper source files. No runtime state is declared.

## Integration Points
This file connects the `sound/pci/au88x0` sources to the ALSA PCI driver build and determines which modules appear in a kernel configuration.

## Risks
Because the shared implementation files are included by wrapper `.c` files, adding shared objects directly here would cause duplicate definitions. Missing a config mapping would silently exclude a chip driver.

## Test Signals
Kbuild should produce the expected `snd-au8810`, `snd-au8820`, and `snd-au8830` modules when their config options are enabled and avoid duplicate symbol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8810.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au8810.c

## Purpose
This file is the AU8810 Aureal Advantage module wrapper that selects AU8810 constants, declares its PCI ID table, and includes the shared Vortex implementation sources.

## Important APIs, Types, And Functions
It includes `au8810.h` and `au88x0.h`, defines `snd_vortex_ids[]` for `PCI_DEVICE_ID_AUREAL_ADVANTAGE`, and includes shared core, PCM, mixer, MPU401, gameport, EQ, A3D, xtalk, and common PCI driver code.

## Control Flow
At compile time, `CHIP_AU8810` from the header disables wavetable sections and enables A3D/EQ paths in shared code. At runtime, control enters the shared `module_pci_driver()` implementation from `au88x0.c`.

## State, Persistence, And Dependencies
This file owns only the static PCI ID table. Runtime state is the shared `vortex_t` structure compiled with AU8810 resource counts and register offsets.

## Integration Points
It binds the generic Vortex ALSA driver to AU8810 hardware and produces the `snd-au8810` object declared by the Makefile.

## Risks
The include-the-world model means compile order and chip macros are critical. Any shared file assuming wavetable resources must be guarded because AU8810 sets `NR_WT` to zero.

## Test Signals
Build should include A3D/EQ/xtalk and exclude wavetable code, the module should match Aureal Advantage PCI devices, and probe should create the expected ALSA card name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8810.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8810.h -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au8810.h

## Purpose
This header defines AU8810-specific identity, resource counts, register offsets, routing helpers, and bit masks for the shared Aureal Vortex driver.

## Important APIs, Types, And Functions
It defines `CHIP_AU8810`, `CARD_NAME`, `CARD_NAME_SHORT`, resource counts such as `NR_ADB`, `NR_SRC`, `NR_A3D`, and `NR_WT`, ADB/WTDMA registers, ADB routing macros, mixer/SRC/FIFO/codec/S/PDIF/timer/IRQ/DMA/MIDI/gameport registers, and control bit masks.

## Control Flow
There is no executable flow. The preprocessor uses these constants to compile shared code for the AU8810 register map and feature set.

## State, Persistence, And Dependencies
No runtime state is declared. The values become compile-time constants used by `vortex_t` resource arrays and MMIO helpers.

## Integration Points
Included only by `au8810.c` before `au88x0.h` and the shared implementation files, thereby shaping the resulting `snd-au8810` module.

## Risks
Many register comments are reverse-engineered or marked FIXME, so hardware behavior may differ by revision. WTDMA constants exist even though `NR_WT` is zero, requiring shared code guards. Incorrect route offsets can break audio paths without compile-time detection.

## Test Signals
Signals include successful playback/capture, A3D and EQ controls, MIDI/gameport behavior, IRQ handling, FIFO state transitions, and absence of wavetable PCM exposure on AU8810.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8810.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8820.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au8820.c

## Purpose
This file is the AU8820 Aureal Vortex module wrapper that selects AU8820 constants, declares the PCI ID table, and includes the shared Vortex driver sources.

## Important APIs, Types, And Functions
It defines `snd_vortex_ids[]` for `PCI_DEVICE_ID_AUREAL_VORTEX_1` and includes synth, core, PCM, MPU401, gameport, mixer, and common PCI driver code.

## Control Flow
The wrapper has compile-time control flow through `CHIP_AU8820`: shared code excludes A3D/EQ/xtalk paths and includes wavetable support. Runtime probe and ALSA setup are handled by shared `au88x0.c`.

## State, Persistence, And Dependencies
Only the PCI ID table is local. All runtime state is `vortex_t`, compiled with AU8820 resource counts and register offsets from `au8820.h`.

## Integration Points
It builds the `snd-au8820` module and binds the shared Vortex implementation to Aureal Vortex 1 PCI devices.

## Risks
Shared code must correctly honor AU8820 feature exclusions. Since the wrapper includes shared `.c` files directly, accidental include reordering can change compiled behavior.

## Test Signals
Build should include wavetable/synth code and exclude A3D/EQ/xtalk, PCI matching should detect Vortex 1 devices, and ALSA should expose the expected PCM/MIDI/gameport set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8820.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8820.h -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au8820.h

## Purpose
This header defines AU8820-specific card identity, resource counts, MMIO register map, ADB route translations, and hardware bit masks.

## Important APIs, Types, And Functions
It defines `CHIP_AU8820`, card names, `NR_ADB`, `NR_WT`, `NR_SRC`, zero `NR_A3D`, ADB/WTDMA registers, ADB/SRC/mixer/FIFO/codec/S/PDIF/IRQ/DMA/MIDI/gameport offsets, and route helper macros such as `ADB_DMA()`, `ADB_SRCOUT()`, and `ADB_WTOUT()`.

## Control Flow
The header contributes no runtime flow. Its macros select paths in shared source files and provide constants for register reads/writes.

## State, Persistence, And Dependencies
No state is stored. Values are compiled into the AU8820 object and determine array sizes in `vortex_t`.

## Integration Points
Included by `au8820.c` before the shared driver code. The shared core, PCM, mixer, and synth files use these constants to program AU8820 hardware.

## Risks
Some offsets are annotated as FIXME or derived from legacy Windows driver addresses. AU8820 lacks A3D resources, so unguarded shared A3D access would be invalid. Route masks differ from AU8810/AU8830 and can cause subtle channel routing failures.

## Test Signals
Signals include wavetable playback, analog playback/capture, mixer routes, SRC conversion, FIFO and DMA operation, codec access, MIDI/gameport operation, and no A3D/EQ controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8820.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8830.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au8830.c

## Purpose
This file is the AU8830 Aureal Vortex 2 module wrapper that selects AU8830 constants, declares the PCI ID table, and includes all shared Vortex implementation sources.

## Important APIs, Types, And Functions
It defines `snd_vortex_ids[]` for `PCI_DEVICE_ID_AUREAL_VORTEX_2` and includes synth, core, PCM, mixer, MPU401, gameport, EQ, A3D, xtalk, and common PCI driver code.

## Control Flow
Compile-time macros from `au8830.h` enable both wavetable and A3D/EQ/xtalk paths. Runtime flow is provided by the shared PCI probe, ALSA component setup, interrupt, and cleanup functions.

## State, Persistence, And Dependencies
The local static PCI table is the only local state. Runtime state uses shared `vortex_t` arrays sized for AU8830's larger ADB and wavetable resources.

## Integration Points
It builds the `snd-au8830` module and binds the shared Vortex driver to Aureal Vortex 2 PCI devices.

## Risks
AU8830 has revision checks in shared probe code, so unrecognized revisions fail intentionally. Including every feature path increases risk of resource conflicts in routing and mixer setup.

## Test Signals
Build should include synth, A3D, EQ, xtalk, PCM, MIDI, and gameport code. Probe should match Vortex 2 devices, reject unknown revisions as coded, and expose the full expected ALSA feature set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8830.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8830.h -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au8830.h

## Purpose
This header defines the AU8830/Vortex 2 identity, resource counts, register map, route helpers, and feature bit masks for the shared Vortex driver.

## Important APIs, Types, And Functions
It defines `CHIP_AU8830`, card names, expanded `NR_ADB` and `NR_WT`, ADB and WTDMA registers, DMA engine control, ADB route offsets for codec, S/PDIF, AC98, EQ, A3D, wavetable, xtalk, and EFX, mixer/SRC/FIFO/GIRT/codec/IRQ/MIDI/gameport constants, and helper macros like `ADB_WTOUT()`.

## Control Flow
No code executes in the header. Preprocessor symbols enable the richest shared-code configuration and constants drive MMIO access.

## State, Persistence, And Dependencies
The header declares no variables. It sets compile-time array sizes and register offsets used in `vortex_t` and shared implementation routines.

## Integration Points
Included by `au8830.c` before `au88x0.h` and all shared source includes. The shared modules use these constants for Vortex 2 routing, DMA, codec, A3D, EQ, and wavetable support.

## Risks
The register map is heavily hardware-specific and partly reverse-engineered. FIFO size and route offsets differ from AU8810 despite similar base addresses. Expanded resources increase the chance of off-by-one route allocation bugs. Unknown `CTRL_SPDIF` value is explicitly marked uncertain.

## Test Signals
Signals include full-duplex PCM, S/PDIF, wavetable playback, A3D, EQ, crosstalk, MIDI, gameport, IRQ status, FIFO/GIRT behavior, and revision-specific probe behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au8830.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0.c

## Purpose
This shared file implements module parameters, PCI probe, card construction, resource mapping, IRQ registration, ALSA component setup, workarounds, and driver registration for all Aureal Vortex variants.

## Important APIs, Types, And Functions
Important functions include `vortex_fix_latency()`, `vortex_fix_agp_bridge()`, `snd_vortex_workaround()`, `snd_vortex_free()`, `snd_vortex_create()`, `__snd_vortex_probe()`, `snd_vortex_probe()`, and the static `pci_driver vortex_driver`. It uses chip-specific macros such as `CARD_NAME`, `CARD_NAME_SHORT`, and `snd_vortex_ids[]`.

## Control Flow
Probe selects an enabled card slot, allocates an ALSA card with `vortex_t` private data, enables PCI and 32-bit coherent DMA, maps MMIO BAR0, initializes the hardware core before requesting IRQ, registers IRQ, applies optional VIA/AMD bridge workarounds, fills card names, creates mixer, PCM devices, MIDI, and optional gameport, validates AU8830 revisions, registers the ALSA card, stores PCI drvdata, connects default routes, and enables interrupts. Cleanup unregisters gameport and shuts down core through `card->private_free`.

## State, Persistence, And Dependencies
Persistent module state includes parameter arrays `index`, `id`, `enable`, and `pcifix`, plus a static probe device counter. Runtime state lives in `vortex_t`: ALSA card, PCM devices, codec, stream resources, MMIO base, IRQ, PCI IDs, and feature-specific structures. Dependencies include ALSA card/PCM/rawmidi/AC97 APIs, Linux PCI/IRQ/DMA, and all shared Vortex subsystems included by chip wrappers.

## Integration Points
Each chip wrapper includes this file after defining chip macros and `snd_vortex_ids[]`, producing separate `snd-au8810`, `snd-au8820`, and `snd-au8830` modules.

## Risks
The static `dev` counter advances across probes and disabled slots. The workaround code touches bridge PCI config registers. Hardware core init must precede IRQ request to avoid spurious interrupts. Feature creation is compile-time conditional and can diverge by chip. AU8830 revision rejection can block otherwise functional unknown hardware.

## Test Signals
Test probe/remove for all three modules, module parameter indexing and disable behavior, VIA/AMD workaround paths, MMIO and IRQ setup, mixer/PCM/MIDI/gameport creation, AU8830 revision handling, and clean shutdown via card free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0.h -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0.h

## Purpose
This shared header defines common Aureal Vortex driver types, MMIO helpers, feature gates, constants, core state, and internal function prototypes.

## Important APIs, Types, And Functions
Important definitions include `hwread()`, `hwwrite()`, MPU401 constants, `SRC_RATIO()`, FIFO and IRQ flags, Vortex resource types, AC97 codec bit masks, `VORTEX_IS_QUAD()`, `IS_BAD_CHIP()`, PCM device indexes, `struct pcm_vol`, `stream_t`, and central `struct snd_vortex`/`vortex_t`. It prototypes internal SRC, DMA, codec, core, routing, mixer, A3D, gameport, EQ, PCM, mixer, and MIDI functions.

## Control Flow
The header itself has no runtime flow. Compile-time guards include or exclude EQ/A3D when not AU8820 and wavetable support when not AU8810, shaping `vortex_t` and available function prototypes.

## State, Persistence, And Dependencies
`vortex_t` is the main persistent per-card state, containing ALSA card/PCM/rawmidi/AC97 pointers, stream arrays, resource maps, feature state, gameport pointer, MMIO/IRQ/lock, PCI device, and revision identifiers. Dependencies include Linux PCI/MMIO and ALSA core, PCM, rawmidi, MPU401, hwdep, AC97, and TLV headers plus feature-specific local headers.

## Integration Points
Included by chip wrappers and all shared Vortex implementation files. It is the contract connecting chip-specific register headers with core, PCM, mixer, MIDI, synth, A3D, EQ, and gameport code.

## Risks
Many functions are declared `static` because shared `.c` files are included into a single wrapper translation unit; changing the build model would require refactoring. Feature-conditional fields can easily drift from guarded code. Resource arrays depend on chip header counts being defined before inclusion.

## Test Signals
Build all three variants to validate conditional structure layout and prototypes. Runtime signals include correct stream allocation, route setup, codec access, IRQ handling, and feature-specific controls matching each chip's declared resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0.h -->
