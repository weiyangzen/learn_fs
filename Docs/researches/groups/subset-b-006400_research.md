# Research: subset-b-006400

Grouped research for ALSA PCI drivers under `sources/distributed-fs/ceph-client/sound/pci/`. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/korg1212/korg1212.c -->
# sources/distributed-fs/ceph-client/sound/pci/korg1212/korg1212.c

## Purpose
This is the complete ALSA PCI driver for the Korg 1212 I/O card. It discovers a PLX-based PCI device, maps card registers, downloads `korg/k1212.dsp` firmware, exposes one duplex PCM device, mixer controls for monitor routing/volume/phase, ADC attenuation, clock source selection, and a proc status file.

## Important APIs, Types, and Functions
The central state is `struct snd_korg1212`, which owns the PCI/card handles, register pointers, DMA buffers, PCM substreams, card state machine, clock settings, routing/volume shared tables, open/play/setup counters, and IRQ wait state. Hardware-facing commands are enumerated in `enum korg1212_dbcnst`; lifecycle states live in `enum CardState`. `snd_korg1212_Send1212Command()` writes mailboxes and doorbells, then polls mailbox acknowledgement except for boot/download commands. `snd_korg1212_downloadDSPCode()` and `snd_korg1212_OnDSPDownloadComplete()` implement firmware boot, DMA address handoff, shared table initialization, ADC sensitivity, clock setup, and idle monitor activation. PCM operations are implemented by `snd_korg1212_playback_ops` and `snd_korg1212_capture_ops`; mixer controls are listed in `snd_korg1212_controls`.

## Control Flow
`snd_korg1212_probe()` allocates an ALSA card and calls `snd_korg1212_create()`. Creation enables PCI, requests regions and IRQ, maps BAR0, allocates shared/playback/capture/DSP DMA buffers, loads firmware, reboots the card, enables interrupts, waits for DSP download completion, creates PCM/control/proc interfaces, and registers the card. Open turns off idle monitor and moves the card to `OPEN`; prepare sends `SetupPlay`; trigger start sends `TriggerPlay`; stop writes a shared `cardCommand` stop sentinel and waits for `CARDSTOPPED`. The IRQ handler acknowledges card doorbells, wakes firmware download/stop waiters, handles DMA error state, advances the current buffer, and calls `snd_pcm_period_elapsed()` for active substreams.

## State and Persistence
Persistent in-memory state includes DMA buffers, shared command/volume/route/timecode tables visible to the DSP, current ring-buffer index, clock source/rate, ADC sensitivity, and open/setup/play reference counters. There is no disk persistence. Firmware is loaded from the kernel firmware interface on probe. The driver uses `spinlock_t lock`, `open_mutex`, and a wait queue around shared state and interrupt-driven transitions.

## Dependencies and Integration Points
The file integrates with Linux PCI managed resources, ALSA core, PCM, control, proc, firmware loading, IRQ handling, DMA allocation, and MMIO helpers. It exposes a PCI driver via `module_pci_driver()`, firmware metadata via `MODULE_FIRMWARE`, an ALSA PCM named `korg1212`, and a proc entry named `korg1212`.

## Risks
Command progress depends on tight udelay polling and doorbell IRQs; missed acknowledgements or interrupt loss can wedge open/prepare/stop flows. DMA addresses are narrowed through 32-bit fields and endian word-swap helpers, making DMA mask and endian behavior important. Mixer controls mutate DSP-visible shared tables from control callbacks. Several comparisons in volume and route `put` paths compare against `volumeData` or use `>= k1212MaxVolume` where `<=` appears intended; those should be regression-tested before trusting control updates. The state machine is counter-based for duplex use, so mismatched open/close/trigger pairs risk stale `running`, `playcnt`, or `setcnt` state.

## Test Signals
Probe should fail cleanly without firmware and succeed with `korg/k1212.dsp`; `dmesg` should show no DSP timeout. ALSA should list one playback and one capture PCM with fixed 1024-frame periods and 8 periods. Playback/capture at 44.1 kHz and 48 kHz should advance pointers and period interrupts. Mixer tests should verify monitor route, volume, phase, ADC attenuation, and sync source actually change hardware-visible values. Fault signals include `DMA Error`, `NoAckFromCard`, `CARDSTOPPED` timeout, period pointer stalls, or proc state inconsistent with stream state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/korg1212/korg1212.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/lola/Makefile

## Purpose
This Makefile builds the Digigram Lola ALSA PCI driver as the `snd-lola` module when `CONFIG_SND_LOLA` is enabled.

