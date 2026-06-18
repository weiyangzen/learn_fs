# subset-b-006393 ALSA PCI Echoaudio and EMU10K1 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_dsp.c

## Purpose

`echoaudio_dsp.c` is the shared low-level DSP runtime for the Echoaudio ALSA PCI drivers. It implements the DSP mailbox protocol, firmware and ASIC loading, comm-page initialization, mixer state restoration, transport start/stop, interrupt acknowledgement, pipe allocation, and scatter-gather list construction. Card-specific files include this C file after defining family and feature macros, so most functions are `static` but become part of each card module.

## Important APIs, Types, and Functions

The key DSP primitives are `wait_handshake()`, `send_vector()`, `write_dsp()`, and `read_dsp()`, which synchronize register and comm-page access through `CHI32_*` registers and DSP vector commands. Firmware loading is handled by `load_dsp()`, optional `install_resident_loader()` for 56361 DSPs, `load_asic_generic()`, `read_sn()`, and `load_firmware()`. Runtime state restoration uses `restore_dsp_settings()`, `init_dsp_comm_page()`, and `init_line_levels()`. Mixer helpers include `set_output_gain()`, optional `set_monitor_gain()`, `set_nominal_level()`, `update_output_line_level()`, `update_input_line_level()`, `set_meters_on()`, and `get_audio_meters()`. Audio pipe helpers include `set_audio_format()`, `start_transport()`, `pause_transport()`, `stop_transport()`, `allocate_pipes()`, `free_pipes()`, `sglist_init()`, `sglist_add_mapping()`, `sglist_add_irq()`, and `sglist_wrap()`.

## Control Flow

Initialization starts by clearing and validating the DSP comm page, setting `comm_size`, initial handshake, MIDI FIFO free count, default sample rate, and muted monitor/vmixer arrays. `load_firmware()` checks an already loaded DSP/ASIC first; otherwise it requests card firmware, resets the DSP, writes loader blocks, sends the comm-page physical address, reads the serial-number words required by the DSP boot sequence, and then calls the card-specific `load_asic()`. After firmware is live, `init_line_levels()` initializes saved software state to muted/internal-clock defaults and calls `restore_dsp_settings()`, which pushes all persisted mixer, vmixer, monitor, input-gain, rate, digital, clock, and flag settings into the comm page and sends the appropriate vector commands.

PCM operation allocates pipe bits, writes DMA counter locations, fills SG entries into a per-pipe page, writes DSP audio-format codes, and starts or stops transfers with `DSP_VC_START_TRANSFER` and `DSP_VC_STOP_TRANSFER`. IRQ service checks `CHI32_STATUS_IRQ`, optionally drains MIDI data through `midi_service_irq()`, clears the MIDI count, and acknowledges with `DSP_VC_ACK_INT`.

## State and Persistence Behavior

Persistent driver state lives in `struct echoaudio`, arrays such as `output_gain`, `input_gain`, `monitor_gain`, `vmixer_gain`, flags like `bad_board`, `asic_loaded`, `dsp_code`, `active_mask`, `pipe_alloc_mask`, and the DMA-visible `struct comm_page`. DSP-visible state must be little-endian and is synchronized by handshakes. `bad_board` is set during failed or in-progress DSP loads to prevent pipe allocation. Mixer and clock settings are retained in software and replayed after DSP reloads, suspend/resume-style reinitialization, or ASIC mode changes.

## Dependencies and Integration Points

This file depends on `echoaudio.h`, constants from `echoaudio_dsp.h`, Linux firmware loading, delay/reschedule helpers, DMA addresses, and ALSA PCM/MIDI users in `echoaudio.c` and `midi.c`. It calls card-specific static functions defined before inclusion, such as `load_asic()`, `set_sample_rate()`, `set_input_clock()`, `set_input_gain()`, `set_vmixer_gain()`, and digital-mode helpers.

## Risks and Test Signals

The highest risks are handshake timeouts, endian or layout mistakes in `struct comm_page`, invalid firmware block parsing, sleeping while spinlocks are held in card-specific ASIC paths, and stale pipe masks after transport failure. Useful signals are successful firmware request and probe, no "Invalid struct comm_page" or DSP timeout messages, ALSA PCM open/start/stop on every exposed pipe, meter updates, MIDI IRQ handling where present, and module builds for each macro combination.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_dsp.h -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_dsp.h

## Purpose

`echoaudio_dsp.h` defines the DSP ABI shared by all Echoaudio PCI card personalities. It contains family selection, DSP register offsets, vector command values, clock and digital-mode bit definitions, audio-format encodings, timeout constants, SG entry layout, and the packed DSP communication page layout.

## Important APIs, Types, and Functions

Important definitions include family gates `ECHOGALS_FAMILY`, `ECHO24_FAMILY`, `ECHO3G_FAMILY`, and `INDIGO_FAMILY`; register offsets `CHI32_CONTROL_REG`, `CHI32_STATUS_REG`, `CHI32_VECTOR_REG`, and `CHI32_DATA_REG`; status bits such as `CHI32_STATUS_HOST_READ_FULL`, `CHI32_STATUS_HOST_WRITE_EMPTY`, `CHI32_STATUS_IRQ`, and host flags HF3/HF4/HF5; vector commands such as `DSP_VC_RESET`, `DSP_VC_START_TRANSFER`, `DSP_VC_STOP_TRANSFER`, `DSP_VC_WRITE_CONTROL_REG`, `DSP_VC_UPDATE_FLAGS`, and `DSP_VC_SET_VMIXER_GAIN`; and clock constants for GLDM, GML, E3G, Mia, Layla24, and Indigo Express hardware. `struct sg_entry` and `struct comm_page` are the central DMA-visible types.

## Control Flow

The header is consumed through compile-time inclusion. Each card wrapper defines a family and feature macros before including common source files; this header then selects DSP type, read timeout, command values, and hardware constants. Runtime code fills `struct comm_page`, sends vector commands, and expects the DSP firmware to read fixed offsets documented in the struct comments.

## State and Persistence Behavior

`struct comm_page` is persistent shared state between host and DSP. It stores flags, sample rate, handshake, start/stop/reset masks, per-pipe audio formats, SG-list physical addresses, DMA positions, meters, line levels, monitor matrix, MIDI buffers, clock/status fields, control registers, and vmixer levels. The layout is an ABI and must not drift; `echoaudio_dsp.c` checks the MIDI output offset at runtime.

## Dependencies and Integration Points

The header is included indirectly by card modules through `echoaudio.h` and is tightly coupled to firmware binaries under `ea/*.fw`. It also aligns with ALSA capabilities exposed by each card wrapper, because PCM formats and rates must map to supported DSP audio-format and clock constants.

## Risks and Test Signals

Changing constants or struct layout can break firmware communication even when the kernel still builds. Test signals include `offsetof(struct comm_page, midi_output) == 0xbe0`, successful DSP command handshakes, correct clock detection bits reported in ALSA controls, working SG DMA, and build coverage for Echogals, Echo24, 3G, and Indigo families.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_dsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_gml.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_gml.c

## Purpose

`echoaudio_gml.c` provides common control-register and digital-I/O helpers for Gina24, Mona, and Layla24 class cards. These cards share GML clock, S/PDIF, ADAT, and auto-mute register semantics while differing in ASIC selection and clock-source details.

## Important APIs, Types, and Functions

`check_asic_status()` sends `DSP_VC_TEST_ASIC` and reads the ASIC-loaded response. `write_control_reg()` applies `GML_DIGITAL_IN_AUTO_MUTE`, writes `comm_page->control_register`, clears the handshake, and sends `DSP_VC_WRITE_CONTROL_REG`. `set_input_auto_mute()` updates `chip->digital_in_automute` by reapplying the current input clock. `set_digital_mode()` validates closed pipes and supported mode bits, delegates to card-specific `dsp_set_digital_mode()`, and refreshes monitor/input/output levels when ADAT bus topology changes. `set_professional_spdif()` rebuilds the S/PDIF status bits based on professional/consumer mode and sample rate.

## Control Flow

Card-specific DSP files call `write_control_reg()` for rate, clock, and digital-mode changes. User-facing control changes enter `set_digital_mode()` or `set_input_auto_mute()`, which protect mode changes from active pipes and then republish levels that the DSP may reinterpret when switching ADAT versus S/PDIF routing.

