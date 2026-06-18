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
