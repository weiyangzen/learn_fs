# subset-b-006394 EMU10K1 audio driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1x.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1x.c

## Purpose

This file is a complete ALSA PCI driver for Creative's Dell OEM EMU10K1X device (`PCI_VDEVICE(CREATIVE, 0x0006)`). It is separate from the larger EMU10K1/Audigy driver because the EMU10K1X has a simpler register model: three playback DMA channels, one capture DMA channel, AC97 codec access, S/PDIF routing/status controls, a `/proc` register debug interface, and one MPU-401 UART raw-MIDI port. The driver exposes three stereo playback PCM devices for front, rear, and center/LFE, plus capture on device 0.

## Important APIs, types, and functions

The main private state is `struct emu10k1x`, which holds the ALSA card, PCI device, I/O base, IRQ, AC97 pointer, PCM pointer, three playback `voices`, one `capture_voice`, cached `spdif_bits[3]`, a small DMA page used for playback period descriptor lists, and embedded MIDI state. `struct emu10k1x_voice` links hardware channel numbers to `struct emu10k1x_pcm`, while `struct emu10k1x_midi` stores rawmidi substreams, locks, interrupt bits, port offsets, and the dispatch callback.

Register helpers `snd_emu10k1x_ptr_read`, `snd_emu10k1x_ptr_write`, `snd_emu10k1x_intr_enable`, `snd_emu10k1x_intr_disable`, and `snd_emu10k1x_gpio_write` serialize MMIO/indexed register access with `emu_lock`. PCM operations are split into playback (`snd_emu10k1x_playback_open`, `snd_emu10k1x_pcm_hw_params`, `snd_emu10k1x_pcm_prepare`, `snd_emu10k1x_pcm_trigger`, `snd_emu10k1x_pcm_pointer`) and capture (`snd_emu10k1x_pcm_open_capture`, `snd_emu10k1x_pcm_hw_params_capture`, `snd_emu10k1x_pcm_prepare_capture`, `snd_emu10k1x_pcm_trigger_capture`, `snd_emu10k1x_pcm_pointer_capture`). Codec callbacks `snd_emu10k1x_ac97_read` and `snd_emu10k1x_ac97_write` implement the `snd_ac97_bus_ops`.

Top-level setup flows through `snd_emu10k1x_probe`, `__snd_emu10k1x_probe`, and `snd_emu10k1x_create`. `snd_emu10k1x_pcm` creates the ALSA PCM devices and channel maps. `snd_emu10k1x_mixer` installs IEC958 and analog/digital jack controls. `emu10k1x_midi_init` and `snd_emu10k1x_midi` register the rawmidi device. `snd_emu10k1x_interrupt` is the shared IRQ handler for PCM and MIDI events.

## Control Flow

Probe checks the module card slot, allocates an ALSA card with private `struct emu10k1x`, enables PCI, applies a 28-bit coherent DMA mask, requests BARs and the shared IRQ, allocates a 4 KiB descriptor page, initializes playback voices, programs default S/PDIF channel status words, selects analog routing/GPIO defaults, enables audio in `HCFG`, then creates PCM, AC97, mixer, MIDI, and proc entries before registering the card.

Playback open constrains period count to an integer and period bytes to a 64-byte step, allocates per-substream `struct emu10k1x_pcm`, and assigns fixed hardware capabilities: S16_LE, 48 kHz, stereo, up to 32 KiB buffer and 2 to 8 periods. `hw_params` binds the ALSA substream to `voices[pcm->device]`. `prepare` writes one 8-byte DMA list entry per period into the shared descriptor page at `1024 * voice`, then programs `PLAYBACK_LIST_ADDR`, `PLAYBACK_LIST_SIZE`, `PLAYBACK_LIST_PTR`, `PLAYBACK_POINTER`, `PLAYBACK_DMA_ADDR`, and `PLAYBACK_PERIOD_SIZE`. `trigger` enables loop or loop+half-loop interrupts depending on period count and sets the matching `TRIGGER_CHANNEL_*` bit; stop clears the bit and disables interrupts. `pointer` combines `PLAYBACK_LIST_PTR` with `PLAYBACK_POINTER`, rereading if the list pointer changed mid-sample, and wraps at the ALSA buffer size.

