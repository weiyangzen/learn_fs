# subset-b-006406 Research

Grouped research for the subset B work item. Each section preserves the original source path and is intended to be split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_wm87x6.c -->
# sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_wm87x6.c

## Purpose

This file implements the Oxygen/CMI8788 model support for Asus cards using Wolfson WM8776 and WM8766 codecs: Xonar DS/DSX and Xonar HDAV1.3 Slim. It defines board-specific initialization, suspend/resume, GPIO handling, codec register programming, ALSA mixer controls, HDMI integration for the Slim model, and model selection based on PCI subdevice IDs.

## Important APIs, Types, And Functions

- `struct xonar_wm87x6` extends the generic Xonar model data with cached WM8776/WM8766 register arrays, control pointers for mutually exclusive ADC mux controls, limiter/ALC control pointers, an optional headphone jack, and HDMI state.
- `wm8776_write_spi()`, `wm8776_write_i2c()`, `wm8776_write()`, and `wm8776_write_cached()` abstract codec writes and keep `wm8776_regs[]` synchronized for controls and resume.
- `wm8766_write()` and `wm8766_write_cached()` do the same for the WM8766 surround DAC over SPI.
- `xonar_ds_init()`, `xonar_hdav_slim_init()`, cleanup, suspend, and resume callbacks become the `oxygen_model` lifecycle hooks.
- `update_wm8776_volume()`, `update_wm87x6_volume()`, `update_wm8776_mute()`, `update_wm87x6_mute()`, and `update_wm8766_center_lfe_mix()` are the callbacks consumed by the common Oxygen PCM/mixer code.
- Mixer callbacks implement headphone volume/switch, ADC input volume, ADC mux, ADC high-pass filter, WM8776 limiter/ALC mode and parameters, HDMI output switch, and DS-specific front/mic/line/aux capture controls.
- `get_xonar_wm87x6_model()` maps PCI subdevices `0x838e`, `0x8522`, and `0x835e` to the DS, DSX, and HDAV Slim models.

## Control Flow

During probe, the common Oxygen driver calls `get_xonar_wm87x6_model()` and then the selected model's `init` callback. DS initialization sets anti-pop/output GPIO metadata, initializes both codecs, configures GPIO direction/data/interrupts for input routing and headphone detect, enables output, creates the headphone jack, reports the current jack state, and registers codec component names. HDAV Slim initialization initializes WM8776, configures HDMI/firmware GPIO pins, initializes HDMI support, enables output, and adds the WM8776 component.

PCM parameter callbacks are light. The WM8776 ADC path changes master-rate control when capture exceeds 48 kHz. HDAV Slim DAC params delegate to `xonar_set_hdmi_params()`. The normal Oxygen mixer invokes the file's DAC volume/mute callbacks, which update cached codec registers and use codec master-update bits so stereo or multi-channel volume changes latch coherently.

GPIO interrupts call `xonar_ds_gpio_changed()`, which re-reads headphone detect under `chip->mutex`, routes front L/R output between speaker and headphone paths, mutes or unmutes the WM8766 surround codec, and reports `SND_JACK_HEADPHONE`.

Mixer creation adds static control templates, captures pointers to the line and mic mux controls, and adds the limiter/ALC dependent controls. The "Level Control" enum toggles WM8776 limiter/ALC enable and changes the active/inactive access state of the mode-specific controls.

## State And Persistence

The persistent runtime state is in `struct xonar_wm87x6` and the shared `struct oxygen`. Codec register caches are authoritative for ALSA control reads, change detection, and resume reprogramming. `chip->dac_volume[]` and `chip->dac_mute` remain common Oxygen state. GPIO routing and HDMI state are hardware-backed and restored through resume callbacks. There is no disk persistence; settings live only while the ALSA card instance exists.

## Dependencies And Integration Points

This file integrates with the Oxygen PCI framework through `struct oxygen_model`. It depends on common Xonar helpers (`xonar_enable_output()`, GPIO bit control callbacks, HDMI helpers), Oxygen bus helpers (`oxygen_write_spi()`, `oxygen_write_i2c()`, GPIO register helpers), ALSA control/jack/proc APIs, and Wolfson register definitions from `wm8776.h` and `wm8766.h`.

## Risks

- Cached register correctness is critical. If a write path forgets to mask update bits or update the cache, future ALSA reads and resume restore stale values.
- The DS line and mic mux controls are mutually exclusive and notify each other manually; changes in control names or missing pointer capture break notification.
- GPIO polarity is board-specific. Headphone detect is active low, while Slim HDMI disable is inverted through the generic GPIO control helper.
- Limiter/ALC controls reuse `private_value` both as cached user value and bit-field metadata, so invalid masks or mode flags can silently program the wrong WM8776 field.
- The DS volume update path appears to compare right DAC volume against `WM8776_DACLVOL` when forming `to_change`; this should be reviewed if volume updates are suspected to skip the right channel.