## State and Persistence Behavior

The file persists digital auto-mute, professional S/PDIF, and digital mode in `struct echoaudio` and the comm-page control register. It relies on the card-specific restore path to replay these settings after firmware reload. ADAT transitions may alter logical bus availability, so cached monitor and gain matrices are written back to the DSP.

## Dependencies and Integration Points

It depends on GML constants from `echoaudio_dsp.h`, card-specific `set_input_clock()`, `dsp_set_digital_mode()`, and optional `set_input_gain()`. It is included only by GML card wrappers after their card-specific DSP file and before `echoaudio.c`.

## Risks and Test Signals

Risks include changing digital mode while streams are open, stale auto-mute bits, failing to refresh gains after ADAT changes, and card-specific lock ordering around `write_control_reg()`. Test signals are successful mode switching among S/PDIF RCA/optical and ADAT, expected `-EAGAIN` with open pipes, correct clock controls, and no DSP handshake failures.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio_gml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina20.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina20.c

## Purpose

`gina20.c` is the ALSA PCI module personality for the Echo Gina20. It defines the card family, feature macros, bus and pipe topology, firmware table, PCI IDs, PCM hardware limits, and includes the Gina20 DSP implementation plus shared Echoaudio core.

## Important APIs, Types, and Functions

Feature macros select Echogals behavior with monitor, analog input gain, digital I/O, external S/PDIF clock, and no ADAT. Topology exposes 8 analog outputs, 2 digital outputs, 2 analog inputs, and 2 digital inputs. The module declares firmware `ea/gina20_dsp.fw`, PCI ID `1057:1801` with Echo subsystem `0020`, and `pcm_hardware_skel` supporting mmap/interleaved/block-transfer/pause/sync-start PCM, U8/S16/S24_3LE/S32_LE/S32_BE samples, 44.1 and 48 kHz, and up to 2 channels per stream.

## Control Flow

Probe and ALSA object creation come from the included `echoaudio.c`; this file supplies the static data and macros that shape that common code. At compile time it includes `gina20_dsp.c`, `echoaudio_dsp.c`, and `echoaudio.c`, producing one card-specific module.

## State and Persistence Behavior

The file itself holds static firmware, PCI-ID, and PCM capability tables. Runtime state is stored in `struct echoaudio` by included common code, with Gina20-specific defaults supplied by `gina20_dsp.c`.

## Dependencies and Integration Points

Dependencies include Linux PCI/module/firmware APIs, ALSA core/control/TLV/PCM headers, and `echoaudio.h`. Integration points are the kernel PCI driver generated by `echoaudio.c`, ALSA PCM devices, and firmware lookup under `ea/`.

## Risks and Test Signals

Incorrect topology or PCM rates would expose unsupported ALSA formats or route channels incorrectly. Test with module build, PCI probe on subsystem `ECC0:0020`, firmware load, playback/capture at 44.1 and 48 kHz, S/PDIF clock selection, and monitor/input-gain controls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina20_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina20_dsp.c

## Purpose

`gina20_dsp.c` implements Gina20-specific DSP setup, clocking, sample-rate control, analog input gain, and S/PDIF flag handling for the shared Echoaudio runtime.

## Important APIs, Types, and Functions

`init_hw()` validates the Gina20 subdevice, initializes the comm page, sets `FW_GINA20_DSP`, marks the no-ASIC board as loaded, enables internal and S/PDIF clock types, and loads firmware. `set_mixer_defaults()` clears professional S/PDIF and initializes line levels. `detect_input_clocks()` maps GLDM S/PDIF detection to generic clock bits. `load_asic()` is a no-op. `set_sample_rate()` maps 44.1/48 kHz into Gina/Darla clock and S/PDIF state bytes. `set_input_clock()` selects internal or S/PDIF clock. `set_input_gain()` applies the GL20 gain magic offset. `set_professional_spdif()` toggles `DSP_FLAG_PROFESSIONAL_SPDIF` and calls `update_flags()`.

## Control Flow

Common probe calls `init_hw()`, which boots the DSP and clears `bad_board`. Mixer initialization calls `set_mixer_defaults()` and then `init_line_levels()`. Rate and clock controls write Gina/Darla-specific comm-page state and send `DSP_VC_SET_GD_AUDIO_STATE`; S/PDIF format updates send `DSP_VC_UPDATE_FLAGS`.

## State and Persistence Behavior

The file maintains `clock_state`, `spdif_status`, `professional_spdif`, `input_clock`, `sample_rate`, and per-input gain in `struct echoaudio` and mirrors them into `comm_page->gd_clock_state`, `gd_spdif_status`, `gd_resampler_state`, flags, and `line_in_level`.

## Dependencies and Integration Points

It depends on shared DSP helpers, GLDM/GD constants in `echoaudio_dsp.h`, and ALSA controls from `echoaudio.c`. It has no ASIC or digital-mode switch dependency.

## Risks and Test Signals

Risks are stale GD clock/S/PDIF state, invalid unsupported sample rates slipping through, and incorrect 0.5 dB input-gain encoding. Test signals are clean DSP load, selectable internal/S/PDIF clocks, correct rejection of non-44.1/48 rates from the PCM layer, and audible/observable input-gain and S/PDIF professional mode changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina20_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina24.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina24.c

## Purpose

`gina24.c` is the card wrapper for Echo Gina24 devices. It selects Echo24/GML behavior, declares firmware for 56301 and 56361 variants, exposes PCI IDs, and sets PCM capabilities for an 8-output/8-digital-capable interface.

## Important APIs, Types, and Functions

Feature macros enable monitor, ASIC loading, nominal input/output levels, super-interleave, digital I/O, digital input auto-mute, digital mode switching, external clocks, ADAT, and stereo 32-bit big-endian samples. Firmware entries include loader, `gina24_301_dsp.fw`, `gina24_361_dsp.fw`, and matching ASIC images. The PCI table matches both 56301 and 56361 revisions. PCM hardware supports standard 8 to 48 kHz rates plus 88.2/96 kHz, 1 to 8 channels, and the common Echo period/buffer limits.

## Control Flow

The module is assembled by including `gina24_dsp.c`, shared DSP, GML helpers, and common Echoaudio code. The card-specific DSP file chooses firmware and digital modes at runtime based on device ID.

## State and Persistence Behavior

Static state consists of firmware, PCI IDs, and PCM caps. Runtime digital mode, ASIC code, clocks, nominal levels, and mixer state are maintained by included code in `struct echoaudio`.

## Dependencies and Integration Points

It integrates with Linux firmware files under `ea/`, ALSA PCM/control surfaces, common `echoaudio.c`, and `echoaudio_gml.c` for GML register control.

## Risks and Test Signals

Risks include mismatching 301/361 firmware or exposing ADAT/digital mode controls inconsistent with hardware revision. Test signals include probe on all listed PCI IDs, firmware load for both DSP families, sample-rate coverage from 8 to 96 kHz, ADAT versus S/PDIF switching, and nominal level controls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina24_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina24_dsp.c

## Purpose

`gina24_dsp.c` implements Gina24 hardware initialization, ASIC selection, sample-rate programming, input-clock selection, and GML digital-mode handling.

## Important APIs, Types, and Functions

`init_hw()` validates Gina24, initializes the comm page, selects 56301 or 56361 DSP firmware, enables internal/S/PDIF/ESYNC/ESYNC96/ADAT clocks, and sets supported digital modes. `set_mixer_defaults()` initializes S/PDIF RCA, consumer S/PDIF, and digital auto-mute. `detect_input_clocks()` maps GML S/PDIF, ADAT, and ESYNC detect bits. `load_asic()` loads the correct Gina24 ASIC and initializes the GML control register to converter enabled, 48 kHz internal. `set_sample_rate()` maps fixed rates into GML clock bits and forbids double-speed ADAT. `set_input_clock()` selects internal, S/PDIF, ADAT, ESYNC, or ESYNC96. `dsp_set_digital_mode()` handles RCA/optical/CDROM/ADAT and incompatible clock fallback.

## Control Flow

Probe boots firmware and ASIC, then common mixer initialization restores line state. Rate changes only program hardware while using the internal clock; external clock mode records the requested rate for ALSA state. Digital-mode changes may force internal 48 kHz first, then rewrite `control_register`.

