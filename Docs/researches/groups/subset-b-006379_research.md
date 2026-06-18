# Research: subset-b-006379

Grouped research for ALSA ISA sound drivers under `sources/distributed-fs/ceph-client/sound/isa`. Each section is bounded for reconciliation into the mapped per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd.c -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd.c

## Purpose
`msnd.c` provides common ALSA support routines for Turtle Beach MultiSound cards. It implements host-to-DSP command transfer, shared SRAM queue setup, IRQ reference management, DSP halt/flush helpers, and ALSA PCM playback/capture operations used by the board driver in `msnd_pinnacle.c` and the Classic wrapper build.

## Important APIs, Types, and Functions
- Exported hardware helpers: `snd_msnd_init_queue`, `snd_msnd_send_dsp_cmd`, `snd_msnd_send_word`, `snd_msnd_upload_host`, `snd_msnd_enable_irq`, `snd_msnd_disable_irq`, `snd_msnd_force_irq`, `snd_msnd_dsp_halt`, `snd_msnd_DAPQ`, `snd_msnd_DARQ`, and `snd_msnd_pcm`.
- Queue helpers program DSP-visible queue structures with `JQS_*` fields and address conversion macros from `msnd.h`.
- PCM operations are split into `snd_msnd_playback_ops` and `snd_msnd_capture_ops`, both using I/O memory mmap through `snd_pcm_lib_mmap_iomem`.
- `snd_msnd_DAPQ` submits playback banks to the DSP and sends `HDEX_PLAY_START`; `snd_msnd_DARQ` advances capture queue tails and adjusts two-period capture buffer offsets.

## Control Flow
Playback open sets `F_AUDIO_WRITE_INUSE`, enables IRQs, maps runtime DMA to `chip->mappedbase`, and installs hardware constraints. `hw_params` stores sample width/channels/rate into the three playback DAQ descriptors. `prepare` rewrites playback queue descriptors for the current buffer and period layout. `trigger(START)` marks `F_WRITING` and primes the DSP queue; later DSP interrupts call `snd_msnd_DAPQ` again through `msnd_pinnacle.c`. Stop clears `F_WRITING` and sends `HDEX_PLAY_STOP`.

Capture open similarly enables IRQs and maps runtime DMA to `mappedbase + 0x3000`; `prepare` rewrites capture descriptors, and `trigger(START)` sends `HDEX_RECORD_START`. Stop sends `HDEX_RECORD_STOP`.

Command flow is mostly polling-based: `snd_msnd_send_dsp_cmd` waits for host-command bit `HPCVR_HC` to clear before writing `HP_CVR`; `snd_msnd_send_word` waits for `HPISR_TXDE` then writes high/mid/low bytes to the transmit ports.

## State and Persistence
Runtime state is held in `struct snd_msnd`: flags such as `F_WRITING` and `F_READING`, IRQ reference count, current PCM format, queue pointers, last bank numbers, and DMA-position counters. No persistent disk state exists. Hardware state lives in ISA I/O ports and mapped SRAM queues and is rebuilt during prepare/reset paths.

## Dependencies and Integration Points
This file depends on ALSA core/PCM APIs, Linux I/O port helpers, `msnd.h` register definitions, and board-specific setup that initializes `mappedbase`, queue pointers, IRQs, and DSP firmware. It is consumed by `msnd_pinnacle.c` and mixer code via exported symbols.

## Risks and Test Signals
Risks include polling timeouts with no delays in `snd_msnd_wait_TXDE`/`snd_msnd_wait_HC0`, IRQ reference underflow only logged in `snd_msnd_disable_irq`, and careful reliance on two or three SRAM queue banks. PCM tests should check playback/capture open-close balance, start/stop/suspend triggers, mmap I/O memory behavior, IRQ enable/disable pairing, period elapsed progression, firmware upload failure behavior, and buffer wrap for two-period and three-period configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd.h -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd.h

## Purpose
`msnd.h` is the shared contract for Turtle Beach MultiSound support. It defines default audio parameters, SRAM layout, host-port registers, DSP command/message constants, queue descriptor offsets, the `struct snd_msnd` device state, and function prototypes exported from common and mixer code.

## Important APIs, Types, and Functions
- Constants map DSP SRAM regions: `SRAM_CNTL_START`, `SMA_STRUCT_START`, `DAPQ_DATA_BUFF`, `DARQ_DATA_BUFF`, `DSPQ_OFFSET`, and queue sizes.
- Host-port constants define control/status registers and bits such as `HP_ICR`, `HP_CVR`, `HP_ISR`, `HPICR_RREQ`, `HPISR_TXDE`, and `HPCVR_HC`.
- DSP message and command constants include `HIMT_PLAY_DONE`, `HIMT_RECORD_DONE`, `HDEX_PLAY_START`, `HDEX_RECORD_START`, and `HDEX_AUX_REQ`.
- `struct snd_msnd` carries mapped memory, queue pointers, card/rawmidi handles, resource identifiers, flags, mixer levels, PCM runtime parameters, and active substreams.

## Control Flow
The header itself has no executable control flow, but it shapes all common paths: board code initializes `struct snd_msnd`, common PCM code updates queue and format fields, interrupt code reads `HIMT_*` messages, and mixer code writes SMA offsets through macros defined here and board-specific headers.

## State and Persistence
All state is in memory and hardware. `struct snd_msnd` keeps volatile driver state; the `SMA_*` offsets defined by board headers identify DSP-shared memory that is rewritten on reset/resume.

## Dependencies and Integration Points
It includes `<sound/pcm.h>` and is included by `msnd.c`, `msnd_pinnacle.c`, `msnd_classic.c`, and `msnd_pinnacle_mixer.c`. Board-specific headers extend the generic register map with Classic or Pinnacle SMA layouts.