## Test Signals

Useful validation includes probe on each subdevice, suspend/resume with register dumps, ALSA control read/write coverage for all WM8776 fields, headphone jack plug/unplug interrupt tests, capture mux exclusivity checks, 96 kHz capture validation for ADC over-sampling, multi-channel playback volume/mute tests, and HDAV Slim HDMI audio/control tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/oxygen/xonar_wm87x6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/Makefile

## Purpose

This Makefile builds the ALSA Digigram PCXHR PCI driver object. It declares the constituent object files for `snd-pcxhr.o` and connects the composite module to `CONFIG_SND_PCXHR`.

## Important APIs, Types, And Functions

- `snd-pcxhr-y` lists `pcxhr.o`, `pcxhr_hwdep.o`, `pcxhr_mixer.o`, `pcxhr_core.o`, and `pcxhr_mix22.o`.
- `obj-$(CONFIG_SND_PCXHR) += snd-pcxhr.o` lets Kbuild include the module only when the kernel configuration enables the driver.

## Control Flow

Kbuild compiles each listed object and links them into the single `snd-pcxhr` module. Runtime entry comes from `pcxhr.o`, whose `module_pci_driver()` registers the PCI driver.

## State And Persistence

The file has no runtime state. Its only persistent effect is build-system composition.

## Dependencies And Integration Points

The Makefile depends on Kbuild composite-object conventions and the `CONFIG_SND_PCXHR` symbol defined elsewhere in ALSA/Kconfig.

## Risks

Omitting one object breaks symbols across the driver stack, because the implementation is split across PCM/probe, firmware, mixer, core mailbox/IRQ, and HR222-specific code. Adding files without updating this list leaves code unlinked.

## Test Signals

Build `CONFIG_SND_PCXHR=m` and verify `snd-pcxhr.ko` links with no unresolved symbols. Also test `CONFIG_SND_PCXHR=n` to ensure no PCXHR objects are built.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr.c -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr.c

## Purpose

This is the main ALSA PCI driver for Digigram PCXHR-compatible cards. It registers supported PCI IDs, maps board parameters, allocates one manager for a physical PCI device, creates one or more ALSA cards for the board's logical chips, implements PCM callbacks, owns sample-clock selection at the stream layer, provides proc diagnostics, and tears down hardware on remove.

## Important APIs, Types, And Functions

- Module parameters `index`, `id`, `enable`, and `mono` control ALSA card registration and mono-capture mode.
- `pcxhr_ids[]` and `pcxhr_board_params[]` map PLX/Digigram device IDs to board names, playback/capture chip counts, firmware sets, and DSP firmware numbers.
- `pcxhr_set_clock()` is the exported clock programming path. It selects generic PCXHR or HR222 clock handling, then sends `CMD_MODIFY_CLOCK` when the hardware control register changed.
- `pcxhr_get_external_clock()` dispatches external clock detection to generic PCXHR or HR222 implementations.
- PCM operations are `pcxhr_open()`, `pcxhr_close()`, `pcxhr_hw_params()`, `pcxhr_prepare()`, `pcxhr_trigger()`, and `pcxhr_stream_pointer()`.
- `pcxhr_create_pcm()` creates ALSA PCM devices and managed DMA buffers.
- `pcxhr_probe()` and `pcxhr_remove()` implement PCI lifecycle through `module_pci_driver()`.

## Control Flow

Probe checks the module enable slot, enables the PCI device, restricts DMA to 32-bit bus-mastering, allocates `pcxhr_mgr`, derives board feature flags, requests PCI regions and a shared threaded IRQ, initializes mutexes and a reusable RMH buffer, then creates ALSA cards for each logical chip. It registers basic proc entries early, allocates the hostport purge DMA buffer, and calls `pcxhr_setup_firmware()`. Firmware setup later creates PCM and mixer devices and re-registers the cards after DSP initialization.

PCM open chooses the `pcxhr_stream` object from playback or capture arrays, applies hardware constraints, rejects already-open streams, disables float format on HR stereo boards, locks the sample rate when another stream or external clock already owns it, sets sync-start behavior, and increments `ref_count_rate`. `hw_params` stores channel count and format. `prepare` programs the card clock once for the first stream and starts the DSP timer. `trigger` either starts a single stream immediately or schedules all linked streams and calls `pcxhr_start_linked_stream()` for synchronized pipe start. Stop marks scheduled stop and sends stop-stream commands. Close releases the sample-rate lock, stops the hardware timer when the last stream closes, and frees the stream slot.

Linked start first stops affected pipes, restores stream formats and ring-buffer addresses, starts each stream, starts all affected pipes together, then marks streams running under the interrupt lock. Runtime pointers are not read directly from DMA hardware on every call; they use timer-maintained period counters updated from the threaded IRQ.

