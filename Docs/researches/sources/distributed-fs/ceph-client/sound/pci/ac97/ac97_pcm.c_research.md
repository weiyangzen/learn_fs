# sources/distributed-fs/ceph-client/sound/pci/ac97/ac97_pcm.c

## Purpose
`ac97_pcm.c` assigns AC97 time-division slots to ALSA PCM streams, configures codec sample-rate registers, controls SPDIF rates, tracks slot ownership while streams are open, and exposes double-rate hardware constraints.

## Important APIs, Types, And Functions
- `snd_ac97_set_rate()` validates and writes AC97 sample-rate registers or the pseudo-register `AC97_SPDIF`; it is exported.
- `snd_ac97_pcm_assign()` copies requested `struct ac97_pcm` definitions into bus-owned runtime assignments and computes usable slots/rates for each codec.
- `snd_ac97_pcm_open()` locks selected slots in `bus->used_slots`, sets codec rates, and enables SPDIF rate setup when requested.
- `snd_ac97_pcm_close()` releases active slots and optionally powers down affected rate paths under `CONFIG_SND_AC97_POWER_SAVE`.
- `snd_ac97_pcm_double_rate_rules()` installs ALSA hw rules that prevent using double-rate playback with more than two channels.
- Internal helpers include `get_slot_reg()`, `set_spdif_rate()`, `get_pslots()`, `get_cslots()`, and `get_rates()`.

## Control Flow
Assignment begins with `snd_ac97_pcm_assign()`: enumerate up to four codecs on the bus, derive available playback/capture slots, reserve exclusive slots first, calculate shared rates by intersecting each codec's supported rate bitmaps, and optionally assign double-rate playback slots on codec 0. Open then validates requested slots under `bus_lock`, marks them busy, configures each unique rate register once, and stores `pcm->aslots`. Close clears those bits and resets active double-rate state.

`snd_ac97_set_rate()` checks VRA/VRM/DRA capability, validates surround and LFE DAC support, scales rates by `bus->clock`, writes the register, and updates `AC97_EA_DRA` plus double-rate slot selection for front DAC double-rate playback. SPDIF uses `set_spdif_rate()`, which handles Cirrus-style SPDIF, C-Media CM9739 limitations, AES status cache updates, and disables SPDIF on invalid rates.

## State And Persistence
`snd_ac97_pcm_assign()` allocates `bus->pcms` with `kzalloc_objs()` and stores `bus->pcms_count`. Runtime slot state is `bus->used_slots[stream][codec]`, protected by `bus->bus_lock`. `pcm->aslots` and `pcm->cur_dbl` remember the current open configuration. Codec register state persists in `ac97->regs[]`, `ac97->spdif_status`, and hardware registers.

## Dependencies And Integration Points
This file depends on ALSA PCM/control headers, AC97 codec definitions, codec IDs, and `ac97_local.h`. Low-level PCI drivers define requested `struct ac97_pcm` layouts and call these helpers from their PCM open/close/prepare paths. It consumes codec patch state such as `ac97->scaps`, `flags`, `ext_id`, `rates[]`, `addr`, and `bus->no_vra`.

## Risks
- Slot assignment is dense and multi-codec aware; regressions can create overlapping `used_slots`, no-audio streams, or wrong channel-to-slot mappings.
- `reg_ok[cidx]` indexes by `reg - AC97_PCM_FRONT_DAC_RATE`; pseudo or unexpected registers would be unsafe if not filtered.
- SPDIF invalid-rate handling disables output, which is correct but can surprise callers that retry without re-enabling.
- Double-rate handling assumes Intel controller slot placement and only checks codec 0.
- `snd_ac97_pcm_assign()` replaces `bus->pcms` without freeing a previous assignment, so callers are expected to assign once during setup.

## Test Signals
- Unit tests with fake buses/codecs should verify assigned slots, `rates` intersections, SPDIF slot placement, and double-rate availability.
- Concurrent open attempts for overlapping slots should return `-EBUSY`.
- Rate-setting tests should cover no-VRA codecs, DRA on/off transitions, unsupported surround/LFE DACs, Cirrus SPDIF, CM9739 48 kHz-only SPDIF, and invalid SPDIF rates disabling output.
- ALSA hw-params tests should reject more than two channels above 48 kHz.