Capture open has the same format/rate constraints but fixes periods to 2. Only one capture voice exists, so `hw_params_capture` returns `-EBUSY` when already in use. Capture prepare programs `CAPTURE_DMA_ADDR`, `CAPTURE_BUFFER_SIZE`, `CAPTURE_POINTER`, and `CAPTURE_UNKNOWN`. Capture trigger toggles `TRIGGER_CAPTURE` and capture loop/half-loop interrupts. Capture pointer reads `CAPTURE_POINTER` and wraps to buffer frames.

The IRQ handler reads `IPR`, returns `IRQ_NONE` if no bit is pending, dispatches capture and playback period notifications through `snd_pcm_period_elapsed`, disables stale interrupts when no voice is active, calls the MIDI interrupt callback for TX/RX bits, then acknowledges by writing the original status back to `IPR`.

## State and Persistence Behavior

Runtime state is kept in the ALSA card private area and is reset on driver bind/unbind. PCM stream state lives in per-open `runtime->private_data`; voice ownership is recorded by `voice->use` and `voice->epcm`. The playback period descriptor page is device DMA memory allocated for the card lifetime. S/PDIF channel status is cached in `emu->spdif_bits[]` and mirrored to `SPCS0..2`; analog/digital output mode is represented directly by hardware `SPDIF_SELECT`, `ROUTING`, and `GPIO` values. MIDI open/close maintains `midi_mode`, substream pointers, and interrupt enable state. There is no disk persistence.

## Dependencies and Integration Points

The file depends on Linux PCI, IRQ, DMA, and I/O port APIs plus ALSA core, PCM, AC97, rawmidi, control, channel-map, and proc-info APIs. It registers as a normal `pci_driver` via `module_pci_driver`. User-space integration is through ALSA PCM devices, AC97 mixer controls, IEC958 controls, rawmidi, and `/proc/asound/.../emu10k1x_regs`. The AC97 layer supplies most analog mixer controls; this file adds EMU10K1X-specific S/PDIF and routing controls.

## Risks

Hardware register programming is mostly undocumented, with `PLAYBACK_UNKNOWN*`, `CAPTURE_UNKNOWN`, `ROUTING`, and GPIO values encoded as magic constants. The playback pointer calculation depends on stable ordering between `PLAYBACK_LIST_PTR` and `PLAYBACK_POINTER` and may be sensitive to races around period rollover. Playback voice allocation for devices 0 to 2 lacks an explicit busy check comparable to capture; correctness depends on ALSA open semantics and device/substream topology. The proc register writer allows privileged proc users to poke indexed registers directly, which is useful for debugging but risky on live hardware. MIDI command paths busy-wait for ACKs under locks and report failure as `1` internally before callers map it to `-EIO`.

## Test Signals

Useful signals are successful module probe on the Dell SB0200/EMU10K1X PCI ID, ALSA card registration, clean interrupt handling with shared IRQs, `aplay` on all three playback devices, `arecord` on device 0, period elapsed timing at two-period and multi-period settings, XRUN-free pointer progression, AC97 mixer enumeration, analog/digital output switching, IEC958 status read/write round trips, rawmidi duplex loopback or hardware MIDI traffic, suspend/unbind cleanup that stops audio and interrupts, and manual proc register read coverage.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emu10k1x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emufx.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emufx.c

## Purpose

This file manages the EMU10K1/EMU10K2 FX8010 DSP. It builds and uploads the default mixer/effects microcode for SB Live! and Audigy-family cards, exposes a hwdep ioctl API for reading and replacing DSP GPR/TRAM/code state, creates dynamic ALSA mixer controls backed by DSP GPRs, handles FX DSP interrupt callbacks, configures external TRAM, and saves/restores DSP state for power management.