## State And Persistence

`pcxhr_mgr` is the physical-device state: PCI device, IRQ, ports, mutexes, firmware/DSP flags, board feature flags, clock state, timer state, async error counters, cached control registers, and card pointers. `snd_pcxhr` is per logical card and caches PCM pipes, streams, mixer settings, and AES bits. `pcxhr_stream` carries ALSA substream linkage, format/channels, pipe, status, and timer-derived playback/capture position. There is no persistent on-disk state; firmware is requested from the kernel firmware store at probe time.

## Dependencies And Integration Points

The file integrates with ALSA core, PCM, procfs info, PCI, DMA mapping, request-threaded-IRQ, and the rest of the PCXHR driver through `pcxhr_core.h`, `pcxhr_hwdep.h`, `pcxhr_mixer.h`, and `pcxhr_mix22.h`. All hardware programming below stream setup is expressed as `pcxhr_rmh` DSP commands sent through `pcxhr_send_msg()`.

## Risks

- Sample-rate ownership is global per manager; bugs in `ref_count_rate` or close error paths can leave the card stuck at a rate or stop the DSP timer while streams remain active.
- Stream state transitions are strict; unexpected status values cause `-EINVAL` and can leave pipes stopped or stream state inconsistent.
- Linked start intentionally stops and restarts pipes, so failures midway can leave streams scheduled or started but pipes not running.
- Probe registers cards before and after firmware setup; error paths must free all partially created cards and hardware resources.
- Continuous rates use PLL programming and may return a real rate different from the requested rate; userspace and diagnostics must treat `sample_rate_real` separately.

## Test Signals

Test matrix should include all board families where possible, mono and stereo capture module parameters, simultaneous playback/capture, linked sync-start groups, open/close reference-count churn, external clock selection with and without lock, suspend-like remove paths, proc `info/sync/gpio/ltc`, and xrun/error counter visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr.h -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr.h

## Purpose

This is the main shared header for the PCXHR driver. It defines driver version constants, stream/pipe/card limits, clock-type enums, the manager/card/stream/pipe state structures, and the top-level exported functions used across implementation files.

## Important APIs, Types, And Functions

- `enum pcxhr_clock_type` defines generic PCXHR clock sources and HR22 aliases.
- `struct pcxhr_mgr` models a physical PCI board and owns shared device state such as ports, IRQ, mutexes, firmware status, board capability flags, clock/timer values, async error counters, cached Xilinx/DSP register copies, and logical card pointers.
- `enum pcxhr_stream_status` and `struct pcxhr_stream` describe PCM stream lifecycle and timer-derived pointer accounting.
- `struct pcxhr_pipe` tracks DSP pipe definition, direction, and first audio index.
- `struct snd_pcxhr` models one logical ALSA card and stores PCM devices, pipes, streams, mixer cache, mic/phantom state, and IEC958 bits.
- Export declarations include `pcxhr_create_pcm()`, `pcxhr_set_clock()`, and `pcxhr_get_external_clock()`.

## Control Flow

The header does not execute code, but its structures define the control-flow contracts used by the rest of the module. `pcxhr.c` owns most `pcxhr_stream_status` transitions, `pcxhr_hwdep.c` defines pipes and firmware state, `pcxhr_core.c` updates timer/async state, and `pcxhr_mixer.c`/`pcxhr_mix22.c` update mixer caches and board-specific register copies.

## State And Persistence

All significant runtime state is declared here. Locks are split by purpose: `lock` protects interrupt/timer stream state, `msg_lock` serializes DSP command transport, `setup_mutex` coordinates open/close/hw_params/clock setup, and `mixer_mutex` protects ALSA control caches. The state is memory-only and rebuilt on probe.

## Dependencies And Integration Points

The header depends on Linux interrupt/mutex types and ALSA PCM types. It is included by all PCXHR implementation files, so changes here affect module-wide ABI between objects.

## Risks

- Bit-field capability flags in `pcxhr_mgr` must match board discovery and board-parameter logic.
- Array dimensions (`PCXHR_MAX_CARDS`, `PCXHR_PLAYBACK_STREAMS`, two capture streams) are assumed in loops across multiple files.
- Stream status enum changes require synchronized updates in trigger, close, IRQ timer update, and DSP start/stop paths.
- The manager lock split must be preserved to avoid sleeping in interrupt-sensitive sections or racing DSP command traffic.

## Test Signals

Compilation is the first signal for structural changes. Runtime validation should stress multi-card boards, stream state transitions, mixer control state, and interrupt pointer accounting because all of those rely on structures declared here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_core.c -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_core.c

## Purpose