## Risks and Test Signals
The main risk is that many offsets are hard-coded hardware ABI values. Any change needs hardware or emulation validation. Test signals include successful compilation of both Classic and Pinnacle variants, correct queue address conversion by `PCTODSP_*`, no struct-field mismatch across users, and stable period/capture positions when queue constants change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_classic.c -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_classic.c

## Purpose
`msnd_classic.c` is a wrapper translation unit for the MultiSound Classic/Monterey/Tahiti variant. It defines `MSND_CLASSIC` and includes `msnd_pinnacle.c`, causing the shared board driver to compile with Classic register constants and conditional branches.

## Important APIs, Types, and Functions
This file defines no functions of its own. Its public surface is inherited from the included `msnd_pinnacle.c` build, with names and metadata selected by `MSND_CLASSIC`, `msnd_classic.h`, `LOGNAME`, and `DEV_NAME`.

## Control Flow
Compilation control flow is the whole purpose: defining `MSND_CLASSIC` selects Classic-specific reset, memory ID, IRQ mask, and Pro reset code inside `msnd_pinnacle.c`, while excluding Pinnacle PnP/config-device paths.

## State and Persistence
Runtime state is the same `struct snd_msnd` state used by the included implementation. Classic-specific state includes `memid` and `irqid` values derived from module parameters.

## Dependencies and Integration Points
It depends entirely on `msnd_pinnacle.c`, `msnd.h`, and `msnd_classic.h`. Build integration must compile it as a distinct module/object only where Classic support is enabled.

## Risks and Test Signals
Including a `.c` file is fragile: symbol names, module metadata, and static variables are duplicated per variant and can diverge silently. Test signals are successful Classic build, distinct module registration name `msnd-classic`, correct parameter validation for Classic I/O/memory/IRQ values, and no accidental Pinnacle-only PnP code compiled into the Classic variant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_classic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_classic.h -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_classic.h

## Purpose
`msnd_classic.h` defines the hardware constants for Turtle Beach MultiSound Classic/Monterey/Tahiti cards. It supplies the register offsets, reset values, queue sizes, MIDI routing constants, SMA shared-memory offsets, firmware filenames, and long name used when `MSND_CLASSIC` builds the common board driver.

## Important APIs, Types, and Functions
Key constants include `DSP_NUMIO`, Classic-only host ports `HP_MEMM`, `HP_BITM`, `HP_WAIT`, `HP_DSPR`, `HP_PROR`, `HP_BLKS`, reset and bank-select values, `DSPQ_BUFF_SIZE`, `DSPQ_DATA_BUFF`, `MOP_*` and `MIP_*` MIDI routing masks, Classic `SMA_*` offsets, and firmware names `turtlebeach/msndinit.bin` and `turtlebeach/msndperm.bin`.

## Control Flow
The header provides compile-time configuration. The included `msnd_pinnacle.c` uses these definitions for Classic reset timing, memory bank selection, IRQ mask programming, SMA initialization, and firmware upload.

## State and Persistence
No direct state is stored here. The constants describe persistent hardware ABI positions in SRAM and volatile control register values.

## Dependencies and Integration Points
It is included only under `MSND_CLASSIC`. It pairs with `msnd.h` for common queue and command constants and with `msnd_classic.c` for build selection.

## Risks and Test Signals
The risk is hardware ABI drift: a wrong SMA offset or queue size would corrupt DSP-shared memory. Test signals include Classic firmware loading from the declared filenames, DSP reset success through Classic ports, correct IRQ mask mapping, and mixer/PCM operation against the Classic SMA layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_classic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle.c -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle.c

## Purpose
`msnd_pinnacle.c` is the board-level ALSA driver for Turtle Beach MultiSound Pinnacle/Fiji and, when included through `msnd_classic.c`, Classic variants. It performs ISA/PnP resource discovery, optional logical-device configuration, DSP reset and firmware upload, IRQ handling, PCM/mixer/MIDI attachment, ADC calibration, and power-management restore.

## Important APIs, Types, and Functions
- Probe/init path: `snd_msnd_isa_match`, `snd_msnd_isa_probe`, `snd_msnd_pnp_detect`, `snd_msnd_probe`, `snd_msnd_attach`, `snd_msnd_initialize`, and `snd_msnd_dsp_full_reset`.
- DSP and SRAM setup: `snd_msnd_reset_dsp`, `snd_msnd_init_sma`, `upload_dsp_code`, `snd_msnd_calibrate_adc`, `snd_msnd_send_dsp_cmd_chk`.
- Interrupt processing: `snd_msnd_interrupt` drains `DSPQ`; `snd_msnd_eval_dsp_msg` dispatches `HIMT_PLAY_DONE`, `HIMT_RECORD_DONE`, and DSP error/status messages.
- Pinnacle configuration helpers: `snd_msnd_write_cfg*`, `snd_msnd_write_cfg_logical`, and `snd_msnd_pinnacle_cfg_reset` program logical DSP/MPU/IDE/joystick devices through a config port.
- PM hooks save capture source and MPU input state, reset firmware on resume, restore capture source, and re-enable IRQs.

## Control Flow
For legacy ISA, `snd_msnd_isa_match` validates module parameters. `snd_msnd_isa_probe` creates an ALSA card, optionally programs Pinnacle logical devices, initializes `struct snd_msnd`, probes the DSP, attaches resources, and registers the card. For PnP, `snd_msnd_pnp_detect` activates audio/MPU PnP devices, copies resource starts into the module arrays, initializes the same state, and calls the same probe/attach path.

Attachment requests IRQ/I/O/memory resources, ioremaps 32 KiB SRAM, performs a full DSP reset, creates PCM and mixer devices, optionally creates MPU401 rawmidi with custom open/close hooks that start/stop DSP MIDI input, disables IRQ until needed, calibrates ADC, forces default recording source, and registers the card.

