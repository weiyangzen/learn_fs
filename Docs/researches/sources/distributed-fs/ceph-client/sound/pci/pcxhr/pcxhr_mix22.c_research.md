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