This file is the low-level hardware transport for PCXHR cards. It owns PLX and DSP register access, Xilinx and DSP firmware loading primitives, RMH DSP command serialization, pipe start/stop sequencing, register-control caching, interrupt acknowledgement, asynchronous error decoding, and timer-driven PCM pointer updates.

## Important APIs, Types, And Functions

- Register macros map DSP and PLX mailbox/register offsets to the appropriate I/O BAR.
- `pcxhr_check_reg_bit()` waits for hardware status bits with jiffies-based timeouts.
- `pcxhr_send_it_dsp()` sends host interrupts/commands to the DSP and handles required HF0/HF1/HF5 handshakes.
- Firmware primitives include `pcxhr_reset_xilinx_com()`, `pcxhr_reset_dsp()`, `pcxhr_enable_dsp()`, `pcxhr_load_xilinx_binary()`, `pcxhr_load_eeprom_binary()`, `pcxhr_load_boot_binary()`, and `pcxhr_load_dsp_binary()`.
- `pcxhr_dsp_cmds[]`, `pcxhr_init_rmh()`, `pcxhr_set_pipe_cmd_params()`, and `pcxhr_send_msg()` implement the RMH command protocol.
- `pcxhr_set_pipe_state()` starts/stops playback and capture pipes using can-start, configure, IRQ fire, polling, and stop commands.
- `pcxhr_write_io_num_reg_cont()` serializes and caches writes to the main IO control register.
- `pcxhr_interrupt()` and `pcxhr_threaded_irq()` are the hard and threaded interrupt handlers.

## Control Flow

Firmware load starts with reset and bit-banged Xilinx transfer, then 24-bit DSP boot/eeprom/main-image transfer through HI08-style registers. Main DSP load is followed by higher-level board initialization in `pcxhr_hwdep.c`.

Normal DSP commands go through `pcxhr_send_msg()`, which takes `msg_lock`, sends the message interrupt, waits for `CHK`, resets the semaphore, writes command words, waits for completion, reads fixed/argument/mask-sized status words, and resets the semaphore again. This serialization is required because the DSP mailbox is a single command channel shared by PCM, mixer, firmware, proc, and IRQ-thread paths.

Pipe state changes first compute a combined playback/capture audio mask from requested masks and current MBOX2 state. Starts are prepared with `CMD_CAN_START_PIPE` retries, toggled with `CMD_CONF_PIPE`, committed with `CMD_SEND_IRQA`, then polled until MBOX2 reflects the new state. Stops are toggled and followed by `CMD_STOP_PIPE`.

The hard IRQ confirms the PLX doorbell belongs to this device, clears it, records the source bits, and wakes the threaded handler for timer or message-worthy events. The threaded handler updates stream positions from DSP time MBOX4, handles wrap/resync cases, calls `snd_pcm_period_elapsed()` outside the manager lock when needed, and runs `pcxhr_msg_thread()` to clear frequency/timecode events or decode async xrun reports.

## State And Persistence

The file updates `mgr->dsp_loaded` indirectly through firmware callers, `mgr->io_num_reg_cont`, `timer_toggle`, `dsp_time_last`, `dsp_time_err`, `src_it_dsp`, and async error counters. Stream timer fields are updated here under `mgr->lock`. State is volatile and hardware-derived.

## Dependencies And Integration Points

It depends on low-level Linux I/O port access, firmware structures, PCI devices, ALSA period notification, and shared PCXHR structures. Higher layers depend on this file for every DSP command and for precise PCM pointer progress.

## Risks

- Timeout loops are hardware-sensitive. Too-short waits cause false failures; too-long waits can stall kernel paths.
- `pcxhr_send_msg_nolock()` rejects `cmd_len >= PCXHR_SIZE_MAX_CMD`, so callers must stay inside the command buffer limit.
- The RMH status reader computes variable status length from the first returned word; malformed firmware status can overrun expected protocol and truncate.
- Timer update unlocks and relocks around `snd_pcm_period_elapsed()`, so stream lifetime and status must remain valid across callback re-entry.
- Any direct use of `pcxhr_send_msg_nolock()` must already hold `msg_lock`.
- Interrupt source is stored in a single `src_it_dsp` field; if hardware posts events faster than the thread handles them, source coalescing assumptions matter.

## Test Signals

Validation requires firmware load on real hardware, DSP command timeout/error-path tests, ALSA playback/capture pointer monotonicity, linked stream start/stop, xrun async counter tests, external clock/frequency-change IRQs, and stress tests with mixer writes while PCM streams run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_core.h -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_core.h

## Purpose

This header declares the PCXHR low-level DSP/firmware/interrupt API and the RMH command protocol constants used by PCM, mixer, firmware, and board-specific files.

## Important APIs, Types, And Functions