## State and Persistence Behavior

Persistent state includes `dsp_code_to_load`, `asic_code`, `digital_modes`, `digital_mode`, `digital_in_automute`, `input_clock`, `sample_rate`, and `comm_page->control_register`. The `device_id` distinguishes 56301-only CDROM S/PDIF mode from 56361 behavior.

## Dependencies and Integration Points

This file depends on `echoaudio_gml.c` for `write_control_reg()`, `set_digital_mode()`, and S/PDIF format handling, plus shared DSP firmware helpers. It is driven by ALSA clock, digital-mode, and PCM rate controls.

## Risks and Test Signals

Risks include allowing ADAT above 48 kHz, failing to clear double-speed bits when switching to ADAT, and incorrect CDROM mode on 56361 hardware. Test signals are ASIC status success, correct external-clock detection, digital-mode fallback to internal clock when needed, and working playback/capture in S/PDIF and ADAT modes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/gina24_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo.c

## Purpose

`indigo.c` is the Echo Indigo playback-card wrapper. It defines an Indigo-family module with virtual mixer support and no physical inputs or digital I/O.

## Important APIs, Types, and Functions

The topology defines 8 playback pipes feeding 2 analog output busses. Feature macros enable super-interleave, vmixer, and stereo 32-bit big-endian support. Firmware entries are `loader_dsp.fw` and `indigo_dsp.fw`; the PCI table matches subsystem `0090`. PCM caps support 32, 44.1, 48, 88.2, and 96 kHz, 1 to 8 channels, and common Echo buffer constraints.

## Control Flow

The file includes `indigo_dsp.c`, shared DSP, and common Echoaudio core. Common probe uses the static tables here and `indigo_dsp.c` supplies internal-only clocking and vmixer behavior.

## State and Persistence Behavior

Runtime state is held by the common Echoaudio structures, especially vmixer gains and output gains. This wrapper contributes fixed firmware, topology, and PCM capability state.

## Dependencies and Integration Points

It depends on the 56361 loader firmware, ALSA PCM/control headers, and `echoaudio.h`. Integration is through common PCI probe and vmixer controls.

## Risks and Test Signals

Risks are exposing nonexistent inputs or more physical output busses than the two analog outputs. Test signals are successful firmware load, playback-only ALSA devices, vmixer routing from 8 virtual pipes to 2 outputs, and rate switching across the advertised rates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo_dsp.c

## Purpose

`indigo_dsp.c` implements the original Indigo card DSP behavior: no ASIC, internal-only clocking, fixed MIA-style sample-rate register values, and vmixer routing.

## Important APIs, Types, and Functions

`init_hw()` validates `INDIGO`, sets `FW_INDIGO_DSP`, marks ASIC loaded, enables only the internal clock, and loads firmware. `set_mixer_defaults()` delegates to `init_line_levels()`. `detect_input_clocks()` returns internal only. `load_asic()` is a no-op. `set_sample_rate()` maps 32/44.1/48/88.2/96 kHz to MIA clock constants and sends `DSP_VC_UPDATE_CLOCKS`. `set_vmixer_gain()` updates `chip->vmixer_gain` and `comm_page->vmixer`; `update_vmixer_level()` sends `DSP_VC_SET_VMIXER_GAIN`.

## Control Flow

After firmware load, common initialization restores muted output and vmixer state. ALSA rate changes rewrite the comm-page control register when the selected clock encoding changes. Mixer controls update individual vmixer cells and then ask the DSP to reread the vmixer table.

## State and Persistence Behavior

State includes `sample_rate`, `control_register`, `input_clock_types`, `vmixer_gain`, and `comm_page->vmixer`. Because there is no ASIC or external clock, reload restore is simpler than GML cards.

## Dependencies and Integration Points

It integrates with shared DSP helpers and common vmixer ALSA controls. It reuses MIA clock constants from `echoaudio_dsp.h` for the Indigo hardware clock register.

## Risks and Test Signals

Risks include unsupported rates and vmixer index mistakes across `output * num_pipes_out + pipe`. Test signals are stable internal-clock detection, successful rate changes, correct 8-pipe to 2-output vmixer controls, and no ASIC load attempts.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo_express_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo_express_dsp.c

## Purpose

`indigo_express_dsp.c` is the shared DSP helper for Indigo Express-derived DJx and IOx cards. It supplies sample-rate programming, vmixer operations, internal clock detection, and no-ASIC behavior, while the small DJx/IOx files supply hardware identity.

## Important APIs, Types, and Functions

`set_sample_rate()` maps 32, 44.1, 48, 64, 88.2, and 96 kHz to `INDIGO_EXPRESS_*` control-register bits, including double-speed encodings. `set_vmixer_gain()` and `update_vmixer_level()` mirror the original Indigo vmixer table update path. `detect_input_clocks()` returns internal only, and `load_asic()` is a no-op.

## Control Flow

DJx/IOx initialization includes this file after defining the card-specific `init_hw()`. Rate changes wait for DSP handshake, mask out `INDIGO_EXPRESS_CLOCK_MASK`, update `comm_page->control_register` when needed, and send `DSP_VC_UPDATE_CLOCKS`. Vmixer changes update one matrix cell and send `DSP_VC_SET_VMIXER_GAIN`.

## State and Persistence Behavior

Persistent state is limited to `sample_rate`, the comm-page control register, and vmixer gain arrays. No external clock or ASIC state is maintained.

## Dependencies and Integration Points

It depends on shared DSP helpers and Indigo Express constants in `echoaudio_dsp.h`. It is included by `indigodjx.c` and `indigoiox.c` after their card-specific DSP identity files.

## Risks and Test Signals

Risks are incorrect double-speed masking, omitting 64 kHz support, and vmixer indexing mistakes. Test signals are successful rate switching including 64/88.2/96 kHz, internal-only clock controls, and working vmixer routing on both DJx and IOx modules.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigo_express_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodj.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodj.c

## Purpose

`indigodj.c` is the card wrapper for Echo Indigo DJ. It is a playback-oriented Indigo-family module with four analog output busses and vmixer support.

## Important APIs, Types, and Functions

The topology defines 8 output pipes and 4 analog output busses, with no inputs. Firmware entries are `loader_dsp.fw` and `indigo_dj_dsp.fw`; the PCI table matches subsystem `00B0`. PCM caps are the same fixed Indigo rates from 32 to 96 kHz, with up to 4 channels.

## Control Flow

The module includes `indigodj_dsp.c`, shared DSP, and common Echoaudio core. Probe and ALSA registration are common; this file supplies compile-time card identity and capability data.

## State and Persistence Behavior

Runtime state is common Echoaudio state, especially vmixer gain and output gain arrays sized by this topology. Static firmware and PCI tables are module-local.

## Dependencies and Integration Points

It integrates with ALSA PCM and mixer controls through `echoaudio.c` and with DSP firmware through `indigodj_dsp.c` and `echoaudio_dsp.c`.

## Risks and Test Signals

Risks are topology mismatches between 8 virtual pipes and 4 output busses, and exposing input controls that should not exist. Test signals include playback on all four analog outputs, vmixer controls, and firmware load for `indigo_dj_dsp.fw`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodj_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodj_dsp.c

## Purpose

`indigodj_dsp.c` provides Indigo DJ-specific DSP initialization and vmixer/sample-rate operations for the four-output DJ card.

## Important APIs, Types, and Functions

The structure mirrors `indigo_dsp.c`: `init_hw()` validates the Indigo DJ subdevice, selects `FW_INDIGO_DJ_DSP`, marks the no-ASIC card as loaded, enables internal-only clocking, and loads firmware. `set_mixer_defaults()`, `detect_input_clocks()`, `load_asic()`, `set_sample_rate()`, `set_vmixer_gain()`, and `update_vmixer_level()` provide defaults, fixed MIA-style rate encodings, and vmixer matrix updates.

## Control Flow

Common initialization calls the card `init_hw()` and then replays line/vmixer defaults. ALSA rate changes write the control register and send `DSP_VC_UPDATE_CLOCKS`; vmixer changes are staged in the comm page and committed with `DSP_VC_SET_VMIXER_GAIN`.

## State and Persistence Behavior

The card persists no external clock or ASIC state. It keeps internal sample-rate state, control-register value, and a vmixer matrix sized by 4 outputs by 8 pipes.