## Important APIs, types, and functions

The externally visible entry points are `snd_emu10k1_init_efx`, `snd_emu10k1_free_efx`, `snd_emu10k1_fx8010_tram_setup`, `snd_emu10k1_fx8010_new`, `snd_emu10k1_fx8010_register_irq_handler`, `snd_emu10k1_fx8010_unregister_irq_handler`, and the PM helpers under `CONFIG_PM_SLEEP`. The driver header provides the shared data structures: `struct snd_emu10k1_fx8010`, `struct snd_emu10k1_fx8010_code`, `struct snd_emu10k1_fx8010_control_gpr`, `struct snd_emu10k1_fx8010_ctl`, `struct snd_emu10k1_fx8010_pcm`, and `struct snd_emu10k1_fx8010_irq`.

Microcode construction uses `snd_emu10k1_write_op` for 10-bit SB Live! operands and `snd_emu10k1_audigy_write_op` for 11-bit Audigy operands, wrapped by `OP` and `A_OP`. `snd_emu10k1_efx_write` and `snd_emu10k1_efx_read` access instruction memory at `MICROCODEBASE` or `A_MICROCODEBASE`. GPR/TRAM/code accessors (`snd_emu10k1_gpr_poke`, `snd_emu10k1_gpr_peek`, `snd_emu10k1_tram_poke`, `snd_emu10k1_tram_peek`, `snd_emu10k1_code_poke`, `snd_emu10k1_code_peek`) implement the low-level data movement for ioctl and in-kernel initialization.

Dynamic mixer control support is implemented by `snd_emu10k1_gpr_ctl_info`, `snd_emu10k1_gpr_ctl_get`, `snd_emu10k1_gpr_ctl_put`, `snd_emu10k1_verify_controls`, `snd_emu10k1_add_controls`, `snd_emu10k1_del_controls`, and `snd_emu10k1_list_controls`. Translation tables map user values to DSP coefficient/register values: dB table, bass and treble biquad coefficient tables, on/off values, negate, and high-resolution volume mode.

## Control Flow

`snd_emu10k1_init_efx` initializes the FX IRQ lock and GPR control list, then dispatches to `_snd_emu10k1_audigy_init_efx` for Audigy or `_snd_emu10k1_init_efx` for SB Live!. Both initializers allocate one combined map for GPR, TRAM data, TRAM address, and instruction words; mark the relevant GPR/TRAM bitmaps valid; construct DSP instructions sequentially; populate an array of GPR-backed ALSA controls; clear unused instruction memory; then call `snd_emu10k1_icode_poke(..., in_kernel=true)` to stop the DSP, delete controls, write GPR/TRAM/code, add controls, and restart the DSP.

The Audigy initializer builds a higher-capacity 1024-instruction program with 512 GPRs and 256 TRAM registers. It handles front/rear/center/LFE/side playback, stereo mix, capture mix, optional 7.1 side channels, EMU1010/0404-style 32-bit FPGA capture conversion into paired 16-bit FX buses, AC97 or non-AC97 inputs, tone controls, master volume, analog/headphone/digital outputs, an optical raw S/PDIF switch, card-specific `spdif_bug` right-channel delay, and 16-channel EFX capture. The SB Live! initializer builds a 512-instruction program with 256 GPRs and 160 TRAM registers. It includes a raw S/PDIF PCM path backed by FX8010 TRAM, wave/synth/surround/front/center/LFE playback and capture controls, optional external input controls derived from `extin_mask`, tone controls, physical output routing from `extout_mask`, and SB Live! 5.1 FXBUS2 remapping.

