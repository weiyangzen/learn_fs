# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3d.c

## Purpose
Implements experimental Aureal A3D source programming for AU88x0 hardware. It writes HRTF, ITD, gain, atmospheric filter, slice control, and VDB routing state into MMIO registers, then exposes limited ALSA PCM controls for per-source 3D parameters. It is compiled as part of the broader au88x0 driver and depends on `au88x0_a3d.h`, `au88x0_a3ddata.c`, `au88x0_xtalk.h`, and core ADB/mixer helpers.

## Important APIs, Types, And Functions
The file operates on `a3dsrc_t`, whose `vortex`, `source`, and `slice` fields select one of 16 A3D sources. Low-level setters include `a3dsrc_SetTimeConsts`, `a3dsrc_SetAtmosTarget`, `a3dsrc_SetHrtfTarget`, `a3dsrc_SetItdTarget`, `a3dsrc_SetGainTarget`, `a3dsrc_SetA3DSampleRate`, `a3dsrc_EnableA3D`, and `a3dsrc_DisableA3D`. Reset/programming helpers are `a3dsrc_ZeroState`, `a3dsrc_ZeroStateA3D`, and `a3dsrc_ProgramPipe`. Driver-level helpers include `vortex_A3dSourceHw_Initialize`, `Vort3DRend_Initialize`, `vortex_Vort3D_enable`, `vortex_Vort3D_disable`, `vortex_Vort3D_connect`, and `vortex_Vort3D_InitializeSource`. ALSA control callbacks are `snd_vortex_a3d_*_info`, `snd_vortex_a3d_get`, and the HRTF/ITD/ILD/filter `put` functions.

## Control Flow
`vortex_core_init()` eventually calls `vortex_Vort3D_enable()` on non-AU8820 builds. That initializes crosstalk cancellation via `Vort3DRend_Initialize()`, iterates all A3D slots, initializes per-source state, zeroes slice IO, and registers ALSA controls. PCM route allocation in `vortex_adb_allocroute()` calls `vortex_Vort3D_InitializeSource()` when a stream uses `VORTEX_PCM_A3D`; enabling programs a pass-through HRTF pipe, sample rate, time constants, and the A3D enable bit. `vortex_Vort3D_connect()` allocates fixed mixer inputs, routes each A3D slice output through XTALK, and connects XTALK outputs into playback mixers. ALSA control writes store user values into `a3dsrc_t` arrays and write targets/current hardware registers.

## State And Persistence
State is runtime-only in MMIO and in `vortex->a3d[]`, `vortex->xt_mode`, and `vortex->mixxtlk[]`. No values survive driver unload or reset. Register state is rewritten on init, route allocation, control changes, and shutdown. `a3dsrc_ZeroStateA3D()` mutates `a->slice` temporarily to zero all slices, then restores source/slice.

## Dependencies And Integration Points
The code needs core register access macros `hwwrite`/`hwread`, ADB route helpers, mixer volume helpers, `vortex_adb_checkinout`, and XTALK programming from `au88x0_xtalk.c`. It is included into the au88x0 compilation unit pattern rather than exported independently. ALSA integration is through `snd_ctl_new1`/`snd_ctl_add`; PCM integration is through `VORTEX_PCM_A3D` route allocation.

## Risks
Several coordinate translation helpers are stubs, so ALSA controls do not calculate meaningful HRTF/ITD/ILD/filter values. `snd_vortex_a3d_itd_put()` passes `a->hrtf[0]` and `a->hrtf[1]` to `vortex_a3d_coord2itd()`, whose declared destination type is `a3d_Itd_t`, indicating a likely type/logic bug hidden by array pointer decay. `snd_vortex_a3d_filter_put()` advertises count 4 but reads six values into a six-element local. `vortex_a3d_unregister_controls()` is empty, so control cleanup relies on card teardown or leaks logical removal during disable. A3D routing is disabled on AU8810 due known bad routes, and much of the hardware behavior is reverse-engineered and minimally verified.

## Test Signals
Useful signals are successful module probe on AU8830/AU8810-class hardware, creation of A3D ALSA controls, no resource exhaustion from `vortex_adb_checkinout`, clean playback through `a3d` PCM, no IRQ/DMA errors under period interrupts, and audible pass-through from A3D PCM through XTALK and the playback mixers. Control tests should verify bounds/counts for all four A3D control types and ensure disabling/re-enabling does not duplicate controls.