## Dependencies and Integration Points

It depends on shared DSP primitives and constants from `echoaudio_dsp.h`, and it is consumed by the `indigodj.c` wrapper and common `echoaudio.c` mixer controls.

## Risks and Test Signals

Risks are unsupported rate programming and vmixer cell ordering. Test with all advertised rates, four-output playback, vmixer gain persistence after DSP reload, and absence of external clock or input controls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodj_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodjx.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodjx.c

## Purpose

`indigodjx.c` is the card wrapper for the Echo Indigo DJx ExpressCard variant. It combines DJ-style four-output topology with the Indigo Express DSP clock helper.

## Important APIs, Types, and Functions

Feature macros enable Indigo family, super-interleave, vmixer, and stereo 32-bit big-endian samples. The topology has 8 output pipes and 4 analog output busses. Firmware entries are `loader_dsp.fw` and `indigo_djx_dsp.fw`; PCI subsystem is `00E0`. PCM caps include 32, 44.1, 48, 64, 88.2, and 96 kHz with up to 4 channels.

## Control Flow

The inclusion order is `indigodjx_dsp.c`, `indigo_express_dsp.c`, shared DSP, and common Echoaudio core. The first file supplies identity/init; the Express helper supplies sample-rate and vmixer functions.

## State and Persistence Behavior

Static state is firmware/PCI/PCM capability data. Runtime state is common Echoaudio state, especially `sample_rate`, `control_register`, and vmixer gains.

## Dependencies and Integration Points

It depends on ALSA PCI/PCM infrastructure, `echoaudio.h`, and firmware under `ea/`. It integrates with common Echoaudio probe and vmixer controls.

## Risks and Test Signals

Risks are losing the Express-only 64 kHz rate or mixing DJx identity with the older DJ firmware. Test signals are probe on subsystem `00E0`, `indigo_djx_dsp.fw` load, 64 kHz playback, and four-output vmixer operation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodjx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodjx_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodjx_dsp.c

## Purpose

`indigodjx_dsp.c` supplies the Indigo DJx card identity and hardware initialization used with the shared Indigo Express DSP helper.

## Important APIs, Types, and Functions

`init_hw()` validates the DJx subdevice, initializes the comm page, records `device_id` and `subdevice_id`, sets `FW_INDIGO_DJX_DSP`, marks the no-ASIC hardware as loaded, enables internal-only clocking, and loads firmware. `set_mixer_defaults()` delegates to `init_line_levels()`. The file forward-declares vmixer helpers that are implemented by `indigo_express_dsp.c`.

## Control Flow

Probe enters `init_hw()`, which performs the comm-page reset and firmware load before common Echoaudio setup continues. Subsequent rate and vmixer operations are resolved to the shared Express helper included after this file.

## State and Persistence Behavior

It initializes durable fields in `struct echoaudio`: device/subdevice IDs, `bad_board`, `dsp_code_to_load`, `asic_loaded`, and internal clock capabilities. Mixer and rate state are restored by the shared code.

## Dependencies and Integration Points

It depends on `init_dsp_comm_page()` and `load_firmware()` from `echoaudio_dsp.c`, plus `indigo_express_dsp.c` for sample-rate and vmixer implementations.

## Risks and Test Signals

Risks are wrong subdevice validation or firmware index, which would fail probe or load the wrong DSP image. Test with DJx PCI ID probe, clean firmware load, internal-clock-only controls, and Express-rate playback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigodjx_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoio.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoio.c

## Purpose

`indigoio.c` is the wrapper for Echo Indigo IO, an Indigo-family card with stereo analog input, stereo analog output, monitor controls, and vmixer playback.

## Important APIs, Types, and Functions

The topology defines 8 playback pipes, 2 analog input pipes, 2 output busses, and 2 input busses. Feature macros enable monitor, super-interleave, vmixer, and stereo 32-bit big-endian samples. Firmware entries are `loader_dsp.fw` and `indigo_io_dsp.fw`; PCI subsystem is `00A0`. PCM caps advertise 32, 44.1, 48, 88.2, and 96 kHz, up to 8 channels.

## Control Flow

The file includes `indigoio_dsp.c`, shared DSP, and common Echoaudio code. The common layer creates PCM and controls according to the topology and feature macros.

## State and Persistence Behavior

Runtime state includes monitor and vmixer matrices plus line levels, persisted in `struct echoaudio` and replayed by common restore logic. Static state is firmware, PCI, and PCM capability data.

## Dependencies and Integration Points

It integrates with ALSA PCM capture/playback, monitor and vmixer controls, and the Indigo IO DSP firmware.

## Risks and Test Signals

Risks include mismatching input bus counts and monitor matrix dimensions. Test signals include stereo capture, playback, monitor controls, vmixer routing, and fixed-rate switching.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoio_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoio_dsp.c

## Purpose

`indigoio_dsp.c` implements DSP initialization, fixed clocking, sample-rate programming, and vmixer handling for Indigo IO.

## Important APIs, Types, and Functions

`init_hw()` validates `INDIGO_IO`, sets `FW_INDIGO_IO_DSP`, marks no ASIC, enables internal clock only, and loads firmware. `set_mixer_defaults()` restores default levels. `detect_input_clocks()` reports internal only. `load_asic()` is a no-op. `set_sample_rate()` programs the same MIA-style fixed clock encodings as the original Indigo. `set_vmixer_gain()` and `update_vmixer_level()` manage virtual mixer cells.

## Control Flow

After probe and firmware load, common code initializes line, monitor, and vmixer levels. Rate changes wait for a DSP handshake before changing `control_register`, then send `DSP_VC_UPDATE_CLOCKS`.

## State and Persistence Behavior

State includes sample rate, control-register value, vmixer gains, monitor gains from common code, and internal-only clock capabilities. No ASIC or external clock state exists.

## Dependencies and Integration Points

It depends on shared Echoaudio DSP helpers and is selected by the `indigoio.c` wrapper. ALSA monitor and vmixer controls exercise its comm-page writes.

## Risks and Test Signals

Risks are assuming external clock support on a card that reports internal only, and incorrect vmixer dimensions with analog input present. Test stereo capture/playback, monitor loopback, vmixer persistence, and all supported rates.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoio_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoiox.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoiox.c

## Purpose

`indigoiox.c` wraps the Echo Indigo IOx ExpressCard variant. It combines Indigo IO-style stereo input/output topology with Indigo Express rate programming.

## Important APIs, Types, and Functions

The topology has 8 playback pipes, 2 analog input pipes, 2 output busses, and 2 input busses. Feature macros enable monitor, super-interleave, vmixer, and stereo 32-bit big-endian. Firmware entries are `loader_dsp.fw` and `indigo_iox_dsp.fw`; PCI subsystem is `00D0`. PCM caps add 64 kHz to the Indigo IO fixed-rate set.

## Control Flow

The file includes `indigoiox_dsp.c`, `indigo_express_dsp.c`, shared DSP, and common Echoaudio code. Identity/init comes from IOx, while rate/vmixer operations come from the Express helper.

## State and Persistence Behavior

Runtime state is common Echoaudio state sized by this topology. Static state is firmware, PCI IDs, and PCM caps.

## Dependencies and Integration Points

It depends on Express clock constants, ALSA PCM/capture, monitor/vmixer controls, and firmware lookup under `ea/`.

## Risks and Test Signals

Risks include omitting Express 64 kHz support or using the non-Express IO firmware. Test signals are successful IOx probe, stereo capture and playback, 64 kHz operation, and monitor/vmixer controls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoiox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoiox_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoiox_dsp.c

## Purpose

`indigoiox_dsp.c` supplies the Indigo IOx identity and initialization layer used with the shared Indigo Express DSP implementation.

## Important APIs, Types, and Functions

`init_hw()` validates the IOx subdevice, initializes the comm page, stores IDs, sets `FW_INDIGO_IOX_DSP`, marks the no-ASIC card as loaded, enables internal clock only, and loads firmware. `set_mixer_defaults()` initializes line levels. Vmixer function prototypes are resolved by `indigo_express_dsp.c`.

## Control Flow

Probe calls this `init_hw()` before common setup. Once firmware is loaded, common restore calls into the Express helper for sample-rate and vmixer operations.