The IRQ handler reads DSP queue head/tail/size, processes queued words, advances the queue head, and acknowledges by reading `HP_RXL`. Playback messages advance DMA position, submit more DAPQ banks, and call `snd_pcm_period_elapsed`. Capture messages advance capture position, repost DARQ banks, and call period elapsed. DSP underflow/overflow messages clear active flags.

## State and Persistence
State is volatile in `struct snd_msnd` and in DSP SRAM. `snd_msnd_init_sma` preserves master volume across repeated initialization with a static `initted` flag, clears both SRAM banks, builds queue pointers, and writes default SMA values. Firmware is loaded from request-firmware files on reset and resume; no driver-managed persistent storage exists.

## Dependencies and Integration Points
This file integrates Linux ISA and PnP buses, request-firmware, ALSA card/PCM/rawmidi APIs, common `msnd.c` routines, `msnd_pinnacle_mixer.c`, and board headers. Firmware dependencies are declared through `MODULE_FIRMWARE`.

## Risks and Test Signals
High-risk areas are firmware availability, shared-memory bank switching under interrupt locking, IRQ disable/enable reference count consistency, reset recursion limit `nresets`, and Classic-vs-Pinnacle conditional compilation. Test signals include non-PnP and PnP probe success, missing firmware errors, playback/capture period interrupts, suspend/resume with active MIDI input, capture-source restoration, digital daughterboard selector behavior, and no IRQ storms after disabling IRQ post-attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle.h -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle.h

## Purpose
`msnd_pinnacle.h` defines Pinnacle/Fiji-specific hardware constants for the MultiSound driver. It covers ISA logical-device configuration registers, DSP control ports, DSP message codes, queue sizes, MIDI routing constants, SMA shared-memory layout, firmware filenames, and user-visible long name.

## Important APIs, Types, and Functions
Important definitions include config registers `IREG_LOGDEVICE`, `IREG_ACTIVATE`, `IREG_IO*_BASE*`, `IREG_IRQ_*`, `IREG_MEM*`; DSP registers `HP_DSPR` and `HP_BLKS`; reset and bank-select values; Pinnacle DSP messages such as `HIDSP_PLAY_UNDER`, `HIDSP_RECQ_OVERFLOW`, and `HIDSP_DAT_IN_OFF`; queue sizes `MIDQ_BUFF_SIZE` and `DSPQ_BUFF_SIZE`; full Pinnacle `SMA_*` offsets for PCM format, mixer, DAT, peaks, and play count; and firmware files `turtlebeach/pndspini.bin` and `turtlebeach/pndsperm.bin`.

## Control Flow
The header contributes compile-time constants consumed by `msnd_pinnacle.c` and `msnd_pinnacle_mixer.c`. Logical-device writes in the board driver rely on the `IREG_*` definitions, while mixer and PCM code rely on the Pinnacle SMA offsets.

## State and Persistence
No state is stored in the header. Its constants describe volatile hardware state in ISA configuration registers and DSP SRAM.

## Dependencies and Integration Points
It integrates with `msnd.h` as the Pinnacle-specific extension and is required by the mixer because the mixer writes Pinnacle-only fields such as mic pot and synth/MHDR volume.

## Risks and Test Signals
Risks are wrong register constants or offsets corrupting card configuration or DSP memory. Test signals include successful logical device activation for DSP/MPU/IDE/joystick, correct firmware request names, successful mixer writes to master/PCM/mic/synth, and correct interpretation of Pinnacle DSP status messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle_mixer.c -->
# sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle_mixer.c

## Purpose
`msnd_pinnacle_mixer.c` implements ALSA mixer controls for MultiSound Pinnacle and shared Classic-compatible controls. It maps ALSA kcontrols to mixer-level arrays in `struct snd_msnd`, writes scaled values into DSP SMA fields, and sends auxiliary DSP commands for hardware potentiometer and capture-source changes.

## Important APIs, Types, and Functions
- Public functions: `snd_msndmix_new`, `snd_msndmix_setup`, and `snd_msndmix_force_recsrc`.
- Capture selector callbacks: `snd_msndmix_info_mux`, `snd_msndmix_get_mux`, `snd_msndmix_put_mux`, and `snd_msndmix_set_mux`.
- Volume callbacks: `snd_msndmix_volume_info`, `snd_msndmix_volume_get`, `snd_msndmix_volume_put`, and internal `snd_msndmix_set`.
- Update macros `update_volm`, `update_potm`, and `update_pot` write SMA fields and send `HDEX_AUX_REQ` when hardware pots must be applied.

## Control Flow
`snd_msndmix_new` initializes `mixer_lock`, sets the mixer name, and registers master, PCM, aux, line, mic, monitor, and capture-source controls. `put` handlers convert user 0-100 values to 8-bit pot and 16-bit DSP levels, update cached `left_levels`/`right_levels`, and write the appropriate SMA fields. Master changes cascade to PCM, monitor, aux, and synth values because several controls are master-scaled. Capture-source changes send an auxiliary request selecting analog, MASS/synth, or SPDIF if digital input exists.

## State and Persistence
Mixer state is cached in `left_levels`, `right_levels`, and `recsrc` in `struct snd_msnd`. `snd_msndmix_setup` replays cached state into the SMA after DSP initialization or reset. There is no disk persistence.

## Dependencies and Integration Points
The mixer depends on ALSA control APIs, common DSP command helpers from `msnd.c`, state from `msnd.h`, and Pinnacle SMA offsets from `msnd_pinnacle.h`. It is called by board attach and reset/resume code.