The hwdep path created by `snd_emu10k1_fx8010_new` exposes `SNDRV_HWDEP_IFACE_EMU10K1`. `snd_emu10k1_fx8010_ioctl` handles version/info queries, code poke/peek, PCM poke/peek, TRAM setup, DSP stop/continue, zero TRAM counter, single-step, and debug register read. Mutating operations that alter microcode or debug state require `CAP_SYS_ADMIN`; info/peek paths copy state back to user buffers. `snd_emu10k1_ipcm_poke` and `snd_emu10k1_ipcm_peek` configure internal FX8010 PCM records with bounds checks and `array_index_nospec`.

FX DSP interrupts are list-driven. `snd_emu10k1_fx8010_register_irq_handler` adds an IRQ record under `fx8010.irq_lock`, installs `emu->dsp_interrupt`, and enables `INTE_FXDSPENABLE` for the first handler. The interrupt callback checks each handler's running GPR high bits, invokes its callback, and writes `1` back to the running GPR. Unregistration removes the node and disables the DSP interrupt when the list becomes empty.

## State and Persistence Behavior

DSP state persists in hardware registers while the card is powered: GPR values, TRAM data/address registers, microcode words, debug register state, and external TRAM backing DMA pages. The driver mirrors dynamic controls in `emu->fx8010.gpr_ctl`, FX PCM records in `emu->fx8010.pcm[]`, active IRQ handlers in `emu->fx8010.irq_handlers`, and external TRAM allocation in `emu->fx8010.etram_pages`. User-created controls are ALSA controls whose private data is freed by `snd_emu10k1_ctl_private_free`. The default program is regenerated at init rather than loaded from disk.

Under `CONFIG_PM_SLEEP`, `snd_emu10k1_efx_alloc_pm_buffer` allocates buffers for GPR, TRAM, and microcode snapshots. Suspend reads all relevant DSP state into those buffers. Resume restores external TRAM base/size, single-steps the DSP, writes saved GPR/TRAM/code back, then restarts the processor. One notable implementation detail is the Audigy resume TRAM control write path, which writes both shifted address parts to `TANKMEMADDRREGBASE`; this deserves scrutiny because normal TRAM poke writes the upper part to `A_TANKMEMCTLREGBASE`.

## Dependencies and Integration Points

This file depends on ALSA control, hwdep, TLV, DMA, user-copy, capability, mutex, spinlock, nospec, and delay APIs, plus the EMU10K1 register and structure definitions in `include/sound/emu10k1.h`. It is called from main card initialization (`snd_emu10k1_init_efx`), hwdep registration, PCM code using FX8010 PCM records, mixer code that exposes controls created by this file, and PM code that invokes the save/restore helpers. User-space integration includes normal ALSA mixer controls and privileged hwdep ioctls used by FX8010 tooling.

## Risks

The highest-risk surface is user-supplied DSP code and control metadata. `CODE_POKE` is privileged, but it still accepts complex pointer-bearing structures and must validate control identity, ranges, TLV size, GPR counts, code-valid bitmaps, and user copies correctly. Microcode construction is dense and register-number sensitive; GPR overflow checks catch only final allocation bounds. Dynamic controls can be overwritten in place, so mistakes can desynchronize ALSA control state from hardware GPR state. `snd_emu10k1_fx8010_tram_setup` changes external DMA memory while locking the tank cache and must leave the cache unlocked on all successful allocation paths. PM restore of Audigy TRAM addressing should be regression-tested because it differs from normal programming. Busy DSP stop/start around code updates can produce audible glitches by design.

## Test Signals

Strong signals include successful default DSP initialization on SB Live!, Audigy, Audigy with 7.1, EMU1010/1616/0404, and SB Live! 5.1 variants; expected ALSA mixer controls with working TLV ranges; correct tone-control coefficient updates; playback and capture routing through front/rear/center/LFE/side and EFX buses; raw S/PDIF PCM operation on SB Live!; 16-channel EFX capture from EXTIN or EMU FPGA inputs; hwdep `INFO`, `CODE_PEEK`, `PCM_PEEK`, and privileged `CODE_POKE` validation including failure paths; FX interrupt handler register/unregister coverage; TRAM allocation size changes; suspend/resume audio continuity; and KASAN/KMSAN/usercopy testing of ioctl paths.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emufx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emumixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emumixer.c

