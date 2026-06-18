# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eq.c

## Purpose
Programs the AU8810/AU8830 hardware equalizer, including ten-band coefficients, gains, bypass/A3D bypass gains, peak reading, and ALSA mixer controls for enable, band volume, and peak meter.

## Important APIs, Types, And Functions
Low-level hardware writers are `vortex_EqHw_SetLeftCoefs`, `vortex_EqHw_SetRightCoefs`, state/gain setters, `vortex_EqHw_SetLevels`, `vortex_EqHw_SetSampleRate`, `vortex_EqHw_Enable`, `vortex_EqHw_Disable`, `vortex_EqHw_ZeroState`, `vortex_EqHw_ProgramPipe`, and `vortex_EqHw_Program10Band`. Logical equalizer functions include `vortex_Eqlzr_SetLeftGain`, `vortex_Eqlzr_SetRightGain`, `vortex_Eqlzr_SetAllBands`, `vortex_Eqlzr_SetBypass`, `vortex_Eqlzr_ReadAndSetActiveCoefSet`, `vortex_Eqlzr_GetAllPeaks`, `vortex_Eqlzr_init`, and `vortex_Eqlzr_shutdown`. ALSA-facing entry points are `vortex_eq_init`, `vortex_eq_free`, and the `snd_vortex_eq*`/`snd_vortex_peaks*` callbacks.

## Control Flow
`vortex_core_init()` calls `vortex_eq_init()` on supported chips. That initializes logical state, zeroes hardware, programs sample rate and normal coefficients, sets bypass state, clears A3D bypass gain, enables hardware, and registers ALSA controls. Playback routes in `vortex_connect_codecplay()` route front mixer outputs through EQ before AC97 codec outputs. ALSA band writes update `eq->this130` and, when not bypassed, immediately write target gain registers. EQ enable toggles call `vortex_Eqlzr_SetBypass()`, which switches between active gains and bypass gains. Shutdown programs pass-through and disables the EQ.

## State And Persistence
Runtime state is `vortex->eq`, including filter count, bypass flags, current gain array, active coefficient set, and A3D bypass gains. Hardware state is fully volatile MMIO and rewritten on init, control writes, bypass changes, and shutdown. No user EQ settings persist across unload.

## Dependencies And Integration Points
The file includes `au88x0.h`, `au88x0_eq.h`, and `au88x0_eqdata.c` directly. It integrates with ALSA control core and with core route setup through EQ ADB endpoints `ADB_EQIN`/`ADB_EQOUT`.

## Risks
The code has many magic register offsets and comments noting untested peak visualization and A3D bypass. `vortex_eq_free()` does not remove the created controls and comments mention old segfault risk. `sign_invert()` special-cases `-32768`; coefficient polarity mistakes would alter audio. Band labels include embedded `\0` terminators. Peak getter returns `-1` instead of a conventional negative errno. The EQ data size `eq_gains_current[12]` is larger than the ten-band loop uses, suggesting reverse-engineered padding.

## Test Signals
Expected signals are creation of one EQ enable control, ten band volume controls, and one volatile peak control; audible bypass/enable behavior; stable playback routed through EQ; peak values changing during playback; and no register/IRQ errors during repeated EQ updates.
