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