- Firmware API: `pcxhr_reset_xilinx_com()`, `pcxhr_reset_dsp()`, `pcxhr_enable_dsp()`, and the Xilinx/eeprom/boot/main DSP load functions.
- `struct pcxhr_rmh` is the reusable DSP command/status container with command length, status length/type, command index, and fixed command/status buffers.
- The command enum defines all RMH command IDs, from version/support checks through pipe/stream/format/level/timecode operations.
- `pcxhr_init_rmh()`, `pcxhr_set_pipe_cmd_params()`, and `pcxhr_send_msg()` form the public command construction/sending API.
- IO register numbers, status selectors/results, codec register constants, codec chip-select constants, and pipe-control helpers are shared with the rest of the driver.
- IRQ entry points `pcxhr_interrupt()` and `pcxhr_threaded_irq()` are declared for PCI registration.

## Control Flow

Callers initialize an RMH with one enum command, OR in command-specific selectors, optionally append command words, then send with `pcxhr_send_msg()`. Pipe commands use `pcxhr_set_pipe_cmd_params()` to encode capture/playback, first-audio, stream index, and masks into the command word layout.

## State And Persistence

The header itself stores no state. It defines constants that determine the shape of mailbox commands and therefore the interpretation of hardware/DSP state.

## Dependencies And Integration Points

It forward-declares `struct firmware` and `struct pcxhr_mgr` and is included by all implementation files that interact with the DSP command layer. It also exposes codec constants used by mixer and source-selection logic.

## Risks

- Command enum order must stay synchronized with `pcxhr_dsp_cmds[]` in `pcxhr_core.c`.
- `PCXHR_SIZE_MAX_CMD`, status sizes, and mask constants define fixed buffer boundaries used by the RMH transport.
- Codec and register constants are raw hardware protocol values; accidental changes break board programming without compile-time symptoms.

## Test Signals

Compile-time coverage catches missing declarations, but real validation is command-level: firmware load, pipe allocation, stream format, mixer level, IEC958, and timecode commands must all complete with expected status lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_hwdep.c -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_hwdep.c

## Purpose

This file manages PCXHR firmware loading and the post-firmware hardware setup sequence. Despite the historical "hwdep" name, it uses the kernel firmware API directly, loads the Xilinx/DSP images, validates DSP capabilities, initializes board options, allocates DSP pipes, creates PCM/mixer devices after firmware is ready, and starts the pipes.

## Important APIs, Types, And Functions

- `pcxhr_setup_firmware()` selects a firmware filename set from `mgr->fw_file_set`, requests each image, and calls `pcxhr_dsp_load()`.
- `pcxhr_dsp_load()` dispatches firmware stages by index: internal Xilinx, communication Xilinx, DSP eeprom, DSP boot, and DSP main.
- `pcxhr_init_board()` enables DSP interrupts, verifies supported physical I/O and stream counts with `CMD_SUPPORTED`, sends `CMD_VERSION`, stores DSP version, and delegates board-specific initialization.
- `pcxhr_sub_init()` handles generic PCXHR option detection and input/output unmute.
- `pcxhr_dsp_allocate_pipe()`, `pcxhr_config_pipes()`, and `pcxhr_start_pipes()` define and start DSP playback/capture pipes.
- `pcxhr_reset_board()` mutes and resets hardware during removal or failure cleanup.

## Control Flow

Probe calls `pcxhr_setup_firmware()`. For each required image, the file requests `pcxhr/<name>` firmware, loads it through the lower-level routines in `pcxhr_core.c`, releases it, and records the loaded bit. The final DSP image triggers board initialization: enable interrupts, query DSP capabilities, send driver/DSP version and granularity, run generic or HR222 sub-init, allocate all playback/capture pipes, create PCM devices for each logical chip, create the mixer once through chip 0, register cards, and start all pipes.

## State And Persistence

The file advances `mgr->dsp_loaded`, fills `mgr->dsp_version`, discovers `board_has_analog`, defines pipe status and stream-to-pipe links in each `snd_pcxhr`, and relies on `mgr->hostport` DMA allocated by probe. Firmware files are persistent external dependencies, but the driver stores only loaded-stage bits.

## Dependencies And Integration Points

It depends on firmware filenames matching installed kernel firmware blobs, on `pcxhr_core.c` for binary transfer and RMH commands, on `pcxhr_mix22.c` for HR stereo initialization, on `pcxhr_create_pcm()` from `pcxhr.c`, and on `pcxhr_create_mixer()` from `pcxhr_mixer.c`.

## Risks

- Missing firmware aborts probe with `-ENOENT`.
- The final firmware stage has many side effects after DSP load; failures during PCM/mixer/card registration need complete cleanup through the manager.
- `pcxhr_dsp_allocate_pipe()` assumes audio pin numbering from card index and mono/stereo capture mode; mismatches break channel routing.
- Generic unmute behavior is inverted for some registers: comments note writes/read differences for mute state, so changes need hardware validation.
- `sprintf(path, "pcxhr/%s", ...)` relies on firmware names fitting the fixed 32-byte buffer.