## Purpose

This file builds the ALSA mixer/control surface for EMU10K1, Audigy, and EMU1010-family cards. It combines AC97 mixer setup and cleanup, S/PDIF channel-status controls, PCM send-routing/send-volume/attenuation controls, multichannel EFX PCM controls, shared analog/digital jack control, Audigy I2C ADC source and gain controls, EMU1010 FPGA routing/source controls, clock and optical mode controls, DAC/ADC pad controls, P16V mixer integration, and card-model-specific control removal/renaming.

## Important APIs, types, and functions

The public entry point is `snd_emu10k1_mixer(struct snd_emu10k1 *emu, int pcm_device, int multi_device)`. Helper `add_ctls` instantiates a template `struct snd_kcontrol_new` for a list of names, using the list index as `private_value`. IEC958 callbacks are `snd_emu10k1_spdif_info`, `snd_emu10k1_spdif_get`, `snd_emu10k1_spdif_get_mask`, and `snd_emu10k1_spdif_put`, operating on cached `emu->spdif_bits[3]` and hardware `SPCS0..2`.

EMU1010 routing is represented by many static text/register/default arrays and `struct snd_emu1010_routing_info`. `emu1010_idx` selects the table by `card_capabilities->emu_model`. `snd_emu1010_output_source_apply`, `snd_emu1010_input_source_apply`, and `snd_emu1010_apply_sources` write source-to-destination links through `snd_emu1010_fpga_link_dst_src_write`. Source enum controls are implemented by `snd_emu1010_input_output_source_info`, output/input get/put callbacks, and `add_emu1010_source_mixers`.

Pad, clock, and optical controls use `snd_emu1010_adc_pads_get/put`, `snd_emu1010_dac_pads_get/put`, `snd_emu1010_clock_source_info/get/put`, `snd_emu1010_clock_fallback_get/put`, `snd_emu1010_optical_out_get/put`, and `snd_emu1010_optical_in_get/put`. Audigy I2C capture uses `snd_audigy_i2c_capture_source_*` plus `snd_audigy_i2c_volume_*`. PCM stream control callbacks include `snd_emu10k1_send_routing_*`, `snd_emu10k1_send_volume_*`, `snd_emu10k1_attn_*`, and their multichannel `snd_emu10k1_efx_*` equivalents.

## Control Flow

`snd_emu10k1_mixer` first initializes AC97 if the board advertises an AC97 codec. It creates an AC97 bus, disables VRA, registers the AC97 mixer, adjusts Audigy defaults, handles STAC9758 rear-channel routing, then removes irrelevant AC97 controls. If AC97 is optional and absent, it proceeds with a model-specific mixer name. For I2C-ADC-only boards it removes controls superseded by the external ADC path. It then renames controls to conventional names or board-specific alternatives, including Audigy 4 Pro and CT4760P special cases.

Next it installs per-PCM controls for send routing, send volume, and attenuation on the normal PCM device, then equivalent EFX multichannel controls on `multi_device`. These controls cache values in `emu->pcm_mixer[]` or `emu->efx_pcm_mixer[]`. When a stream is currently attached to hardware voices, `put` callbacks immediately rewrite `FXRT`/`A_FXRT*`, send-amount registers, or `VTFT_VOLUMETARGET` under `reg_lock`.

For non-EMU model SB Live!/Audigy cards, it adds IEC958 mask/default controls. For Audigy or SB Live! cards without EMU daughtercard routing, it adds the analog/digital output jack control, which toggles GPIO bits in `A_IOCFG` and/or `HCFG`, respecting inverted shared-S/PDIF board quirks. If the card has a P16V/CA0151 chip, `snd_p16v_mixer` is called.