## Risks and Test Signals
Risks include modulo-based volume normalization (`% 101`) silently wrapping invalid userspace values, Classic paths rejecting mic volume but still registering the mic control, and capture-source values depending on `F_HAVEDIGITAL`. Test signals include mixer control enumeration with and without digital daughterboard, ALSA control change return values, correct master-scaled volume writes after reset, and hardware response to line/mic/aux pot commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/msnd/msnd_pinnacle_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opl3sa2.c -->
# sources/distributed-fs/ceph-client/sound/isa/opl3sa2.c

## Purpose
`opl3sa2.c` is the ALSA ISA/PnP driver for Yamaha OPL3-SA2/SA3-family sound cards. It configures the card control port, registers a WSS PCM codec, mixer, timer, optional OPL3 synth, optional MPU401 MIDI, shared IRQ handler, and suspend/resume support.

## Important APIs, Types, and Functions
- `struct snd_opl3sa2` stores control-port resource, version, IRQ, WSS/OPL/rawmidi handles, cached control registers, and master-control pointers.
- Detection and register helpers: `snd_opl3sa2_detect`, `snd_opl3sa2_read`, `snd_opl3sa2_write`.
- IRQ path: `snd_opl3sa2_interrupt` dispatches OPL3, MPU401, WSS, and hardware-volume notifications from `OPL3SA2_IRQ_STATUS`.
- Mixer path: `snd_opl3sa2_mixer` renames WSS controls, adds OPL3SA controls, and registers SA3 tone/3D controls when available.
- Bus paths: ISA match/probe and both PnP BIOS and PnP card drivers call `snd_opl3sa2_probe`.

## Control Flow
Module arrays provide resources for legacy ISA; PnP fills them from active PnP devices. Card creation initializes register locking and card names. Probe detects the chip by validating `MISC` and `MIC` register behavior, powers the device to D0, programs IRQ/DMA routing, creates a WSS codec at `wss_port + 4`, attaches PCM/mixer/timer, adds Yamaha-specific mixer controls, optionally creates OPL3 and MPU401 devices, builds `longname`, and registers the card.

## State and Persistence
The driver caches control-register values in `ctlregs` so mixer gets can avoid hardware reads and resume can restore registers. Power management writes D3 on suspend, saves state in memory, resumes by powering D0, replaying cached registers, and resuming the WSS codec. There is no persistent storage.

## Dependencies and Integration Points
It integrates Linux ISA and PnP subsystems with ALSA WSS, OPL3, MPU401, control, and power APIs. Hardware-volume IRQs notify ALSA controls by ID to keep userspace mixers in sync.

## Risks and Test Signals
Risks include shared IRQ demultiplexing, hardware-volume notification correctness, resource arrays being mutated by PnP, and resume replay ordering. Test signals include PnP BIOS and PnP-card probe, legacy parameter probe, WSS playback/capture, OPL3 timer/hwdep creation, MPU IRQ behavior, hardware volume button notification, and suspend/resume preserving mixer settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opl3sa2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/opti9xx/Makefile

## Purpose
This Makefile builds ALSA ISA modules for OPTi 9xx and Miro sound cards. It maps Kconfig symbols to module objects and defines the object composition for each module.

## Important APIs, Types, and Functions
There are no C APIs. Build variables define `snd-opti92x-ad1848-y`, `snd-opti92x-cs4231-y`, `snd-opti93x-y`, and `snd-miro-y`, then append them to `obj-*` for `CONFIG_SND_OPTI92X_AD1848`, `CONFIG_SND_OPTI92X_CS4231`, `CONFIG_SND_OPTI93X`, and `CONFIG_SND_MIRO`.

## Control Flow
Kbuild selects the object based on enabled config symbols. The `opti92x-cs4231.o` and `opti93x.o` objects are tiny wrappers that include `opti92x-ad1848.c` with different preprocessor symbols.

## State and Persistence
No runtime state exists. Build configuration controls which modules are compiled.

## Dependencies and Integration Points
It integrates the `opti9xx` directory with the kernel ALSA sound build and relies on wrapper C files for variant-specific preprocessor builds.

## Risks and Test Signals
Risks are wrong module composition or missing wrapper object selection. Test signals are successful builds for each Kconfig option and distinct generated modules with expected module descriptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/miro.c -->
# sources/distributed-fs/ceph-client/sound/isa/opti9xx/miro.c

## Purpose
`miro.c` is the ALSA driver for Miro miroSOUND PCM1 pro, PCM12, and PCM20 Radio cards. It combines OPTi 82C924/82C929 WSS configuration with a Miro ACI command/mixer interface, optional MPU401, optional OPL4, proc reporting, ISA/PnP probing, and card-model-dependent controls.

## Important APIs, Types, and Functions
- `struct snd_miro` stores OPTi hardware information, management-control resources, WSS/IRQ/DMA/MPU settings, card pointer, and ACI pointer.
- ACI API: `snd_aci_cmd` and `snd_aci_get_aci` are exported; internal helpers `aci_busy_wait`, `aci_write`, `aci_read`, `aci_getvalue`, and `aci_setvalue` serialize access with `aci_mutex`.
- Mixer callbacks handle capture solo mode, preamp, line amp, stereo volumes, seven-band EQ, radio/line controls, and model-specific additions.
- Probe flow: `snd_card_miro_detect`, `snd_card_miro_aci_detect`, `snd_miro_configure`, `snd_miro_probe`, `snd_miro_isa_probe`, and `snd_miro_pnp_probe`.

## Control Flow
Legacy ISA creates a card, detects the OPTi chip through passworded management registers, auto-finds WSS/MPU/IRQ/DMA resources when requested, detects ACI at port `0x344` or `0x354`, initializes ACI, configures OPTi WSS and MPU routing, creates WSS PCM/mixer/timer, adds Miro ACI mixer controls according to product ID, optionally creates MPU401 and OPL4, applies ACI defaults, and registers the card. PnP activates audio/MPU/MC devices, fills the same global resource variables, initializes as 82C924, and uses the same probe path.