## State and Persistence Behavior

It initializes the durable card identity, firmware selection, `bad_board`, `asic_loaded`, and clock capability fields. Mixer, monitor, and sample-rate values are held by common Echoaudio state.

## Dependencies and Integration Points

It depends on `echoaudio_dsp.c` for comm-page and firmware loading and on `indigo_express_dsp.c` for operational DSP controls.

## Risks and Test Signals

Risks are wrong firmware index or subdevice mask. Test with IOx PCI ID probe, clean firmware load, internal-only clock detection, stereo capture, and Express-rate playback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/indigoiox_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla20.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla20.c

## Purpose

`layla20.c` is the Echo Layla20 wrapper. It defines an Echogals card with ASIC firmware, MIDI, monitor controls, analog input gain, output nominal levels, external clocks, and output clock switching.

## Important APIs, Types, and Functions

The topology exposes 10 analog outputs, 2 digital outputs, 8 analog inputs, and 2 digital inputs. Firmware entries are `layla20_dsp.fw` and `layla20_asic.fw`; PCI subsystems include revisions `0030` and `0031`. PCM caps support U8/S16/S24_3LE/S32_LE/S32_BE, continuous 8 to 50 kHz rates, up to 10 channels, and standard Echo buffer limits. It includes `midi.c` because `ECHOCARD_HAS_MIDI` is set.

## Control Flow

The module includes `layla20_dsp.c`, shared DSP, common Echoaudio code, and MIDI support. Common probe registers PCM, mixer, and rawmidi interfaces according to these macros.

## State and Persistence Behavior

Static firmware, topology, and PCM caps are local. Runtime ASIC, clock, MIDI, monitor, nominal-level, and gain state is held in `struct echoaudio` and the comm page.

## Dependencies and Integration Points

It integrates with ALSA PCM, controls, and rawmidi; firmware loading for both DSP and ASIC; and external clock/output clock controls.

## Risks and Test Signals

Risks include ASIC firmware failure when the external box is absent, incorrect continuous-rate handling, and MIDI timer/IRQ regressions. Test signals are probe with both revisions, ASIC status success or clear error, 8-channel capture, 10-channel playback, rawmidi I/O, and word/super/S/PDIF clock controls.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla20.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla20_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla20_dsp.c

## Purpose

`layla20_dsp.c` implements Layla20-specific DSP initialization, ASIC loading, external clock control, sample-rate programming, output clock selection, input gain, and S/PDIF flag handling.

## Important APIs, Types, and Functions

`init_hw()` validates Layla20, initializes the comm page, selects `FW_LAYLA20_DSP`, enables internal/S/PDIF/word/super clocks, and loads firmware. `load_asic()` uses `load_asic_generic()` with `FW_LAYLA20_ASIC` and `check_asic_status()`. `detect_input_clocks()` maps GLDM S/PDIF, word, and super-clock bits. `set_sample_rate()` programs Layla sample-rate state. `set_input_clock()` selects internal, S/PDIF, word, or super. `set_output_clock()` switches word versus super clock output. `set_input_gain()`, `update_flags()`, and `set_professional_spdif()` update analog gain and S/PDIF flags.

## Control Flow

Probe boots DSP and ASIC, then default mixer restore writes muted levels and clock defaults. Clock/rate changes use comm-page fields plus `DSP_VC_SET_LAYLA_SAMPLE_RATE` or `DSP_VC_UPDATE_FLAGS`. ASIC status is checked after load and during restore.

## State and Persistence Behavior

State includes `asic_loaded`, `input_clock`, `output_clock`, `sample_rate`, `professional_spdif`, input gains, and output nominal levels. These values are replayed by `restore_dsp_settings()` after reload.

## Dependencies and Integration Points

It depends on shared ASIC and DSP loader helpers, GLDM/Layla clock constants, and optional MIDI shutdown through shared code. ALSA controls for clocks, S/PDIF, gain, and output level reach these functions.

## Risks and Test Signals

Risks include external-box ASIC load failures, wrong output clock mode, and unsupported continuous rates. Test signals are successful ASIC test, valid clock detection, output clock control behavior, MIDI operation, and no DSP handshake timeout during rate/gain changes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla20_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla24.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla24.c

## Purpose

`layla24.c` wraps the Echo Layla24, a full 32-pipe Echo24/GML card with MIDI, ASIC firmware, digital mode switching, ADAT, and nominal level controls.

## Important APIs, Types, and Functions

The topology defines 8 analog outputs, 8 digital outputs, 8 analog inputs, and 8 digital inputs. Firmware entries include loader, `layla24_dsp.fw`, one PCI-card ASIC, and external S/ADAT ASIC images. PCI subsystem is `0060` on DSP 56361. PCM caps support 8 to 96 kHz nominally with `rate_max` 100 kHz for continuous mode, up to 8 channels, and common Echo limits. It includes GML helpers and MIDI support.

## Control Flow

The inclusion chain is `layla24_dsp.c`, shared DSP, GML helpers, common Echoaudio, and MIDI. Card-specific DSP code loads the base ASIC and switches external ASIC images as digital modes change.

## State and Persistence Behavior

Runtime state includes ASIC code, digital mode, digital auto-mute, professional S/PDIF, MIDI state, nominal levels, clocks, and line/mixer settings. Static state is firmware and capability data.

## Dependencies and Integration Points

It integrates with firmware `ea/layla24_*`, ALSA PCM/control/rawmidi, GML register helpers, and common Echoaudio transport.

## Risks and Test Signals

Risks are wrong external ASIC selection, continuous-rate register mistakes, and ADAT/double-speed conflicts. Test with DSP/ASIC load, S/PDIF and ADAT mode switching, continuous rates around 25 to 100 kHz, MIDI I/O, and full 8-channel capture/playback.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla24.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla24_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla24_dsp.c

## Purpose

`layla24_dsp.c` implements Layla24-specific firmware/ASIC handling, GML control-register programming, continuous sample-rate mode, input clocking, and digital-mode ASIC switching.

## Important APIs, Types, and Functions

`init_hw()` validates Layla24, initializes the comm page, enables internal/S/PDIF/word/ADAT clocks, sets supported digital modes, and loads firmware. `load_asic()` loads the PCI-card ASIC and default external S/PDIF ASIC, then writes a 48 kHz internal GML control register. `set_sample_rate()` maps standard rates and uses `LAYLA24_CONTINUOUS_CLOCK` plus `DSP_VC_SET_LAYLA24_FREQUENCY_REG` for nonstandard rates. `set_input_clock()` handles internal, S/PDIF, word, and ADAT. `switch_asic()` swaps external ASIC images while preserving monitor state. `dsp_set_digital_mode()` selects S/PDIF RCA, S/PDIF optical, or ADAT and switches ASICs as needed.

## Control Flow

Initialization loads DSP, base ASIC, and default external ASIC. Rate changes either update fixed clock bits or program the frequency register before writing the GML control register. Digital-mode changes may first force internal 48 kHz, then sleep while switching ASIC firmware, then take the spinlock to update the control register.

## State and Persistence Behavior

Persistent fields include `asic_code`, `digital_mode`, `input_clock`, `sample_rate`, auto-mute/pro S/PDIF state, and monitor matrix. `switch_asic()` temporarily mutes the monitor matrix during firmware load and restores it afterward.

## Dependencies and Integration Points

It depends on `echoaudio_gml.c`, shared DSP loader helpers, Layla24 ASIC firmware files, and ALSA clock/digital-mode controls.

## Risks and Test Signals

Risks include sleeping under the wrong lock, losing monitor levels during ASIC switch, bad continuous-rate divisor math, and invalid double-speed ADAT states. Test signals are ASIC switch success, monitor persistence across S/PDIF/ADAT changes, clock detection, nonstandard rate playback, and no handshake errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/layla24_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/mia.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/mia.c

## Purpose

`mia.c` wraps Echo Mia and Mia MIDI-capable revisions. It defines Echo24 behavior without ASIC, with stereo analog/digital I/O, vmixer, MIDI, nominal levels, and S/PDIF clock support.

## Important APIs, Types, and Functions