For EMU1010-family models, it maps default FPGA source register values to enum indexes, applies all input and output source routes under the FPGA lock, adds clock source and fallback controls, adds model-specific ADC/DAC pad switches, adds optical input/output mode controls when ADAT is available, then adds all source enum controls. For I2C ADC Audigy variants, it adds capture source and per-source volume controls. For Audigy AC97 boards, it adds a `Mic Extra Boost` control backed by AC97 record gain.

## State and Persistence Behavior

Mixer state is cached in `struct snd_emu10k1`: `spdif_bits`, `pcm_mixer[]`, `efx_pcm_mixer[]`, `i2c_capture_source`, `i2c_capture_volume`, and the `emu1010` substructure for source routing, pads, clock, fallback clock, and optical modes. The cached state is mirrored to hardware registers or FPGA registers when controls change. AC97 controls are maintained by the ALSA AC97 layer, with `snd_emu10k1_mixer_free_ac97` clearing `emu->ac97` on free. State lasts for the driver/card lifetime and is not persisted to disk by this file.

## Dependencies and Integration Points

This file depends on ALSA control/TLV/AC97 APIs, EMU10K1 register helpers from the broader driver, EMU1010 FPGA helpers, Audigy I2C helpers, and the P16V mixer. It uses the card capability table extensively: `audigy`, `ecard`, `emu_model`, `ac97_chip`, `i2c_adc`, `adc_1361t`, `ca0151_chip`, `no_adat`, `spk71`, `invert_shared_spdif`, and subsystem IDs alter the mixer surface. Integration with PCM runtime is direct: controls update live voice routing and volumes when `mix->epcm` and voice pointers are present. User-space sees the result as ALSA mixer and PCM controls.

## Risks

The largest maintenance risk is table correctness. EMU1010 source/destination/default arrays must stay aligned; static assertions cover many lengths, but semantic mismatches would route audio incorrectly. `private_value` indexes from generated controls are trusted by callbacks after range checks; wrong name arrays or counts can expose invalid channels. Hardware locking is split across `reg_lock`, `emu_lock`, and FPGA locks, so new callbacks must match the register domain they touch. Control removal/renaming depends on exact AC97 control names, making it sensitive to upstream ALSA naming changes. The shared analog/digital jack writes both Audigy and base HCFG paths on some cards, and board quirks can invert semantics. I2C capture source changes mute, change GPIO, update gains, then unmute by source selection; partial failure handling is limited because I2C writes are fire-and-forget in this code.

## Test Signals

Test signals include expected mixer control enumeration for SB Live!, Audigy, Audigy 2 ZS Notebook/I2C ADC, Audigy 4 Pro, EMU APS, EMU1010 rev1/rev2, EMU1616, and EMU0404; correct absence/removal of unused AC97 controls; successful renames; IEC958 status get/put with out-of-range index rejection; live PCM routing/volume changes reflected in voice registers; EMU1010 source enum changes updating FPGA links; clock-source changes muting, settling, and unmuting; optical mode toggles changing FPGA optical type; ADC/DAC pad switch writes; I2C capture source and volume switching; and regression tests for card-specific subsystem branches.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emumixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emumpu401.c -->
# sources/distributed-fs/ceph-client/sound/pci/emu10k1/emumpu401.c

## Purpose

This file implements MPU-401 UART raw-MIDI support for the main EMU10K1/Audigy driver. It creates one MIDI port on EMU10K1 cards and two MIDI ports on Audigy cards, bridges ALSA rawmidi open/close/trigger operations to the hardware UART, and dispatches MIDI receive/transmit-ready interrupts.

## Important APIs, types, and functions

The public entry points are `snd_emu10k1_midi` and `snd_emu10k1_audigy_midi`. Both use `emu10k1_midi_init` to allocate an ALSA rawmidi device, set input/output ops, initialize `open_lock`, `input_lock`, and `output_lock`, and attach `struct snd_emu10k1_midi` as private data. `snd_emu10k1_midi` configures the classic EMU10K1 port at `MUDATA`; `snd_emu10k1_audigy_midi` configures `A_MUDATA1` and `A_MUDATA2` with separate Audigy interrupt bits and callbacks.