## State and Persistence
ACI state is held in a single static `aci_device`, including vendor/product/version, port, mutex, and cached amp/preamp/solomode. Runtime resources and mixer state are in `struct snd_miro`; proc output reports current values. No persistent storage is used.

## Dependencies and Integration Points
The driver integrates Linux ISA/PnP, ALSA WSS/MPU401/OPL4/control/proc APIs, legacy resource finders, and the public ACI header. Exported ACI access can be used by related code.

## Risks and Test Signals
Risks include the static single ACI device limiting concurrency, long sleeps in `aci_busy_wait`, mutable global module-resource variables after PnP detection, unimplemented suspend/resume, and product-ID-specific mixer registration. Test signals include PCM1/PCM12/PCM20 detection, ACI ID/version reads, ACI mixer get/put round trips, WSS mode and IDE enable options, proc report correctness, PnP fallback to ISA, and OPL4/MPU optional-device failure tolerance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/miro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti92x-ad1848.c -->
# sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti92x-ad1848.c

## Purpose
`opti92x-ad1848.c` is the shared implementation for OPTi 82C92x AD1848, OPTi 82C92x CS4231, and OPTi 82C93x ALSA drivers. Preprocessor symbols select codec type and 93x-specific control paths. The driver configures OPTi management registers, creates WSS PCM/mixer/timer services, optional MPU401 and OPL3/OPL4 devices, PnP/ISA probing, and power management.

## Important APIs, Types, and Functions
- `struct snd_opti9xx` tracks card, hardware ID, password, management-control base, indirect register base for 93x, codec pointer, lock, WSS base, and IRQ.
- Register access: `snd_opti9xx_init`, `snd_opti9xx_read`, `snd_opti9xx_write`, and `snd_opti9xx_write_mask`.
- Hardware programming: `snd_opti9xx_configure`, `snd_opti9xx_read_check`, and `snd_card_opti9xx_detect`.
- Variant-specific code under `OPTi93X` adds custom mixer controls and `snd_opti93x_interrupt`.
- Probe paths include `snd_opti9xx_probe`, ISA match/probe, PnP card probe/remove, suspend/resume, and module init/exit.

## Control Flow
ISA probe auto-finds legacy resources if requested, creates a card, scans supported hardware IDs by programming passworded management-register access, configures WSS base/IRQ/DMA/MPU routing, creates the WSS codec, PCM, mixer, optional timer, and optional OPTi93x mixer/IRQ. It then registers optional MPU401 and FM/OPL devices. PnP probe activates PnP child devices, derives audio/MC/MPU resources, maps PnP IDs to hardware IDs, verifies management-register access, then uses the same probe path.

## State and Persistence
Runtime state is in `struct snd_opti9xx` and global module parameters that may be overwritten by PnP resources. PM suspend moves the ALSA card to D3 and suspends WSS; resume re-runs `snd_opti9xx_configure`, resumes the codec, and returns to D0. There is no disk persistence.

## Dependencies and Integration Points
It depends on Linux ISA/PnP/I/O helpers, ALSA WSS, MPU401, OPL3, OPL4, initval legacy resource scanning, and optional 93x-specific WSS register definitions. Wrapper files compile this source under `CS4231` or `OPTi93X`.

## Risks and Test Signals
Risks include compile-time variant coupling, mutable globals across probe paths, invalid DMA pairing, non-fatal resource validation branches that skip programming but continue, and IRQ handling differences between WSS-shared and OPTi93x custom interrupts. Test signals include AD1848, CS4231, and OPTi93x module builds; ISA and PnP probe; WSS PCM playback/capture; timer creation where enabled; OPL4 fallback to OPL3; MPU optional failure handling; and resume restoring register routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti92x-ad1848.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti92x-cs4231.c -->
# sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti92x-cs4231.c

## Purpose
`opti92x-cs4231.c` is a wrapper build unit for OPTi 82C92x cards using CS4231/CS4248-compatible codec behavior. It defines `CS4231` and includes `opti92x-ad1848.c`.

## Important APIs, Types, and Functions
It defines no independent runtime APIs. The included implementation gains CS4231-specific module description, a second DMA parameter, CS4231 fix bit programming, and WSS timer creation.

## Control Flow
Build-time control flow selects `CS4231` branches in `opti92x-ad1848.c`. Runtime probe, configuration, PnP, PM, and registration are inherited from the included file.

## State and Persistence
State is inherited from `struct snd_opti9xx` and module globals in the included implementation. The CS4231 variant adds `dma2`.

## Dependencies and Integration Points
It depends on the shared OPTi implementation and the Kbuild target `snd-opti92x-cs4231.o`.

## Risks and Test Signals
Risks are wrapper-induced symbol/metadata coupling and behavior drift from the AD1848 base. Test signals are successful CS4231 module build, second DMA validation, WSS timer availability, and correct module description.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti92x-cs4231.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti93x.c -->
# sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti93x.c

## Purpose
`opti93x.c` is a wrapper build unit for OPTi 82C930/82C931/82C933 cards. It defines `OPTi93X` and includes `opti92x-ad1848.c`.

## Important APIs, Types, and Functions
It defines no independent functions. The included implementation gains OPTi93x-specific hardware IDs, indirect management register access, second DMA support, custom mixer controls, custom interrupt handler, and PnP ID mapping for OPT0931.

## Control Flow
Build-time `OPTi93X` changes detection order, configuration register programming, WSS hardware type, IRQ request path, and module description. Runtime flows are inherited from the shared source.