## Test Signals

Test every firmware set used by board parameters, missing-firmware failure paths, DSP capability rejection, mono-capture pipe allocation, card registration after firmware load, mixer creation, pipe start, and cleanup/reset after partial firmware load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_hwdep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_hwdep.h -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_hwdep.h

## Purpose

This small header defines firmware stage indices for the PCXHR load sequence and declares the firmware setup/reset functions shared with the main and core driver files.

## Important APIs, Types, And Functions

- `PCXHR_FIRMWARE_XLX_INT_INDEX`, `PCXHR_FIRMWARE_XLX_COM_INDEX`, `PCXHR_FIRMWARE_DSP_EPRM_INDEX`, `PCXHR_FIRMWARE_DSP_BOOT_INDEX`, and `PCXHR_FIRMWARE_DSP_MAIN_INDEX` enumerate the five possible firmware stages.
- `PCXHR_FIRMWARE_FILES_MAX_INDEX` documents the firmware-stage count.
- `pcxhr_setup_firmware()` loads and initializes firmware.
- `pcxhr_reset_board()` resets/mutes loaded hardware during cleanup.

## Control Flow

The indices drive the ordered firmware loop in `pcxhr_setup_firmware()` and the stage switch in `pcxhr_dsp_load()`. The reset function is called from the manager free path if any firmware stage was loaded.

## State And Persistence

No state is stored here, but the constants define the bit positions used in `mgr->dsp_loaded`.

## Dependencies And Integration Points

This header is consumed by `pcxhr.c`, `pcxhr_core.c`, and `pcxhr_hwdep.c`. Its stage indices must match the firmware filename arrays and load dispatch logic.

## Risks

Changing index values without updating firmware arrays, loaded-bit tests, and reset logic would break staged loading and cleanup. The header name may suggest an ALSA hwdep device, but current code uses direct firmware loading.

## Test Signals

Compile and firmware-load tests verify declarations and indices. Cleanup after failures at each firmware stage is the key runtime signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_hwdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mix22.c -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mix22.c

## Purpose

This file implements board-specific support for HR222/PCXHR stereo cards. It programs Xilinx and AKM codec registers directly through I/O ports, handles HR222 clocking and external clock measurement, controls GPIO/GPO and timecode bits, implements analog level programming, source routing, IEC958 bit access, microphone boost, and phantom-power ALSA controls.

## Important APIs, Types, And Functions

- `hr222_sub_init()` initializes stereo-card analog capabilities, detects mic support, resets codec logic, configures AKM, and initializes mic boost.
- `hr222_sub_set_clock()` programs internal PLL or AES clock routing and codec speed.
- `hr222_get_external_clock()` measures AES clock presence and rate through Xilinx registers.
- `hr222_read_gpio()`, `hr222_write_gpo()`, and `hr222_manage_timecode()` expose stereo-card GPIO/timecode controls to proc code.
- `hr222_update_analog_audio_level()` maps cached ALSA mixer values to playback/capture hardware levels.
- `hr222_set_audio_source()` routes line, digital, SRC, mic, or line+mic capture sources.
- `hr222_iec958_capture_byte()` and `hr222_iec958_update_byte()` read/write AES channel-status bits through Xilinx UER registers.
- `hr222_add_mic_controls()` adds Mic Capture Volume, MicBoost Capture Volume, and Phantom Power controls when the board reports mic support.

## Control Flow

After main DSP firmware load, `pcxhr_init_board()` calls `hr222_sub_init()` for single-playback-chip stereo boards. Clock changes from `pcxhr_set_clock()` call `hr222_sub_set_clock()`, which mutes AKM, optionally programs PLL registers, updates Xilinx clock-select bits, updates codec speed mode, stores real sample rate/current clock, marks the clock changed, and unmutes.

Mixer callbacks in `pcxhr_mixer.c` call HR222-specific functions when `mgr->is_hr_stereo` is set. Analog capture level updates always program line-left, line-right, and mic in one 32-bit transfer so line and mic mute/active state stays coherent. Source selection rewrites `mgr->xlx_cfg`, enabling digital/SRC bits or analog line/mic activity and then writes `PCXHR_XLX_CFG`.

## State And Persistence

Stereo-card state is cached in `pcxhr_mgr`: `xlx_cfg`, `xlx_selmic`, `dsp_reset`, `codec_speed`, `board_has_mic`, `board_has_aes1`, `sample_rate_real`, and `last_reg_stat`. Per-card mixer caches in `snd_pcxhr` determine active analog/mic/phantom state. There is no persistent storage beyond hardware registers and memory caches.

## Dependencies And Integration Points