The topology has 8 playback pipes, 2 analog input pipes, 2 digital input pipes, 2 analog output busses, 2 digital output busses, and 2 analog plus 2 digital input busses. Firmware entries are loader and `mia_dsp.fw`; PCI subsystems are `0080` and `0081`. PCM caps advertise 32/44.1/48/88.2/96 kHz, up to 8 channels, and common Echo buffer limits. `ECHOCARD_HAS_MIDI` is set but actual MIDI is detected by revision in the DSP file.

## Control Flow

The file includes `mia_dsp.c`, shared DSP, common Echoaudio, and MIDI support. Common code uses card macros to expose PCM, mixer, nominal level, digital clock, vmixer, and rawmidi functionality.

## State and Persistence Behavior

Runtime state includes optional `has_midi`, S/PDIF professional mode, input clock, vmixer matrix, monitor matrix, nominal levels, and line-out gain. Static state is firmware/PCI/PCM capability data.

## Dependencies and Integration Points

It depends on ALSA PCM/rawmidi/control APIs, firmware loading, and common Echoaudio code.

## Risks and Test Signals

Risks are exposing MIDI on non-MIDI revisions, rate mismatch from `rate_min` versus listed rates, and incorrect digital/analog bus mapping. Test with both revisions, MIDI presence only where expected, internal/S/PDIF clocking, vmixer, and stereo analog/digital I/O.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/mia.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/mia_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/mia_dsp.c

## Purpose

`mia_dsp.c` implements Mia-specific initialization, MIDI revision detection, MIA control-register rate/clock programming, vmixer routing, and S/PDIF flag handling.

## Important APIs, Types, and Functions

`init_hw()` validates `MIA`, selects `FW_MIA_DSP`, marks no ASIC, sets `has_midi` for `MIA_MIDI_REV`, enables internal and S/PDIF clocks, and loads firmware. `detect_input_clocks()` maps GLDM S/PDIF detection. `set_sample_rate()` maps fixed rates to MIA constants and ORs S/PDIF clock bits when needed. `set_input_clock()` accepts internal or S/PDIF and reapplies the sample rate. `set_vmixer_gain()` and `update_vmixer_level()` update the virtual mixer. `update_flags()` and `set_professional_spdif()` toggle S/PDIF professional mode.

## Control Flow

Probe initializes hardware and optional MIDI capability. Rate and clock controls converge through `set_sample_rate()`, so changing to S/PDIF clock reprograms the same stored sample rate with the S/PDIF clock bit. S/PDIF format changes send `DSP_VC_UPDATE_FLAGS`.

## State and Persistence Behavior

State includes `has_midi`, `input_clock`, `sample_rate`, `control_register`, `professional_spdif`, and vmixer gains. No ASIC state exists, but DSP reloads restore these fields through common code.

## Dependencies and Integration Points

It depends on shared DSP helpers, MIA constants in `echoaudio_dsp.h`, common Echoaudio controls, and optional `midi.c` rawmidi creation.

## Risks and Test Signals

Risks are wrong MIDI revision detection, unsupported rates, and stale S/PDIF clock bits after input-clock changes. Test signals are MIDI only on revision 1, internal and S/PDIF clock switching, professional S/PDIF control, and vmixer operation.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/mia_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/midi.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/midi.c

## Purpose

`midi.c` implements raw MIDI support for Echoaudio cards that define `ECHOCARD_HAS_MIDI`. It manages DSP MIDI input flags, MIDI output polling, MIDI time-code timestamp filtering, and ALSA rawmidi registration.

## Important APIs, Types, and Functions

`enable_midi_input()` toggles `DSP_FLAG_MIDI_INPUT` and sends `DSP_VC_UPDATE_FLAGS`. `write_midi()` writes a bounded MIDI packet into `comm_page->midi_output` and sends `DSP_VC_MIDI_WRITE` when host flag HF4 says the DSP can accept data. `mtc_process_data()` skips timestamp words inserted after MTC `0xF1`. `midi_service_irq()` copies DSP input bytes into `chip->midi_buffer`. ALSA callbacks are `snd_echo_midi_input_open()`, `snd_echo_midi_input_trigger()`, `snd_echo_midi_input_close()`, `snd_echo_midi_output_open()`, `snd_echo_midi_output_write()`, `snd_echo_midi_output_trigger()`, `snd_echo_midi_output_close()`, and `snd_echo_midi_create()`.

## Control Flow

Input open stores the substream and trigger toggles the DSP MIDI input flag under `chip->lock`. IRQ service reads the comm-page count and filters timestamp words. Output trigger starts a timer; the timer peeks rawmidi bytes, attempts a DSP write, acknowledges sent bytes, and rearms itself based on MIDI wire time if data remains or the DSP FIFO is full.

## State and Persistence Behavior

Persistent state includes `midi_in`, `midi_out`, `rmidi`, `midi_input_enabled`, `midi_full`, `tinuse`, `mtc_state`, a timer, and `midi_buffer`. DSP-visible state lives in comm-page MIDI input/output arrays and `midi_out_free_count`.

## Dependencies and Integration Points

It depends on shared DSP handshake/vector helpers, `struct comm_page`, ALSA rawmidi APIs, timers, and card IRQ service in `echoaudio_dsp.c`.

## Risks and Test Signals

Risks include timer deletion races, writing too many bytes to the DSP MIDI buffer, mishandling MTC timestamp words, and rawmidi callbacks after close. Test signals are duplex rawmidi creation, input byte delivery from IRQ, output progress under FIFO-full conditions, clean trigger start/stop, and no timer use-after-close.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/midi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/mona.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/mona.c

## Purpose

`mona.c` is the wrapper for Echo Mona cards. It selects Echo24/GML behavior with PCI and external ASICs, monitor controls, super-interleave, digital mode switching, external clocks, and ADAT.

## Important APIs, Types, and Functions

The topology exposes 6 analog outputs, 8 digital outputs, 4 analog inputs, and 8 digital inputs. Firmware entries include loader, 56301 and 56361 DSP images, 48/96 kHz PCI-card ASIC images for each DSP family, and an external ASIC. PCI IDs cover 56301 and 56361 revisions `0070` to `0072`. PCM caps support 8 to 96 kHz and up to 8 channels.

## Control Flow

The module includes `mona_dsp.c`, shared DSP, GML helpers, and common Echoaudio code. Card-specific DSP code chooses 56301/56361 firmware and swaps PCI-card ASICs according to rate and external clock speed.

## State and Persistence Behavior

Runtime state includes ASIC code, digital mode, auto-mute, professional S/PDIF, clock source, monitor matrix, and line levels. Static module state is firmware, PCI IDs, topology, and PCM caps.

## Dependencies and Integration Points

It integrates with GML control-register helpers, multiple Mona firmware files, ALSA PCM and controls, and common Echoaudio transport.

## Risks and Test Signals

Risks are wrong ASIC selection for 48 versus 96 kHz, external-box ASIC load failure, and invalid ADAT/double-speed combinations. Test signals include probe across supported IDs, S/PDIF/word/ADAT clock detection, sample-rate changes across 48/96 boundary, and mode switching without losing monitor state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/mona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/mona_dsp.c -->
# sources/distributed-fs/ceph-client/sound/pci/echoaudio/mona_dsp.c

## Purpose

`mona_dsp.c` implements Mona-specific DSP boot, dual ASIC loading, 48/96 kHz ASIC switching, GML sample-rate and clock control, and digital-mode handling.

## Important APIs, Types, and Functions

`init_hw()` validates Mona, selects 56301 or 56361 DSP firmware, enables internal/S/PDIF/word/ADAT clocks, and sets RCA/optical/ADAT modes. `load_asic()` loads the PCI-card 48 kHz ASIC and external ASIC, checks status, and initializes the control register. `switch_asic()` chooses 48 or 96 kHz PCI-card ASIC based on double-speed needs. `set_sample_rate()` swaps ASICs if needed, rejects ADAT double-speed, and maps fixed GML rates. `set_input_clock()` handles internal, S/PDIF, word, and ADAT and may switch ASICs using detected S/PDIF/word 96 kHz bits. `dsp_set_digital_mode()` handles RCA, optical, and ADAT with incompatible-clock fallback.

## Control Flow

Probe loads DSP plus both required ASIC stages. Rate changes under internal clock may temporarily drop `chip->lock` while loading a new ASIC, then relock to finish control-register writes. External clock changes similarly switch ASIC based on detected clock speed. Digital-mode changes force internal 48 kHz when needed and ensure ADAT does not use a 96 kHz ASIC.