## State and Persistence
State is inherited from `struct snd_opti9xx`; OPTi93x adds indirect-register resource state and `dma2`.

## Dependencies and Integration Points
It depends on the shared OPTi source and Kbuild target `snd-opti93x.o`.

## Risks and Test Signals
Risks are `.c` inclusion coupling and custom interrupt behavior diverging from normal WSS. Test signals are successful OPTi93x build, indirect MC resource request, custom mixer replacement, playback/capture period interrupt delivery, and PnP probe for OPT0931.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/opti9xx/opti93x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/Makefile -->
# sources/distributed-fs/ceph-client/sound/isa/sb/Makefile

## Purpose
This Makefile builds ALSA ISA Sound Blaster-family modules, including common SB support, SB8/SB16 DSP modules, SB/AWE cards, EMU8000 sequencer synth support, Jazz16, and optional SB16 CSP composition.

## Important APIs, Types, and Functions
There are no runtime APIs. Build variables compose modules: `snd-sbawe-y := sbawe.o emu8000.o`, `snd-emu8000-synth-y := emu8000_synth.o emu8000_callback.o emu8000_patch.o emu8000_pcm.o`, and `snd-jazz16-y := jazz16.o`. Config symbols add modules to `obj-*`.

## Control Flow
Kbuild includes object lists according to `CONFIG_SND_*`. If `CONFIG_SND_SB16_CSP=y`, the CSP object is linked into both SB16 and SBAWE modules. `CONFIG_SND_SBAWE_SEQ` controls the EMU8000 synth plugin module.

## State and Persistence
No runtime state exists. Build configuration controls module contents.

## Dependencies and Integration Points
It integrates `emu8000.c` into the AWE card driver and the separate sequencer synth plugin with callback, patch, and PCM support objects.

## Risks and Test Signals
Risks include missing EMU8000 companion objects or incorrect CSP linkage under built-in/module combinations. Test signals include successful builds for SB common, SB8/SB16, SBAWE, SBAWE sequencer, and Jazz16 config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000.c

## Purpose
`emu8000.c` implements low-level control for the Creative EMU8000 wavetable synth used by AWE32/AWE64. It provides register I/O helpers, DMA channel setup, chip detection, hardware initialization, DRAM sizing, FM refresh setup, equalizer/chorus/reverb programming, ALSA mixer controls, and sequencer-device creation.

## Important APIs, Types, and Functions
- Exported register and DMA helpers: `snd_emu8000_poke`, `snd_emu8000_peek`, `snd_emu8000_poke_dw`, `snd_emu8000_peek_dw`, and `snd_emu8000_dma_chan`.
- Hardware init: `snd_emu8000_detect`, `init_audio`, `init_dma`, `init_arrays`, `size_dram`, `snd_emu8000_init_fm`, and `snd_emu8000_init_hw`.
- Effect APIs: `snd_emu8000_load_chorus_fx`, `snd_emu8000_update_chorus_mode`, `snd_emu8000_load_reverb_fx`, `snd_emu8000_update_reverb_mode`, and `snd_emu8000_update_equalizer`.
- Mixer creation: `snd_emu8000_create_mixer` registers bass, treble, chorus, reverb, and FM depth controls.
- Entry point: `snd_emu8000_new` allocates `struct snd_emu8000`, requests ports, initializes hardware, creates mixers, and registers a sequencer device.

## Control Flow
`snd_emu8000_new` validates sequencer-port count, allocates state, requests three I/O port windows, sets defaults, detects the chip, initializes the hardware, registers mixer controls, and creates a sequencer device carrying the hardware pointer. Hardware initialization resets all channels, writes vendor initialization arrays, initializes FM/refresh voices, sizes DRAM by write/read probes, enables audio, and applies default effect modes.

## State and Persistence
`struct snd_emu8000` stores port bases, last selected register, DRAM size, defaults for bass/treble/effect modes, control locks, card pointer, and later emux/memory headers. Global arrays hold predefined and uploaded chorus/reverb modes; uploaded modes persist only while the module is loaded.

## Dependencies and Integration Points
The file depends on ALSA core/control/initval, EMU8000 register macros, Linux I/O and user-copy helpers, and the sequencer device framework. It is linked into `snd-sbawe`; `emu8000_synth.c` consumes the sequencer device and the callback/patch/PCM files consume exported helpers.

## Risks and Test Signals
Risks include busy-wait loops on hardware bits, global effect mode arrays shared across devices, DRAM sizing writes to sample RAM, and user-supplied effect structures copied from userspace. Test signals include port request failure handling, chip detect, DRAM size logs, mixer get/put updating hardware, effect upload bounds checks, sequencer device creation, and no stuck waits during init or DMA operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_callback.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_callback.c

## Purpose
`emu8000_callback.c` binds the generic ALSA emux sequencer engine to EMU8000 hardware. It provides voice allocation, voice prepare/trigger/release/update/reset/terminate operations, SoundFont sample callbacks, SysEx effect handling, optional OSS emulation ioctl handling, and custom effect loading.

## Important APIs, Types, and Functions
- `snd_emu8000_ops_setup` installs `emu8000_ops` into `hw->emu`.
- Emux operators include `get_voice`, `start_voice`, `trigger_voice`, `release_voice`, `update_voice`, `terminate_voice`, `reset_voice`, `snd_emu8000_sample_new`, `snd_emu8000_sample_free`, `snd_emu8000_sample_reset`, `load_fx`, and `sysex`.
- Hardware setters include `set_pitch`, `set_volume`, `set_pan`, `set_fmmod`, `set_tremfreq`, `set_fm2frq2`, `set_filterQ`, and `snd_emu8000_tweak_voice`.