The file depends on raw I/O byte accesses to DSP/Xilinx BAR 2, ALSA control/TLV APIs, shared PCXHR state, and mixer/core register definitions. It is linked into the PCXHR module through the Makefile and called by `pcxhr.c`, `pcxhr_hwdep.c`, and `pcxhr_mixer.c`.

## Risks

- Direct byte I/O sequences to AKM/Xilinx registers are timing/order-sensitive and not protected internally; callers rely on higher-level mixer/setup locking.
- `hr222_sub_set_clock()` sets `*changed = 1` unconditionally, so higher-level code always sends `CMD_MODIFY_CLOCK`.
- Source-selection logic resets `analog_capture_active` and `mic_active` before checking whether an update is needed, making `update_lvl` conditions subtle.
- External clock measurement relies on delays and cached `last_reg_stat`; noisy or rapidly changing clocks may report stale or rounded rates.
- Phantom power and mic boost are hardware-affecting controls and must be exposed only when mic capability is detected.

## Test Signals

Validate HR222 boot initialization, clock switching among internal/AES sources, external clock measurements at common rates, GPI/GPO proc read/write, LTC enable, line/digital/SRC/mic source selection, analog level/mute behavior, IEC958 bit round-trips, and mic boost/phantom controls on mic-capable boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mix22.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mix22.h -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mix22.h

## Purpose

This header declares the HR222/stereo-card helper API and mixer level constants used by the generic PCXHR files when `mgr->is_hr_stereo` is true.

## Important APIs, Types, And Functions

- Initialization and clocking: `hr222_sub_init()`, `hr222_sub_set_clock()`, and `hr222_get_external_clock()`.
- Proc/hardware helpers: `hr222_read_gpio()`, `hr222_write_gpo()`, and `hr222_manage_timecode()`.
- Mixer helpers: `hr222_update_analog_audio_level()`, `hr222_set_audio_source()`, `hr222_iec958_capture_byte()`, `hr222_iec958_update_byte()`, and `hr222_add_mic_controls()`.
- Constants define playback, line-capture, and microphone capture level ranges for HR222 boards.

## Control Flow

Generic code dispatches to these functions for stereo-card special cases: board initialization from firmware setup, clock operations from `pcxhr_set_clock()`, mixer updates from `pcxhr_mixer.c`, and proc GPIO/LTC paths from `pcxhr.c`.

## State And Persistence

The header stores no state. It defines the valid mixer level ranges that gate ALSA control writes and hardware programming.

## Dependencies And Integration Points

It forward-declares `struct pcxhr_mgr` but relies on including code already knowing `enum pcxhr_clock_type` and `struct snd_pcxhr` through `pcxhr.h`. It is the coupling point between generic PCXHR logic and HR222-specific hardware programming.

## Risks

Range constants must match both ALSA TLV descriptions and the hardware conversion code in `pcxhr_mix22.c`. Signature changes require updates in main, hwdep, and mixer files.

## Test Signals

Compile all PCXHR objects and run stereo-board mixer/clock tests. Boundary writes at min/zero/max levels are especially useful because this header defines accepted ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mix22.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mixer.c

## Purpose

This file implements ALSA mixer controls for PCXHR boards. It creates analog and digital volume controls, playback switches, capture source selection, monitoring controls, clock mode/rate controls, IEC958 controls, and HR222 mic controls when applicable. It bridges ALSA control state to DSP RMH commands or HR222-specific register programming.

## Important APIs, Types, And Functions

- `pcxhr_create_mixer()` is the exported mixer setup entry.
- Analog controls use `pcxhr_analog_vol_*()` and `pcxhr_audio_sw_*()`, with HR222 dispatch where required.
- Digital PCM playback/capture controls use `pcxhr_pcm_vol_*()`, `pcxhr_pcm_sw_*()`, `pcxhr_update_playback_stream_level()`, and `pcxhr_update_audio_pipe_level()`.
- Monitoring controls use `pcxhr_monitor_vol_*()` and `pcxhr_monitor_sw_*()`.
- Capture routing uses `pcxhr_audio_src_*()` and generic `pcxhr_set_audio_source()` or HR222 `hr222_set_audio_source()`.
- Clock controls use `pcxhr_clock_type_*()` and `pcxhr_clock_rate_*()`.
- IEC958 controls use `pcxhr_iec958_*()` and HR222-specific IEC958 helpers when needed.
- `pcxhr_init_audio_levels()` seeds runtime mixer caches and writes initial hardware values where required.

## Control Flow

`pcxhr_create_mixer()` initializes `mixer_mutex`, iterates logical chips, and conditionally adds controls based on playback/capture availability. Playback cards get analog master volume/switch, per-stream PCM volume/switch, and playback IEC958 controls. Capture cards get line capture volume, PCM capture volume, capture source, and capture IEC958 controls. Cards with both directions get monitoring volume/switch. Chip 0 gets manager-wide clock controls. HR stereo capture cards may get mic controls from `hr222_add_mic_controls()`.

