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