## Control Flow
When emux needs a voice, `get_voice` ranks channels by off, released/pending, or playing state and reuses the oldest suitable voice, also checking single-shot samples that already reached loop end. `start_voice` silences the channel, programs pitch, envelopes, LFOs, pan, loop points, chorus, filter Q, current address, and target values. `trigger_voice` starts the volume envelope and sets reverb/pitch target. Runtime updates selectively rewrite pitch, volume, pan, modulation, tremolo, LFO2, or filter Q. Release and terminate write release or forced-off envelope values.

## State and Persistence
Voice state is managed by `snd_emux` and per-voice register snapshots. The file mutates hardware registers directly and updates effect mode fields in `struct snd_emu8000` for SysEx/OSS commands. No persistent storage is used.

## Dependencies and Integration Points
It depends on `emu8000_local.h`, ALSA emux, SoundFont sample callbacks from `emu8000_patch.c`, and effect functions from `emu8000.c`. It is loaded as part of `snd-emu8000-synth`.

## Risks and Test Signals
Risks include voice stealing semantics, single-shot completion detection based on CCCA address, signed modulation/pitch clamping, and userspace effect payload handling after a fixed 16-byte header skip. Test signals include MIDI note on/off, voice reuse under polyphony pressure, real-time controller updates for pitch/volume/pan/modulation, GS SysEx chorus/reverb changes, OSS ioctl compatibility when enabled, and SoundFont loading callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_local.h -->
# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_local.h

## Purpose
`emu8000_local.h` is the private header shared by the EMU8000 synth plugin files. It includes common kernel and ALSA headers and declares cross-file callbacks for sample memory management, emux operator setup, and PCM device creation.

## Important APIs, Types, and Functions
It declares `snd_emu8000_sample_new`, `snd_emu8000_sample_free`, `snd_emu8000_sample_reset`, `snd_emu8000_ops_setup`, and `snd_emu8000_pcm_new`.

## Control Flow
There is no executable control flow. The declarations connect `emu8000_synth.c` to operator setup in `emu8000_callback.c`, sample loading in `emu8000_patch.c`, and optional PCM creation in `emu8000_pcm.c`.

## State and Persistence
No state is declared here beyond included external structures. Runtime state lives in `struct snd_emu8000`, `struct snd_emux`, and memory-header structures from ALSA.

## Dependencies and Integration Points
It depends on `<sound/emu8000.h>` and `<sound/emu8000_reg.h>`, plus core kernel memory/scheduler headers. It is included by all `snd-emu8000-synth` component files.

## Risks and Test Signals
Risks are mainly interface drift between companion C files. Test signals include successful compilation of all EMU8000 synth objects and correct linkage of patch/callback/PCM functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_patch.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_patch.c

## Purpose
`emu8000_patch.c` implements SoundFont sample-memory callbacks for the EMU8000 synth. It allocates sample blocks, converts userspace sample data, writes it into EMU8000 DRAM through hardware DMA registers, expands reverse/bidirectional loops, appends blank loops when needed, frees sample blocks, and terminates voices on sample reset.

## Important APIs, Types, and Functions
- Public callbacks: `snd_emu8000_sample_new`, `snd_emu8000_sample_free`, and `snd_emu8000_sample_reset`.
- DMA helpers: `snd_emu8000_open_dma`, `snd_emu8000_close_dma`, `snd_emu8000_write_wait`, and `write_word`.
- `read_word` handles 8-bit to 16-bit conversion, endian conversion, and unsigned-to-signed conversion.
- Module parameter `emu8000_reset_addr` optionally resets the hardware write address for each word to avoid lost writes.

## Control Flow
On new sample load, the driver computes true size, allocates memory from the emux memory header, validates user memory, translates byte offset to EMU8000 word address, terminates all voices, reserves voices for DMA, sets the write address, streams sample words from userspace, conditionally duplicates reverse-loop data, appends blank loop samples, adjusts sample start/end/loop addresses to DRAM absolute addresses, closes DMA, and reinitializes FM refresh voices.

## State and Persistence
Sample allocation state is stored in `sp->block` and the emux memory header. The sample metadata is mutated in place to include true size and DRAM-based addresses. Data persists only in card DRAM while loaded.

## Dependencies and Integration Points
It depends on `emu8000_local.h`, ALSA soundfont/emux memory APIs, EMU8000 DMA helper functions from `emu8000.c`, and userspace copy/access helpers. It is used through the emux operator table installed by `emu8000_callback.c`.

## Risks and Test Signals
Risks include memory leaks on errors after allocation, slow or interruptible long sample writes, unchecked `get_user` result in `read_word`, and mutation of loop metadata for reverse/bidir loops. Test signals include loading 8-bit, 16-bit, unsigned, single-shot, reverse-loop, and bidirectional-loop SoundFonts; ENOSPC on small DRAM; interrupting large loads; freeing samples; and verifying no voices remain locked after load failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_patch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_pcm.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_pcm.c

## Purpose
`emu8000_pcm.c` exposes an ALSA playback-only PCM device that uses EMU8000 sample DRAM and wavetable voices as a PCM playback engine. It allocates DRAM buffers, writes PCM samples into card memory, sets up one or two voices, starts/stops playback, and uses a software timer to report periods.

## Important APIs, Types, and Functions
- `struct snd_emu8k_pcm` stores the EMU8000 pointer, substream, memory block, offsets, buffer/period sizes, loop starts, pitch, panning, playback pointer state, voice count, DRAM/timer/running flags, and timer lock.
- PCM ops: `emu8k_pcm_open`, `emu8k_pcm_close`, `emu8k_pcm_hw_params`, `emu8k_pcm_hw_free`, `emu8k_pcm_prepare`, `emu8k_pcm_trigger`, `emu8k_pcm_pointer`, `emu8k_pcm_copy`, and `emu8k_pcm_silence`.
- DRAM helpers: `emu8k_open_dram_for_pcm`, `emu8k_close_dram`, `snd_emu8000_write_wait`, `setup_voice`, `start_voice`, and `stop_voice`.
- Public creator: `snd_emu8000_pcm_new`.