## State and Persistence Behavior

Persistent fields include `asic_code`, `input_clock`, `digital_mode`, `digital_in_automute`, and `sample_rate`; comm-page state includes GML control bits and clock detect status. The selected ASIC image is part of runtime state and must match rate/mode.

## Dependencies and Integration Points

It depends on `echoaudio_gml.c`, shared DSP/ASIC loading, Mona firmware entries, and ALSA controls for rate, clock, and digital mode.

## Risks and Test Signals

Risks are lock ordering around sleeping ASIC loads, using the wrong ASIC for detected 96 kHz external clocks, and leaving ADAT in double-speed mode. Test with internal and external 44.1/48/88.2/96 kHz transitions, S/PDIF/word clock detection, ADAT mode switching, and monitor/gain persistence.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/echoaudio/mona_dsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/Makefile

## Purpose

This Makefile defines the ALSA EMU10K1-related kernel objects built from the `sound/pci/emu10k1` directory.

## Important APIs, Types, and Functions

`snd-emu10k1-y` links the main EMU10K1/Audigy driver from PCI binding, hardware init, IRQ, memory, voice, MPU-401 MIDI, PCM, I/O, mixer, FX8010, timer, and P16V files. `snd-emu10k1-$(CONFIG_SND_PROC_FS)` optionally adds procfs diagnostics. `snd-emu10k1-synth-y` builds the wavetable synth companion from synth, callback, and patch files. `snd-emu10k1x-y` builds the separate EMU10K1X driver. `obj-$(CONFIG_SND_EMU10K1)`, `obj-$(CONFIG_SND_EMU10K1_SEQ)`, and `obj-$(CONFIG_SND_EMU10K1X)` connect those objects to Kconfig.

## Control Flow

Kbuild evaluates the selected config symbols and links the corresponding composite modules. The synth module is separate from the main PCI module and depends on sequencer configuration.

## State and Persistence Behavior

The file has no runtime state; its persistent effect is build composition and feature-dependent object inclusion.

## Dependencies and Integration Points

It integrates the driver with kernel Kbuild and config symbols. Source-level dependencies are reflected by object grouping: the main driver exports services used by PCM/mixer/synth components, and the synth module includes callback and patch loading code.

## Risks and Test Signals

Risks include missing an object from a composite module, causing unresolved symbols or disabled functionality. Test signals are successful builds with `CONFIG_SND_EMU10K1`, `CONFIG_SND_EMU10K1_SEQ`, `CONFIG_SND_PROC_FS`, and `CONFIG_SND_EMU10K1X` combinations.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1.c

## Purpose

`emu10k1.c` is the PCI driver entry point for Creative EMU10K1, Audigy, and Audigy 2 family ALSA cards. It declares module parameters, PCI IDs, probe sequencing, optional wavetable sequencer setup, and power-management callbacks.

## Important APIs, Types, and Functions

Module parameters control ALSA card index/id/enable, FX8010 external input/output masks, sequencer ports, max synth voices, max sample buffer size, IR enablement, and forced subsystem model. `snd_emu10k1_ids` matches Creative PCI device IDs `0002`, `0004`, and `0008`. `snd_card_emu10k1_probe()` creates the ALSA card, clamps sample cache size, calls `snd_emu10k1_create()`, registers PCM devices, mixer, timer, multi-channel PCM, optional P16V PCM, MIDI, FX8010, and optional synth sequence device. `snd_emu10k1_suspend()` and `snd_emu10k1_resume()` save/restore AC97, FX, registers, P16V, and hardware init state. `module_pci_driver()` registers the PCI driver.

## Control Flow

Probe skips disabled slots, allocates a devm-managed ALSA card, initializes hardware through `snd_emu10k1_create()`, then layers ALSA devices in dependency order: PCM, mixer, timer, multi, P16V, MIDI, FX8010, and synth. It fills card names and registers the card. Suspend cancels E-MU work, suspends subdevices, saves registers, and shuts down hardware; resume reinitializes hardware, restores FX/AC97/registers/P16V, and returns the card to D0.

## State and Persistence Behavior

Static state includes module parameter arrays and the PCI ID table. Per-card state is in `struct snd_emu10k1` stored as `card->private_data`. Power management persists register snapshots through helpers in `emu10k1_main.c`.

## Dependencies and Integration Points

It depends on ALSA core/initval, PCI APIs, `sound/emu10k1.h`, optional sequencer support, and many driver-internal creation functions implemented in sibling files.

## Risks and Test Signals

Risks include partial probe ordering bugs, missing cleanup on intermediate failures, invalid module parameters, and PM restore ordering regressions. Test signals are probe on supported PCI IDs, all ALSA devices appearing, synth device creation with sequencer enabled, suspend/resume with active PCM, and correct behavior with P16V/Audigy variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_callback.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_callback.c

## Purpose

`emu10k1_callback.c` implements `snd_emux` wavetable synth callbacks for EMU10K1 hardware voices. It allocates/reclaims hardware voices, prepares sample playback registers, starts and releases envelopes, updates modulation parameters, and frees voices back to the main driver.

## Important APIs, Types, and Functions

`snd_emu10k1_ops_setup()` installs `emu10k1_ops` into an emux instance. `snd_emu10k1_synth_get_voice()` steals an active synth voice for PCM when needed. `lookup_voices()` ranks candidate voices as free, off, released, playing, or ended. `get_voice()` allocates a hardware voice through `snd_emu10k1_voice_alloc()`. `start_voice()` maps sample memory, adjusts loop addresses, programs routing, pitch, envelopes, LFOs, filter, cache, and map registers. `trigger_voice()` enables playback. `release_voice()`, `terminate_voice()`, and `free_voice()` stop/release hardware and sample-map references. `update_voice()` writes live volume, pitch, pan, modulation, tremolo, and filter parameters. `make_fmmod()`, `make_fm2frq2()`, and `get_pitch_shift()` derive register values.

## Control Flow

The synth module registers these callbacks during probe. When emux needs a note, `get_voice()` selects or allocates a channel; `start_voice()` maps sample memory and writes a full register set while the channel is silent; `trigger_voice()` starts the envelope and pitch. MIDI/control changes call `update_voice()`. Note-off calls `release_voice()`, and voice cleanup calls `terminate_voice()`/`free_voice()`. PCM voice pressure can call `snd_emu10k1_synth_get_voice()` to reclaim a synth channel.

## State and Persistence Behavior

State spans `struct snd_emux_voice`, hardware voice registers, `struct snd_emu10k1_memblk` map locks, `hw->voices[]`, and `emux->num_voices`. `start_voice()` mutates sample address fields by adding mapped offsets, so sample mapping and voice lifecycle must stay coordinated.

## Dependencies and Integration Points

It depends on `emu10k1_synth_local.h`, `sound/asoundef.h`, emux core, EMU10K1 register write helpers, voice allocator, and synth memory mapping functions from other EMU10K1 files.

## Risks and Test Signals

Risks include leaked `map_locked` references, voice stealing while still audible, invalid loop unroll/address math, Audigy versus EMU10K1 routing register differences, and the noted `hw == NULL` free path. Test with wavetable playback, heavy polyphony and voice stealing, PCM plus synth concurrency, modulation/pitch/pan updates, and unload/replug cycles.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_main.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_main.c

## Purpose

`emu10k1_main.c` is the central hardware-control implementation for the EMU10K1/Audigy driver. It initializes and shuts down the chip, identifies card models, configures DMA memory, firmware-backed E-MU 1010/Hana hardware, ECARD/CardBus variants, interrupts, voice defaults, FX engine setup, and suspend/resume register preservation.

## Important APIs, Types, and Functions

Core entry points are `snd_emu10k1_create()`, `snd_emu10k1_done()`, `snd_emu10k1_voice_init()`, `snd_emu10k1_suspend_regs()`, `snd_emu10k1_resume_init()`, and `snd_emu10k1_resume_regs()`. Hardware init helpers include `snd_emu10k1_init()`, `snd_emu10k1_audio_enable()`, `snd_emu10k1_ecard_init()`, `snd_emu10k1_ecard_write()`, `snd_emu10k1_ecard_setadcgain()`, `snd_emu10k1_cardbus_init()`, `snd_emu10k1_emu1010_init()`, `snd_emu1010_load_firmware()`, `snd_emu1010_load_dock_firmware()`, `emu1010_dock_event()`, `emu1010_clock_event()`, `emu1010_work()`, and `emu1010_interrupt()`. `emu_chip_details[]` maps PCI IDs/subsystems/revisions to model capabilities such as EMU10K1, Audigy, CA0102/CA0108, CA0151/P16V, CardBus, E-MU 1010, ECARD, AC97, speaker layouts, and quirks.