Each ALSA `put` callback validates the requested value, updates the cached field in `snd_pcxhr` or `pcxhr_mgr` under `mixer_mutex`, and sends the appropriate hardware command. Generic boards send RMH commands for analog levels, digital stream levels, monitor levels, source routing, SRC programming, IEC958 bit writes, and clock changes. HR stereo boards call `pcxhr_mix22.c` helpers for analog/mic/source/IEC958 details.

## State And Persistence

Mixer state is cached in `struct snd_pcxhr`: analog playback active/volume, analog capture active/volume, digital playback active/volume, digital capture volume, monitoring active/volume, capture source, mic volume/boost/active, phantom power, and AES status bytes. Manager-wide mixer state includes selected and current clock type/rate. State is memory-only and reinitialized at mixer creation.

## Dependencies And Integration Points

This file depends on ALSA control/TLV APIs, shared PCXHR structures, RMH command definitions from `pcxhr_core.h`, firmware availability from `pcxhr_hwdep.h`, and HR222 helpers. It is called after firmware and pipe setup so hardware commands are expected to succeed.

## Risks

- Many controls ignore out-of-range per-channel values by continuing instead of returning `-EINVAL`, so userspace may see partial updates.
- Clock mode changes nest `mixer_mutex` and `setup_mutex` and can send DSP clock commands; lock ordering must remain consistent with PCM open/prepare paths.
- Capture source enumeration size depends on `board_has_aes1` and `board_has_mic`; incorrect board flags expose invalid controls or hide valid ones.
- IEC958 write loops update one bit at a time through DSP commands; partial failures can leave cache and hardware inconsistent because some helper return values are ignored by callers.
- `pcxhr_init_audio_levels()` has extra hardware initialization under `CONFIG_SND_DEBUG`, so debug and non-debug builds differ in initial analog writes for generic boards.

## Test Signals

Use `amixer`/ALSA control tests to enumerate controls per board type, write min/max/out-of-range values, verify playback/capture/monitor levels on running streams, switch clock sources with active/inactive streams, read external clock rates, change IEC958 playback bits, read capture IEC958 bits, and verify HR222-specific mic controls only appear on mic boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mixer.h -->
# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mixer.h

## Purpose

This header exposes the mixer creation entry point for the PCXHR driver.

## Important APIs, Types, And Functions

- `pcxhr_create_mixer(struct pcxhr_mgr *mgr)` creates ALSA controls for every logical card managed by the physical PCI board.

## Control Flow

Firmware setup calls `pcxhr_create_mixer()` after DSP firmware has loaded, board options have been detected, pipes have been allocated, and PCM devices have been created. The mixer implementation then adds controls based on `mgr` and per-card capabilities.

## State And Persistence

No state is stored in the header. The function it declares initializes and populates in-memory mixer state in `pcxhr_mgr` and `snd_pcxhr`.

## Dependencies And Integration Points

It is included by `pcxhr.c`, `pcxhr_core.c`, `pcxhr_hwdep.c`, and `pcxhr_mixer.c`. The declaration keeps mixer setup independent from the main probe and firmware setup files.

## Risks

Because the header exposes only one entry point, all feature gating and error handling are inside `pcxhr_mixer.c`. Callers must invoke it only after firmware is ready to accept DSP commands.

## Test Signals

Compilation verifies the declaration; runtime probe should show expected mixer controls after firmware load and no mixer creation before the DSP command path is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mixer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/riptide/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/riptide/Makefile

## Purpose

This Makefile builds the ALSA Riptide PCI driver as the composite `snd-riptide` module when enabled in kernel configuration.

## Important APIs, Types, And Functions

- `snd-riptide-y := riptide.o` declares the single object that forms the composite module.
- `obj-$(CONFIG_SND_RIPTIDE) += snd-riptide.o` integrates the module with Kbuild and the `CONFIG_SND_RIPTIDE` option.

## Control Flow

Kbuild compiles `riptide.o` and links it into `snd-riptide.o` only when the config symbol is enabled. Runtime control flow is in `riptide.c`, not in this file.

## State And Persistence

The file has no runtime state. Its persistent effect is build inclusion of the Riptide driver.

## Dependencies And Integration Points

It depends on Linux Kbuild syntax and the surrounding ALSA PCI sound Makefile hierarchy. The SPDX line marks the build metadata as GPL-2.0-only.

## Risks

Because there is only one object, any future split of the Riptide driver must update `snd-riptide-y`; otherwise new code will not link. A mismatched config symbol would silently omit or incorrectly include the module.

## Test Signals

Build with `CONFIG_SND_RIPTIDE=m` and verify `snd-riptide.ko` links. Build with the option disabled and verify no Riptide module is produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/riptide/Makefile -->