## Control Flow
Open allocates per-substream state and constrains period time to timer granularity. `hw_params` allocates a card DRAM block large enough for audio plus blank loop padding. `prepare` computes pitch from sample rate, loop starts, channel panning, opens DRAM for PCM if needed, clears blank regions, and programs voices. Copy/silence writes frames into EMU8000 DRAM through SMALW/SMARW/SMLD/SMRD. Trigger start starts each voice and a one-jiffy timer; the timer reads current address from CCCA, computes pointer deltas and period transitions, then calls `snd_pcm_period_elapsed`. Trigger stop stops voices and deletes the timer.

## State and Persistence
State is per-open runtime state in `struct snd_emu8k_pcm` and a memory block from `emu->memhdr`. DRAM contents persist while the PCM buffer is allocated. No disk persistence exists.

## Dependencies and Integration Points
It depends on `emu8000_local.h`, ALSA PCM APIs, EMU8000 register helpers, emux voice locking, and the memory header created by `emu8000_synth.c`. It is created only when EMU8000 DRAM is available.

## Risks and Test Signals
Risks include timer-based period accounting drift, voice lock/unlock balance, memory block cleanup when DRAM was opened, signal interruption returning `-EAGAIN` during copy/silence, and stereo interleaving through separate left/right write ports. Test signals include mono/stereo playback, continuous sample-rate pitch calculation, large buffer/period combinations, start/stop races, hw_params reallocation, silence fill, pointer wrap, and module removal while PCM exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_synth.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_synth.c

## Purpose
`emu8000_synth.c` is the ALSA sequencer-driver plugin for EMU8000 hardware. It receives the hardware pointer from the sequencer device created by `snd_emu8000_new`, creates an emux synthesizer instance, allocates sample memory management, registers sequencer ports, optionally creates an EMU8000 PCM device, and frees those resources on removal.

## Important APIs, Types, and Functions
- `snd_emu8000_probe` creates and registers the emux device.
- `snd_emu8000_remove` destroys optional PCM, emux, and memory-header resources.
- `emu8000_driver` is a `struct snd_seq_driver` with ID `SNDRV_SEQ_DEV_ID_EMU8000` and argument size `sizeof(struct snd_emu8000 *)`.

## Control Flow
Probe fetches the `struct snd_emu8000 *` from the seq-device argument, rejects missing or already-bound hardware, allocates `snd_emux`, installs EMU8000 ops, sets voice count and port counts, creates `snd_util_memhdr` sized to detected DRAM, configures MIDI port exposure, registers the emux synth, and creates PCM playback if DRAM size is nonzero. Remove reverses the sequence.

## State and Persistence
The file populates `hw->emu`, `hw->memhdr`, and `dev->driver_data`. Sample memory state is in the memory header and is freed on removal. No disk persistence exists.

## Dependencies and Integration Points
It depends on ALSA sequencer driver helpers, emux APIs, `emu8000_local.h`, callback setup, and PCM creation. It is built as `snd-emu8000-synth`.

## Risks and Test Signals
Risks include partial-registration cleanup, double-probe protection, and ordering between PCM device free and emux/memory teardown. Test signals include seq-driver autoload/probe, emux port availability, SoundFont memory allocation, optional PCM creation only when DRAM exists, and clean module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/emu8000_synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/jazz16.c -->
# sources/distributed-fs/ceph-client/sound/isa/sb/jazz16.c

## Purpose
`jazz16.c` is the ALSA ISA driver for Media Vision Jazz16-based sound cards. It detects/configures the Jazz16 DSP, creates Sound Blaster DSP PCM and mixer devices, optional OPL3 and MPU401 devices, and basic suspend/resume support.

## Important APIs, Types, and Functions
- Module arrays configure card index/id/enable, DSP port, MPU port, IRQs, and 8/16-bit DMAs.
- Detection/configuration helpers: `jazz16_configure_ports`, `jazz16_detect_board`, and `jazz16_configure_board`.
- Bus callbacks: `snd_jazz16_match`, `snd_jazz16_probe`, PM suspend/resume, and `snd_jazz16_driver`.
- `jazz16_interrupt` delegates to `snd_sb8dsp_interrupt`.

## Control Flow
Match validates enabled flag, DSP port, DMA choices, MPU port, and MPU IRQ. Probe creates the card, auto-selects IRQ/DMA resources when requested, optionally configures the wakeup port `0x201` to map DSP and MPU ports, resets and identifies the DSP, creates an SB DSP instance, sends Jazz16 DMA/IRQ configuration commands, creates SB PCM and mixer, optionally creates OPL3 and MPU401 devices, registers the card, and stores driver data.

## State and Persistence
`struct snd_card_jazz16` stores the `struct snd_sb *` needed for suspend/resume. Runtime state is otherwise held by ALSA SB, mixer, OPL3, and MPU subsystems. No persistent storage exists.

## Dependencies and Integration Points
It integrates Linux ISA registration, ALSA Sound Blaster common/DSP/mixer APIs, OPL3, MPU401, legacy resource finders, and PM helpers.

## Risks and Test Signals
Risks include use of fixed config port `0x201`, resource mismatch where probed `xirq`/`xdma*` are not consistently passed to `snd_sbdsp_create` in the current code path, limited valid DMA/IRQ mappings, and optional-device failures. Test signals include board detection across wakeup indices, Jazz16 revision/model reads, SB PCM playback, mixer suspend/resume, OPL3 optional creation, MPU optional creation, and validation that auto-selected IRQ/DMA values are actually used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/sb/jazz16.c -->