## Control Flow

`snd_emu10k1_create()` enables the PCI device, initializes locks/lists/work, reads subsystem identity, selects a capability table entry, detects IOMMU workaround needs, sets DMA masks and register bases, requests I/O regions, allocates the page table and silent page, creates the synth sample memory header, sets PCI bus mastering, applies extin/extout masks, and runs variant-specific initialization. It then requests the IRQ, initializes S/PDIF bits, fills the page table with silent-page mappings, assigns voice numbers, runs `snd_emu10k1_init()`, allocates PM buffers, initializes FX8010, enables audio, and optionally registers procfs.

`snd_emu10k1_init()` disables interrupts/audio, resets capture buffers and voices, configures Audigy/P16V/P17V special registers, SPI DAC and I2C ADC init where present, sets page table and silent mappings, writes HCFG according to model, optionally toggles IR, and enables expanded memory. E-MU 1010 setup loads Hana firmware, optional dock firmware, programs FPGA routing, default clocks, MIDI routing, IRQ enables, and unmute state. Shutdown disables interrupts, silences voices, stops DSP execution, resets buffers/page table, and locks/mutes hardware.

Suspend saves per-voice and global registers into allocated buffers; resume reruns variant init, core init, audio enable, HCFG/A_IOCFG restore, and register replay.

## State and Persistence Behavior

Persistent driver state includes `struct snd_emu10k1` fields for capability model, port, IRQ, DMA mask, page tables, silent page, memory header, voice table, S/PDIF bits, FX8010 state, E-MU 1010 firmware pointers/dock state/clock state, saved PM registers, and IOMMU workaround flag. Firmware objects are retained for reuse and released in `snd_emu10k1_free()`. PM state is stored in `saved_ptr`, `saved_hcfg`, and `saved_a_iocfg`.

## Dependencies and Integration Points

The file depends on Linux PCI, firmware, DMA, IOMMU, workqueue, mutex/spinlock, vmalloc, and ALSA core APIs. It integrates with sibling IRQ, I/O, memory, voice, FX, mixer, PCM, P16V, procfs, and synth code through exported driver helpers and shared `sound/emu10k1.h` types.

## Risks and Test Signals

Risks include model-table misidentification, DMA mask/page-table mistakes, IOMMU over-read workaround regressions, variant-specific GPIO/HCFG ordering, E-MU firmware load failures, workqueue versus suspend/shutdown races, and PM register coverage gaps. Test with builds across PM/procfs configs, probe on representative SB Live/Audigy/Audigy2/E-MU/CardBus models, firmware load and dock hotplug events, DMA playback/capture under IOMMU, FX8010 operation, suspend/resume, and module unload cleanup.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_patch.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_patch.c

## Purpose

`emu10k1_patch.c` implements SoundFont sample allocation and transfer callbacks for the EMU10K1 wavetable synth. It converts sample metadata into hardware-friendly memory blocks and copies user sample data into synth memory.

## Important APIs, Types, and Functions

`snd_emu10k1_sample_new()` validates sample/header input, warns on unsupported bidirectional or reverse loops, determines 8-bit versus 16-bit storage, signedness XOR conversion, blank head/tail sizing, loop boundaries, and loop unrolling for the hardware cache. It allocates synth memory with `snd_emu10k1_synth_alloc()`, fills blank regions with `snd_emu10k1_synth_memset()`, copies user data with `snd_emu10k1_synth_copy_from_user()`, sets `sp->v.truesize`, and unwinds on copy failure. `snd_emu10k1_sample_free()` frees the sample block.

## Control Flow

When emux loads a patch, `sample_new` computes the true memory image, adjusts sample start/end/loop offsets by a blank head, unrolls short loops until the loop end exceeds the 64-sample cache window, allocates a memory block, fills/copies data, and records the block on the sample. Freeing releases that block and clears the pointer.

## State and Persistence Behavior

The function mutates `struct snd_sf_sample` fields for adjusted offsets, loop points, true size, and `block`. The allocated memory persists in the EMU10K1 synth memory manager until `sample_free()` or error unwind.

## Dependencies and Integration Points

It depends on `emu10k1_synth_local.h`, emux sample loading, and synth memory helpers implemented elsewhere in the EMU10K1 driver. User data enters through `copy_from_user`-style helper paths.

## Risks and Test Signals

Risks include integer/offset mistakes in loop unrolling, unsupported loop modes only warning rather than failing, user-copy error unwind leaks, and signedness conversion bugs. Test signals are successful SoundFont load/unload, single-shot and looped samples shorter than 64 samples, 8-bit and 16-bit signed/unsigned samples, and clean failure on invalid loop size or copy fault.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_patch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_synth.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_synth.c

## Purpose

`emu10k1_synth.c` registers the EMU10K1 wavetable synth as an ALSA sequencer device and connects the generic emux synth engine to EMU10K1 hardware callbacks.

## Important APIs, Types, and Functions

`snd_emu10k1_synth_probe()` reads `struct snd_emu10k1_synth_arg`, clamps max voices to 1..64, allocates an emux instance, installs EMU10K1 ops with `snd_emu10k1_ops_setup()`, wires hardware pointer, voice/port counts, sample memory header, MIDI port mapping, panning mode, and fixed hwdep index, then registers emux and stores it under `hw->synth`. `snd_emu10k1_synth_remove()` detaches `hw->synth` and `hw->get_synth_voice` under `voice_lock` and frees emux. `emu10k1_synth_driver` registers the sequencer driver for `SNDRV_SEQ_DEV_ID_EMU10K1_SYNTH`.

## Control Flow

The main PCI driver creates a sequence device with synth args during probe. The sequencer core calls this probe, which builds and registers emux. Removal reverses the hardware linkage before freeing emux to prevent callbacks into stale state.

## State and Persistence Behavior

State persists in the emux instance, `hw->synth`, and `hw->get_synth_voice`. The synth uses the main card's `memhdr`, so sample memory lifetime is tied to the hardware driver.

## Dependencies and Integration Points

It depends on ALSA sequencer/emux infrastructure, `emu10k1_synth_local.h`, and the main EMU10K1 card state provided through `snd_emu10k1_synth_arg`.

## Risks and Test Signals

Risks include invalid args, voice count outside hardware capacity, stale synth pointers on removal, and mismatched MIDI device indexes for Audigy versus non-Audigy. Test signals are sequencer synth device creation/removal, SoundFont load, MIDI playback through configured ports, and module unload with no dangling callbacks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_synth_local.h -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_synth_local.h

## Purpose

`emu10k1_synth_local.h` is the private header shared by the EMU10K1 wavetable synth module files. It declares patch, memory-header, callback setup, and voice-stealing interfaces.

## Important APIs, Types, and Functions

The header includes `sound/core.h` and `sound/emu10k1_synth.h`, then declares `snd_emu10k1_sample_new()`, `snd_emu10k1_sample_free()`, `snd_emu10k1_memhdr_init()`, `snd_emu10k1_ops_setup()`, and `snd_emu10k1_synth_get_voice()`.

## Control Flow

`emu10k1_synth.c` includes this header to call `snd_emu10k1_ops_setup()`. `emu10k1_callback.c` includes it to expose callback setup and use sample callbacks. `emu10k1_patch.c` includes it to define the sample allocation/free functions declared here.

## State and Persistence Behavior

The header owns no state, but its prototypes define how synth files manipulate persistent emux state, EMU10K1 sample memory blocks, and hardware voice allocation.

## Dependencies and Integration Points

It is a local integration point between the synth registration, callback, and patch-transfer files, and with public ALSA EMU10K1 synth structures.

## Risks and Test Signals

Risks are prototype drift or exposing functions with mismatched types across synth files. Test signals are successful build of `snd-emu10k1-synth`, clean modpost, and runtime synth probe with patch loading and voice callbacks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1_synth_local.h -->