## Important APIs, Types, and Functions
It declares `snd-lola-y := lola.o lola_pcm.o lola_clock.o lola_mixer.o`, so the base module always includes PCI probe/CORB/RIRB handling, PCM stream handling, clock control, and mixer control. It conditionally appends `lola_proc.o` via `snd-lola-$(CONFIG_SND_DEBUG)` to include proc debugging only in debug builds.

## Control Flow
Kbuild compiles the listed objects into one composite module. `obj-$(CONFIG_SND_LOLA) += snd-lola.o` connects the module to the kernel config option.

## State and Persistence
The Makefile has no runtime state. Its important persistence behavior is build-contract persistence: adding or removing Lola source files requires updating this object list.

## Dependencies and Integration Points
It depends on Kbuild composite-object conventions and the kernel configuration symbol `CONFIG_SND_LOLA`. It also encodes that `lola_proc.c` must not be linked unless debug support is configured.

## Risks
Forgetting to update `snd-lola-y` when adding a required implementation file will cause unresolved symbols or missing runtime features. Accidentally linking debug proc support unconditionally could expose direct codec register access outside debug builds.

## Test Signals
`make M=sound/pci/lola` or a full kernel build with `CONFIG_SND_LOLA=m/y` should produce `snd-lola`. A debug build should include proc entries from `lola_proc.c`; a non-debug build should not reference `lola_proc_debug_new()` beyond the stub macro in `lola.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola.c -->
# sources/distributed-fs/ceph-client/sound/pci/lola/lola.c

## Purpose
This is the core PCI, codec-command, interrupt, and probe implementation for the Digigram Lola PCIe ALSA driver. It initializes BAR0/BAR1, implements an HD-audio-like CORB/RIRB command transport, parses the card widget tree, and wires PCM/mixer/debug helpers into an ALSA card.

## Important APIs, Types, and Functions
Module parameters provide ALSA card index/id/enable plus Lola-specific `granularity` and `sample_rate_min`. `corb_send_verb()`, `lola_codec_write()`, `lola_codec_read()`, and `lola_codec_flush()` are the exported codec verb transport used by clock, PCM, mixer, and proc code. `lola_update_rirb()` consumes responses and unsolicited clock events. `lola_interrupt()` handles stream, controller, FIFO, and microcontroller interrupts. `reset_controller()`, `setup_corb_rirb()`, `lola_irq_enable()`, and `lola_parse_tree()` form the hardware bring-up path.

## Control Flow
`lola_probe()` delegates to `__lola_probe()` through `snd_card_free_on_error()`. Probe creates the card, calls `lola_create()` for PCI enable, BAR mapping, reset, IRQ request, stream count discovery, CORB/RIRB allocation, and IRQ enablement. Then `lola_parse_tree()` validates Digigram vendor/function IDs, discovers capture/playback widgets, pins, clock, and mixer, enables clock events, and restores setup after warm reset. Finally it creates PCM devices, mixer controls, optional debug proc files, and registers the card.

## State and Persistence
`struct lola` stores register locks, CORB/RIRB buffers and pointers, pending command count, last command/debug responses, stream arrays, pin/clock/mixer metadata, sample-rate constraints, granularity, cold-reset status, and polling fallback state. There is no disk persistence. Runtime state is hardware-resident in BAR registers and firmware widget state, with driver shadows used for restoration.

## Dependencies and Integration Points
This file is the hub for Linux PCI managed resources, ALSA card lifecycle, IRQs, DMA ring buffers, the other Lola source files through `lola.h`, and Digigram PCI ID `0x0001`. The CORB/RIRB helpers are the integration contract used by `lola_clock.c`, `lola_mixer.c`, `lola_pcm.c`, and `lola_proc.c`.

## Risks
CORB/RIRB command completion is serialized with `reg_lock` and a command count; lost RIRB interrupts switch to polling, which is useful but can hide IRQ failures. `lola_create()` enables interrupts before full widget parsing, so partial initialization must unwind through managed resources. Stream-count and widget-count values are hardware-provided and must stay bounded by `MAX_*` constants. Warm-reset restoration replays mixer/clock/granularity state and can fail if helpers assume fully initialized widgets.

## Test Signals
Probe should log valid stream counts and vendor/function IDs, then register an ALSA card named Digigram Lola. Codec verb reads should not time out or set `LOLA_RIRB_EX_ERROR`. Interrupt tests should show period elapsed callbacks for input/output streams and no repeated FIFO/microcontroller error bits. Warm reboot or driver reload should preserve functional clock, gain, SRC, and stream setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola.h -->
# sources/distributed-fs/ceph-client/sound/pci/lola/lola.h

## Purpose
This header defines the Digigram Lola driver’s register map, protocol constants, shared state structures, MMIO helper macros, codec verbs, widget parameter helpers, and cross-file function prototypes.

## Important APIs, Types, and Functions
BAR0 constants model HD-audio global, CORB/RIRB, immediate command, and stream descriptor registers. BAR1 constants model Digigram-specific FPGA, stream, interrupt, board, mixer, peak-meter, and DSD registers. Core structs include `lola_bar`, `lola_rb`, `lola_pin`, `lola_pin_array`, `lola_sample_clock`, `lola_clock_widget`, `lola_mixer_array`, `lola_mixer_widget`, `lola_stream`, `lola_pcm`, and the top-level `struct lola`. Helper macros such as `lola_readl()`, `lola_writel()`, and `lola_dsd_read/write()` centralize MMIO addressing. Prototypes expose codec, PCM, clock, mixer, and proc functions.

## Control Flow
The header itself has no runtime flow, but it establishes the initialization order used by `lola.c`: detect stream counts into `pcm[]`, initialize audio widgets into `lola_stream`, pins into `pin[]`, clock metadata into `clock`, mixer register/shadow metadata into `mixer`, then create user-facing ALSA interfaces.

## State and Persistence
The state model is explicit in `struct lola`: BAR mappings, IRQ number, register lock/open mutex, CORB/RIRB queues, last command/debug response, stream arrays, SRC mask, pins, clock selection/frequency/validity, mixer matrix, hardware caps, module parameters, and flags. State persists only for the driver lifetime and may be replayed into hardware after reset.

## Dependencies and Integration Points
The header depends on ALSA PCM constants for `PLAY` and `CAPT`, Linux MMIO accessors through source users, and the Lola-specific codec verb protocol. It is included by every Lola implementation file and is the main internal ABI for the module.

## Risks
Many macros directly compute MMIO offsets; wrong BAR selection or DSD index can write to unrelated hardware registers. Fixed maxima (`MAX_STREAM_COUNT`, `MAX_PINS`, `LOLA_MIXER_DIM`, `MAX_SAMPLE_CLOCK_COUNT`) protect stack/static arrays but require validation against hardware values. `struct lola_mixer_array` overlays an MMIO region and must match hardware layout exactly.

## Test Signals
Compile coverage is important because this header carries prototypes and composite state. Runtime test signals include correct BAR register dumps in debug proc, stream counts bounded by header maxima, clock/mixer/pin parsing matching hardware variants, and absence of out-of-range stream DSD accesses during multi-channel playback/capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola_clock.c -->
# sources/distributed-fs/ceph-client/sound/pci/lola/lola_clock.c

## Purpose
This file implements Lola clock-list discovery, clock selection, sample-rate conversion, granularity configuration, and unsolicited external-clock updates.

## Important APIs, Types, and Functions
`lola_sample_rate_convert()` decodes Lola clock codes into Hz using base frequency, multiplier/divisor, and 1000/1001 adjustments. `lola_set_granularity()` validates and sends `LOLA_VERB_SET_GRANULARITY_STEPS`. `lola_init_clock_widget()` validates the clock widget, reads the clock list in groups of four, filters internal/video clocks below `sample_rate_min`, and builds `idx_lookup`. `lola_enable_clock_events()` enables unsolicited clock responses. `lola_set_clock_index()`, `lola_set_clock()`, and `lola_set_sample_rate()` select valid internal/current clocks. `lola_update_ext_clock_freq()` updates external clock validity/frequency from IRQ-delivered unsolicited responses.

## Control Flow
During probe, `lola_parse_tree()` calls `lola_init_clock_widget()` if hardware advertises a clock widget, then enables events. PCM prepare calls `lola_set_sample_rate()` to lock the stream rate to a valid internal clock. IRQ-side RIRB handling calls `lola_update_ext_clock_freq()` for unsolicited clock status changes.

## State and Persistence
The file maintains `chip->clock.items`, `cur_index`, `cur_freq`, `cur_valid`, `sample_clock[]`, and `idx_lookup[]`; it also writes `chip->granularity`. These are in-memory mirrors of codec clock/granularity hardware state and are replayed by `lola_reset_setups()`.

## Dependencies and Integration Points
It depends on `lola_codec_read/write/flush()`, clock constants and widget structures from `lola.h`, ALSA PCM rate expectations through `lola_pcm.c`, and interrupt-driven unsolicited response delivery from `lola.c`.

## Risks
Clock validity rules reject non-current external clocks unless the current external source reports a valid frequency. Granularity limits are tied to max sample rate, so wrong compatibility checks can allow unstable high-rate streaming. `lola_set_clock_index()` assumes caller-provided `idx` is valid for `idx_lookup`; external callers should validate through `lola_set_clock()` or clock item bounds. A missing clock widget would leave clock fields mostly zero, making later sample-rate selection fail.

## Test Signals
Clock-list proc/debug output should decode expected internal, video, and external clocks. Opening PCM at supported rates should select a matching internal clock; unsupported rates should fail with `-EINVAL`. External clock connect/disconnect should update `cur_valid` and `cur_freq` through unsolicited events. Granularity changes should reject incompatible 96/192 kHz combinations and should survive warm reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola_mixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/lola/lola_mixer.c

## Purpose
This file discovers Lola pin and mixer widgets, initializes firmware-visible mixer matrices, manages analog gains and digital SRC controls, and creates ALSA mixer controls for analog and digital volume/SRC.

## Important APIs, Types, and Functions
`lola_init_pin()` validates pin widget caps and fills analog gain capabilities. `lola_init_pins()` walks input/output pin NIDs. `lola_init_mixer_widget()` validates the vendor mixer widget, maps the BAR1 mixer array, computes source/destination offsets and masks, and allocates a saved mixer shadow. `lola_mixer_set_src_gain()` and `lola_mixer_set_mapping_gain()` update MMIO gain arrays and notify firmware with mixer verbs. `lola_setup_all_analog_gains()` and `set_analog_volume()` manage pin amp verbs. `lola_set_src_config()` toggles input sample-rate converters by stereo pairs. `lola_create_mixer()` adds ALSA controls and calls `init_mixer_values()`.

## Control Flow
Probe parses pins before the mixer widget. Mixer creation adds analog playback/capture volume controls if all pins in that direction are analog, an optional digital SRC capture switch, digital capture/playback source-gain controls, and initializes default routing: SRC on, matrix cleared, physical inputs mapped to capture, playback streams mapped to physical outputs, and digital source gains at 0 dB.

## State and Persistence
Pin state persists in `chip->pin[dir].pins[]` including current gain step. Mixer state exists both in BAR1 MMIO arrays and driver metadata masks/offsets; `array_saved` is reserved for sleep/reset-style preservation but this file primarily replays current pin/SRC values. `input_src_mask` shadows active SRC channels.

## Dependencies and Integration Points
It depends on codec verbs from `lola.c`, BAR1 mixer register definitions from `lola.h`, ALSA control/TLV APIs, and stream/pin counts discovered by `lola_parse_tree()` and `lola_pcm.c`.

## Risks
The mixer matrix is 32x32 and heavily offset-dependent; invalid hardware caps could cause wrong source/destination writes, so mask validation is critical. Destination gain controls are disabled with a FIXME for buggy matrix handling, indicating unresolved risk in exposing full matrix control. `lola_analog_vol_put()` always returns 0 even after successful changes, so userspace may not get change notifications. SRC is stereo-pair based; odd channel expectations can surprise callers.

## Test Signals
Mixer creation should expose analog controls only on all-analog directions, expose SRC only when digital capture pins advertise SRC, and expose digital capture/playback volumes. Default loopback should route physical inputs to capture and playback to outputs. ALSA mixer writes should update BAR1 gain enable/value registers and produce successful codec flushes. Regression tests should verify change notification behavior and no out-of-mask MMIO writes for Lola280/Lola881/Lola16161-style layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola_pcm.c -->
# sources/distributed-fs/ceph-client/sound/pci/lola/lola_pcm.c

## Purpose
This file implements Lola PCM stream discovery, ALSA PCM device creation, buffer descriptor programming, stream reset/prepare/trigger/pointer operations, and period notification handling.

## Important APIs, Types, and Functions
`lola_init_pcm()` and `lola_init_stream()` parse audio widget NIDs into `struct lola_stream`, determine DSD indices, validate widget caps, detect float support, and mark digital capture SRC capability. `lola_create_pcm()` allocates BDL DMA pages, creates a PCM with one substream per hardware stream, installs `lola_pcm_ops`, and preallocates SG buffers. Runtime operations include `lola_pcm_open/close`, `lola_pcm_hw_params/free`, `lola_pcm_prepare`, `lola_pcm_trigger`, `lola_pcm_pointer`, and IRQ helper `lola_pcm_update()`. Low-level helpers program BDL entries, stream formats, channel stream IDs, DSD registers, and synchronized timestamps.

## Control Flow
Open reserves a stream, constrains rate to either the locked card sample rate or min/max module settings, and constrains buffer/period sizes to granularity. Prepare resets prior state, reserves adjacent streams for multichannel use, builds BDL entries, selects sample rate, configures codec stream/channel IDs, writes DSD BDL/LVI/control registers, and waits for FIFO readiness. Trigger starts or stops all linked streams with a common LRC-based timestamp when needed. Interrupt handling in `lola.c` calls `lola_pcm_update()` to deliver `snd_pcm_period_elapsed()`.

## State and Persistence
Each `lola_stream` tracks NID, stream index, DSD index, substream pointer, master stream for multichannel, buffer size, period bytes, BDL fragment count, format verb, and opened/prepared/paused/running flags. `chip->sample_rate` is a card-wide lock released when the last stream closes via `ref_count_rate`.

## Dependencies and Integration Points
This file depends on BAR1 DSD register helpers, codec verbs for stream format/channel assignment, clock selection in `lola_clock.c`, PCM structures in ALSA, and IRQ status routing from `lola_interrupt()`.

## Risks
Multichannel playback/capture consumes adjacent hardware streams; inadequate cleanup can leave slave streams marked opened. BDL setup allows only eight entries and can fail for fragmented SG periods. Sample rate is locked globally while any stream is open, so close/refcount bugs can block later rates. Trigger synchronization depends on LRC/granularity math and linked-stream grouping. FIFO waits time out after 200 ms and should be treated as hardware/firmware failures.

## Test Signals
Open should reject reopening the same hardware stream and constrain channel counts to remaining streams. Prepare should fail cleanly when channels exceed available streams or BDL entries exceed limits. Linked playback/capture streams should start sample-synchronously. Pointer movement should match DSD LPIB and wrap at buffer size. IRQ period notifications should arrive once per completed BDL fragment and stop after trigger stop/hw_free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola_proc.c -->
# sources/distributed-fs/ceph-client/sound/pci/lola/lola_proc.c

## Purpose
This debug-only file creates ALSA proc entries for inspecting Lola codec widgets, issuing direct codec read/write commands, and dumping BAR/DSD registers.

## Important APIs, Types, and Functions
`lola_proc_debug_new()` creates `codec`, `codec_rw`, and `regs` proc entries when `CONFIG_SND_DEBUG` links this file. `lola_proc_codec_read()` prints vendor/function/specific caps and walks the same NID order as probe: capture audio widgets, playback audio widgets, input pins, output pins, optional clock, optional mixer. `lola_proc_codec_rw_write/read()` provides direct four-integer codec command access and returns the last response. `lola_proc_regs_read()` dumps BAR0/BAR1 ranges and DSD status/LPIB/control/BDL registers.

## Control Flow
Probe calls `lola_proc_debug_new()` after PCM and mixer creation. Read callbacks query live codec/register state on demand. The read/write proc path parses user input lines as `id verb data extdata`, calls `lola_codec_read()`, and stores results in `chip->debug_res` and `chip->debug_res_ex`.

## State and Persistence
The file adds only transient debug response fields in `struct lola`; it does not persist data. Proc reads may have hardware side effects if the underlying codec verbs do.

## Dependencies and Integration Points
It depends on ALSA proc helpers, codec verb helpers, widget constants from `lola.h`, and `CONFIG_SND_DEBUG` build gating in the Makefile/header. It is explicitly not present in normal builds.

## Risks
`codec_rw` is powerful direct hardware access and can change or query arbitrary codec verbs, so keeping it debug-only matters. Dump callbacks issue live codec reads without extensive error handling. Register dumps assume fixed DSD count of 32, matching BAR1 layout constants.

## Test Signals
With `CONFIG_SND_DEBUG`, proc entries should appear under the card and show coherent widget caps matching probe. `codec_rw` should return expected response pairs for benign read verbs. `regs` should show changing DSD LPIB/STS during active PCM streams. Non-debug builds should compile without this object and use the no-op `lola_proc_debug_new` macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lola/lola_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/lx6464es/Makefile

## Purpose
This Makefile builds the Digigram LX6464ES ALSA PCI driver as the `snd-lx6464es` composite module.

## Important APIs, Types, and Functions
It declares `snd-lx6464es-y := lx6464es.o lx_core.o`, splitting the module between ALSA-facing PCI/PCM/control code and lower-level DSP/PLX mailbox code. `obj-$(CONFIG_SND_LX6464ES) += snd-lx6464es.o` ties the module to its kernel config symbol.

## Control Flow
Kbuild compiles `lx6464es.c` and `lx_core.c`, then links them into one module when `CONFIG_SND_LX6464ES` is enabled as built-in or module.

## State and Persistence
The Makefile has no runtime state. It preserves the source-to-module composition contract for LX6464ES.

## Dependencies and Integration Points
It depends on Kbuild composite-object syntax and `CONFIG_SND_LX6464ES`. The two object files share internal headers `lx6464es.h`, `lx_core.h`, and `lx_defs.h`.

## Risks
Missing either object breaks linkage: `lx6464es.o` needs DSP/IRQ helpers from `lx_core.o`, and `lx_core.o` needs `struct lx6464es` from the shared header. Adding future source files requires updating this list.

## Test Signals
A kernel build with `CONFIG_SND_LX6464ES=m/y` should produce/link `snd-lx6464es` without unresolved `lx_*` symbols. Disabling the config should omit the module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx6464es.c -->
# sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx6464es.c

## Purpose
This is the ALSA-facing PCI driver for Digigram LX6464ES/ESe variants. It handles PCI probe, PLX/Xilinx/EtherSound DSP initialization, ALSA PCM operations, playback mute control, proc level reporting, and card registration.

## Important APIs, Types, and Functions
The driver matches PLX 9056 devices with Digigram subsystem IDs. `lx_caps` describes a continuous-rate, 2-64 channel, 16/24-bit PCM interface. Hardware lifecycle helpers `lx_hardware_open/start/stop/close()` allocate/release firmware pipes and set stream format/granularity. ALSA callbacks include `lx_pcm_open`, `lx_pcm_prepare`, `lx_pcm_hw_params`, `lx_pcm_hw_free`, `lx_pcm_trigger`, and `lx_pcm_stream_pointer`. Initialization helpers include `lx_init_xilinx_reset/test`, `lx_init_ethersound_config`, `lx_init_get_version_features`, `lx_set_granularity`, and `lx_init_dsp`. `snd_lx6464es_create()` wires PCI resources, IRQ, DSP init, PCM, proc, and mixer control.

## Control Flow
Probe creates an ALSA card and calls `snd_lx6464es_create()`. Creation enables PCI bus mastering, restricts DMA to 32-bit, maps PLX I/O BAR1 and DSP BAR2, requests a threaded shared IRQ, initializes DSP/EtherSound/MAC/version/granularity, creates PCM/proc/control interfaces, then card registration sets IDs based on MAC. PCM open constrains rate to the board clock and period size to MicroBlaze IBL limits. Prepare opens and starts firmware hardware. Trigger prequeues one buffer per period, starts/stops stream state, and IRQ thread later replenishes buffers on EOB events.

## State and Persistence
`struct lx6464es` holds MAC address, mutexes, mapped ports, shared message structure, IRQ source, frequency ratio, playback mute, per-direction hardware-running flags, board sample rate, PCM granularity, PCM device, and one capture/playback stream. Runtime stream state is mostly firmware-owned, with `frame_pos` tracking the current ALSA period. There is no disk persistence.

## Dependencies and Integration Points
This file depends on Linux PCI, DMA mask/resource management, threaded IRQs from `lx_core.c`, ALSA PCM/control/proc APIs, and the LX DSP mailbox functions declared in `lx_core.h`. Hardware initialization integrates PLX registers, Xilinx reset, EtherSound configuration, and MicroBlaze firmware commands.

## Risks
The driver assumes one playback and one capture pipe while exposing up to 64 channels per stream. Buffer period bytes are calculated as `channels * 3`, matching 24-bit packed hardware, so 16-bit runtime formats need careful validation. `lx_control_playback_put()` toggles mute using `!current_value` rather than the requested value, which may ignore malformed userspace values. Trigger start ignores some `lx_buffer_ask/give` errors during prequeue loops. Board sample rate is constrained to the detected EtherSound clock and may be zero if clock detection fails.

## Test Signals
Probe should reset Xilinx, initialize EtherSound, obtain a nonzero MAC, print DSP version, and set default granularity. ALSA open should expose a single locked board rate and period constraints 32-512 frames. Playback/capture trigger should prequeue periods, start stream, receive EOB threaded IRQ callbacks, advance `frame_pos`, and call `snd_pcm_period_elapsed()`. Proc `levels` should return 64 capture and playback peak entries. Mute control should call `lx_level_unmute()` and reflect state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx6464es.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx6464es.h -->
# sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx6464es.h

## Purpose
This header defines top-level LX6464ES driver state and stream status used by the ALSA-facing code and low-level DSP core.

## Important APIs, Types, and Functions
It includes ALSA core/PCM and `lx_core.h`. The command-state enum documents mailbox/read command states, although this file’s current implementation primarily serializes through mutexes. `enum lx_stream_status` models scheduling and running state for capture/playback trigger dispatch. `struct lx_stream` stores the ALSA substream pointer, current period index, stream status, and capture flag. `struct lx6464es` is the driver’s main state object.

## Control Flow
The header has no executable flow. It defines the object passed from probe through ALSA callbacks and low-level DSP functions. `lx6464es.c` allocates it as `card->private_data`; `lx_core.c` dereferences it for register access, mailbox commands, IRQ processing, and buffer replenishment.

## State and Persistence
`struct lx6464es` contains card/PCI/IRQ identity, MAC address, setup/message/IRQ mutexes, PLX and DSP port mappings, reusable `lx_rmh` message buffer, last IRQ source, frequency ratio, playback mute, hardware-running flags, board sample rate, granularity, managed DMA buffers, PCM pointer, and one capture/playback stream. State exists only for the driver lifetime.

## Dependencies and Integration Points
It is the shared internal ABI between `lx6464es.c` and `lx_core.c`. It depends on Linux mutex/atomic-related includes, ALSA PCM types, and DSP command definitions from `lx_core.h`/`lx_defs.h`.

## Risks
Because `struct lx6464es` embeds a single reusable `lx_rmh`, every DSP command path must honor `msg_lock`. The single capture/playback stream model should remain aligned with the PCM creation code. `hardware_running[2]` uses ALSA stream direction values as indices, so assumptions about `SNDRV_PCM_STREAM_*` values matter.

## Test Signals
Build tests should catch field/API drift between `lx6464es.c` and `lx_core.c`. Runtime tests should verify `capture_stream.is_capture` is set, playback remains output, `frame_pos` wraps by ALSA periods, and mutex-protected DSP commands do not overlap under full-duplex stream and proc/control activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx6464es.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_core.c -->
# sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_core.c

## Purpose
This file implements the low-level LX6464ES PLX/DSP register access, MicroBlaze mailbox protocol, pipe/stream/buffer/gain commands, peak metering, and interrupt handling.

## Important APIs, Types, and Functions
`lx_dsp_reg_read/write()` and `lx_plx_reg_read/write()` map symbolic register enums to MMIO/I/O offsets. `lx_message_init()` and `lx_message_send_atomic()` build and synchronously submit `struct lx_rmh` commands using the `dsp_commands[]` table. Public DSP helpers include `lx_dsp_get_version()`, `lx_dsp_get_clock_frequency()`, `lx_dsp_set_granularity()`, `lx_dsp_read_async_events()`, and `lx_dsp_get_mac()`. Pipe/stream/buffer APIs include `lx_pipe_allocate/release/start/pause/stop/state/sample_count`, `lx_stream_set_format/state/sample_position`, `lx_buffer_ask/give/free/cancel`, `lx_level_unmute()`, and `lx_level_peaks()`. IRQ APIs are `lx_interrupt()`, `lx_threaded_irq()`, `lx_irq_enable()`, and `lx_irq_disable()`.

## Control Flow
ALSA-facing code calls pipe allocation and stream format/state helpers during prepare/trigger. Each command locks `msg_lock`, initializes the mailbox header, writes command words to CRM registers, sets the CSM command bit, polls for response, reads status words, clears the response bit, and returns firmware status or Linux errors. The hard IRQ acknowledges PLX doorbells, records async IRQ sources, and wakes the thread. The threaded IRQ reads async events, derives input/output EOB pipe masks, asks firmware for buffer status, gives the next ALSA period DMA address, advances `frame_pos`, and notifies ALSA.

## State and Persistence
State is held in hardware registers, `chip->rmh`, `chip->irqsrc`, `chip->mac_address`, and `lx_stream.frame_pos`. Commands are synchronous and serialized. There is no persistence beyond runtime hardware/driver state.

## Dependencies and Integration Points
This file depends on `lx6464es.h` for device state, `lx_core.h`/`lx_defs.h` for command/register constants, Linux PCI/MMIO/delay helpers, ALSA period notification through `snd_pcm_period_elapsed()`, and buffer addresses supplied by the PCM layer.

## Risks
The mailbox send path busy-polls up to 40 ms and runs under a mutex; long DSP stalls can block PCM/control/proc callers. Firmware status codes are returned directly in some paths, mixing positive DSP errors with negative Linux errors. IRQ buffer replenishment calculates period size as `channels * 3 * period_size`; this must match DMA format programming. The threaded IRQ calls `snd_pcm_period_elapsed()` without checking whether `lx_stream->stream` is non-NULL, so teardown races rely on IRQ synchronization and locks. `lx_dsp_get_mac()` has a TODO for endian handling.

## Test Signals
DSP commands should complete without `ED_DSP_TIMED_OUT` or `ED_DSP_CRASHED`. Pipe state waits should reach `PSTATE_RUN` and `PSTATE_IDLE` within 50 ms. EOB interrupts should produce `CMD_04_GET_EVENT` masks and successful buffer give operations. Peak metering should map 4-channel groups into 64 values. Tests should stress full-duplex start/stop/hw_free while interrupts are active to catch stale stream pointer or frame position issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_core.h -->
# sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_core.h

## Purpose
This header declares the LX6464ES low-level DSP/PLX register interface, mailbox message structure, pipe/stream/buffer/gain/IRQ APIs, stream format constants, and pointer helper used by the ALSA-facing driver.

## Important APIs, Types, and Functions
Register enums define DSP ports such as CSM, CRM1-CRM12, interrupt/status, EtherSound config/MAC registers, and PLX ports such as mailboxes, doorbell, IRQ control, and chip select control. `struct lx_rmh` stores command/status lengths, status type, command index, and up to 12 command/status words. Function declarations expose all low-level operations implemented in `lx_core.c`. Inline wrappers `lx_stream_start/pause/stop()` call `lx_stream_set_state()`. `unpack_pointer()` splits DMA addresses into low/high 32-bit words.

## Control Flow
The header defines the call surface used by `lx6464es.c`: initialization uses version/clock/MAC/granularity/IRQ helpers; PCM prepare uses pipe and stream format helpers; trigger/IRQ uses stream state and buffer helpers; proc/control uses level helpers.

## State and Persistence
The only state type defined here is `struct lx_rmh`, embedded in `struct lx6464es`. It is reused for command submission and must be protected by `msg_lock`. Constants here encode firmware protocol state values but do not persist data.

## Dependencies and Integration Points
It includes `lx_defs.h` for opcodes, states, flags, and error constants. It forward-declares `struct lx6464es` to avoid circular dependencies and includes Linux interrupt types for IRQ prototypes.

## Risks
The register enum ordering must stay synchronized with offset arrays in `lx_core.c`. Duplicate `START_STATE`/`PAUSE_STATE` defines exist in the header and should be kept consistent if edited. DMA pointer splitting handles 32-bit and 64-bit hosts, but the main driver restricts DMA mask to 32-bit, so future 64-bit DMA changes require coordinated updates.

## Test Signals
Compile tests should detect prototype drift. Runtime tests should exercise every declared path indirectly: DSP version/clock/MAC during probe, pipe allocate/release during prepare/free, stream start/stop during trigger, buffer give on IRQ, level peak reads through proc, and IRQ enable/disable during module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_defs.h -->
# sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_defs.h

## Purpose
This header contains adapted LX6464ES/EtherSound firmware protocol definitions: clock-frequency thresholds, EtherSound configuration bitfields, interrupt masks, command opcodes, pipe/stream/buffer flags, stream format fields, and DSP/board error codes.

## Important APIs, Types, and Functions
Frequency macros classify 44.1/48 kHz EtherSound clock counters. `IOCR_*`, `FREQ_RATIO_*`, and `CONFES_*` define EtherSound configuration register fields. `MASK_SYS_STATUS_*`, `MASK_SYS_ASYNC_EVENTS`, and `MASK_SYS_PCI_EVENTS` describe interrupt/event bits. `enum cmd_mb_opcodes` defines MicroBlaze mailbox commands from system config through stream state. `enum pipe_state_t`, `enum stream_state_t`, `enum buffer_flags`, and `enum stream_flags` define firmware state/flag meanings. Error macros encode driver, board, resource, context, and realtime errors.

## Control Flow
The header has no executable flow, but `lx_core.c` uses these constants to construct commands, interpret responses, parse event masks, classify buffer slots, map stream/pipe states, and convert firmware errors into diagnostics.

## State and Persistence
Definitions here describe firmware-visible state, not driver-owned storage. They act as the persistent protocol contract between Linux driver source and LX firmware.

## Dependencies and Integration Points
It is included by `lx_core.h` and therefore by both LX implementation files. The constants integrate with PLX doorbell IRQs, MicroBlaze mailbox commands, EtherSound configuration, ALSA stream lifecycle, and proc peak reporting.

## Risks
Incorrect bit positions or masks would corrupt mailbox command object IDs, stream direction, buffer flags, or interrupt handling. Some comments indicate adapted vendor headers and legacy naming; edits should be validated against hardware documentation. Error codes mix warning/error/source/class/code fields, so callers must distinguish firmware-positive codes from Linux negative errno values.

## Test Signals
Probe should correctly configure 64 inputs/outputs and single frequency ratio. Clock detection should classify 44.1/48 kHz counters as expected. Buffer ask/give should identify valid/free/EOB slots through `BF_*` flags. Pipe/stream state polling should decode `PSTATE_*` and `SF_START` correctly. Injected or observed firmware errors should log the expected `ED_*`/`EB_*` class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/lx6464es/lx_defs.h -->
