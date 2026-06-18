# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_patch.c

## Purpose
`ac97_patch.c` is the ALSA AC97 codec quirk and vendor-extension layer. The generic AC97 core detects a codec, then selected `patch_*()` routines in this file modify `struct snd_ac97` capabilities, flags, register defaults, mixer control names, TLV metadata, jack routing, SPDIF controls, and PM restore hooks so non-standard codecs work through the generic AC97 mixer/PCM paths.

## Important APIs, Types, And Functions
- `patch_build_controls()` adds arrays of `struct snd_kcontrol_new` controls to `ac97->bus->card` using `snd_ac97_cnew()`.
- `reset_tlv()` rewrites TLV scale data for already-created mixer controls when codec volume resolution differs from generic probing.
- `ac97_update_bits_page()` serializes paged vendor-register updates through `ac97->page_mutex`, switches `AC97_INT_PAGING`, updates a register, and restores the previous page.
- Shared jack controls include `ac97_surround_jack_mode_*()` and `ac97_channel_mode_*()`, backed by `ac97->indep_surround` and `ac97->channel_mode`.
- `is_surround_on()`, `is_clfe_on()`, `is_shared_*()` centralize channel-mode decisions used by Realtek, Analog Devices, C-Media, IC Ensemble, and VIA update callbacks.
- Codec families covered include Yamaha YMF7x3, Wolfson WM97xx, TriTech, SigmaTel STAC97xx, Cirrus CS42xx, Conexant, Analog Devices AD18xx/AD19xx, Realtek ALC20x/65x/850, Aztech AZF3328, C-Media CM97xx/CM9780, VIA VT1613/1616/1617A/1618, IC Ensemble/IT2646, Silicon Labs SI3036 modem codec, and National LM4550.
- `snd_ac97_find_mixer_ctl()` and `snd_ac97_add_vmaster()` support VIA VT1616 control renaming and virtual master creation.

## Control Flow
The file is invoked indirectly by the AC97 core after codec identification. Each patch function updates `ac97->build_ops` with callbacks such as `.build_specific`, `.build_3d`, `.build_spdif`, `.build_post_spdif`, `.resume`, or `.update_jacks`. Later generic mixer construction calls those hooks to add or rename controls. Runtime mixer writes call the per-control `.put` callbacks, which update vendor registers and sometimes recompute jack-routing state.

Major families follow a repeated pattern: add custom controls, write cache defaults, mark missing generic controls via `ac97->flags`, force capability bits when hardware fails to advertise them, and attach an `update_jacks` callback when controls can repurpose physical jacks. Analog Devices patches also detect chained AD1881-family codecs and store per-codec IDs/configuration in `ac97->spec.ad18xx`.

## State And Persistence
Persistent runtime state is stored in `struct snd_ac97`, not in this file. Important fields include `regs[]` as the AC97 register cache, `flags`, `caps`, `scaps`, `ext_id`, `rates[]`, `res_table`, `build_ops`, `channel_mode`, `indep_surround`, `spec.dev_flags`, and `spec.ad18xx`. Most writes use `snd_ac97_write_cache()` or `snd_ac97_update_bits()`, so suspend/resume and proc views can use the cached state. PM paths for Wolfson and Analog Devices restore vendor registers and multi-codec routing after resume.

## Dependencies And Integration Points
This file depends on declarations and generic helpers from `ac97_local.h` and `ac97_patch.h`, plus AC97 register and codec ID definitions. It integrates with the ALSA control core through `snd_ctl_add()`, `snd_ctl_find_id_mixer()`, `snd_ctl_make_virtual_master()`, `snd_ctl_add_followers()`, and with the AC97 bus through `ac97->bus->card` and bus ops. It also affects PCM behavior by changing `ac97->rates[]`, SPDIF flags, channel-map pointers, and DAC capability flags consumed by `ac97_pcm.c`.

## Risks
- Vendor register writes are hardware-specific; wrong subsystem exceptions or revision detection can mute outputs, misroute jacks, or expose controls that do not work.
- Several callbacks modify paged vendor registers. Missing page restoration would corrupt unrelated register access; `ac97_update_bits_page()` mitigates this but direct writes must be checked carefully.
- AD18xx chained-codec detection rewrites serial config and codec IDs; regressions can remove surround/CLFE DACs or break resume.
- Some comments mark uncertain behavior (`FIXME`, model-specific bits, undocumented C-Media/Realtek fields), so behavioral verification needs real hardware or targeted emulation.
- Control renaming/removal is string-based and depends on generic control names staying stable.

## Test Signals
- Boot/probe logs should show correct codec identification and no mixer-control registration errors.
- ALSA mixer enumeration should include expected vendor controls and omit controls hidden via `AC97_HAS_NO_*` flags.
- Channel mode and surround jack mode changes should update hardware registers and audible jack routing.
- SPDIF rate/source controls should accept only supported rates per codec family.
- Suspend/resume should preserve mixer values, jack modes, SPDIF status, and AD18xx chained codec state.
- Regression tests can inspect `ac97->regs[]`, `flags`, `scaps`, and registered control names after invoking each patch with mocked AC97 read/write hooks.