Low-level helpers `mpu401_read` and `mpu401_write` abstract the hardware difference: Audigy accesses MIDI registers through `snd_emu10k1_ptr_read/write`, while non-Audigy cards use direct I/O ports relative to `emu->port`. Macros define data/status/command access and the standard status bits (`0x80` input empty, `0x40` output busy). `snd_emu10k1_midi_cmd` sends `MPU401_RESET` or `MPU401_ENTER_UART` and optionally waits for `MPU401_ACK`.

ALSA rawmidi callbacks are `snd_emu10k1_midi_input_open`, `snd_emu10k1_midi_output_open`, `snd_emu10k1_midi_input_close`, `snd_emu10k1_midi_output_close`, `snd_emu10k1_midi_input_trigger`, and `snd_emu10k1_midi_output_trigger`. Interrupt callbacks are `snd_emu10k1_midi_interrupt`, `snd_emu10k1_midi_interrupt2`, and shared `do_emu10k1_midi_interrupt`.

## Control Flow

Opening either input or output records the substream and sets the matching mode bit under `open_lock`. If the opposite direction is already open, the port is already in UART mode and the callback returns. Otherwise the hardware is reset and put into UART mode, with ACK checking. Closing a direction disables the matching interrupt, clears the mode bit and substream pointer, and resets the hardware only when both directions are closed.

Input trigger simply enables or disables the receive interrupt bit. Output trigger opportunistically writes up to four bytes immediately while the UART reports output-ready, then enables transmit-empty interrupts if more data may be pending. If the ALSA transmit queue is empty or the output mode is no longer active, it returns without enabling TX interrupts. The interrupt handler receives a card-wide status word from the main IRQ code. For RX, it reads one byte when the RX bit is set and input is available, clearing stale bytes if the input side is not active. For TX, it writes one queued byte when the TX bit is set and the hardware is ready, disabling TX interrupts when no byte is available.

## State and Persistence Behavior

All state is runtime-only in `struct snd_emu10k1_midi`: rawmidi pointer, current input/output substreams, mode bits, locks, interrupt masks, hardware port offsets, and dispatch callback. `snd_emu10k1_midi_free` clears `interrupt` and `rmidi` so late IRQs disable MIDI interrupts instead of dereferencing a freed rawmidi object. Hardware UART mode is reset on first open and final close; queued MIDI bytes live in ALSA rawmidi buffers, not in this file.

## Dependencies and Integration Points

The code depends on ALSA rawmidi APIs, EMU10K1 register helpers, card interrupt enable/disable helpers, and the main device struct from `include/sound/emu10k1.h`. The main IRQ handler in the core driver calls the function pointer stored in each MIDI struct when MIDI bits appear in the interrupt status. User-space integration is the standard ALSA rawmidi device interface with duplex capability.

## Risks

The command path busy-waits for ACKs while holding `input_lock`, and failure paths log hardware status/data reads after the lock is released. Interrupt processing reads or writes at most one byte per IRQ, so high traffic depends on timely repeated TX/RX interrupts. The code uses separate open/input/output locks; changes must preserve ordering to avoid races among trigger, close, and interrupt paths. Audigy and non-Audigy register access are intentionally different; using the wrong port offset or interrupt mask would silently break one generation. The free callback only nulls pointers, so main-driver teardown must also ensure interrupts are disabled or synchronized.

## Test Signals

Useful tests include rawmidi device creation on EMU10K1 and two-device creation on Audigy, successful reset/UART ACK on first open, duplex open without redundant reset, final close reset, MIDI receive delivery through `snd_rawmidi_receive`, transmit drain through immediate writes plus TX interrupts, interrupt disabling when queues empty or rawmidi is freed, behavior when no hardware ACK arrives, and regression coverage for Audigy pointer-register access versus legacy I/O-port access.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/emu10k1/emumpu401.c -->
