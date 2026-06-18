# Research: subset-b-006387

Grouped research for the au88x0 Aureal Vortex ALSA driver support files and the aw2 Audiowerk2/SAA7146 driver files. Each section preserves the original source path and is bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3d.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3d.h -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3d.h

## Purpose
Defines the Aureal A3D register map, array sizes, ALSA control ID constants, and `a3dsrc_t` per-source state used by `au88x0_a3d.c`. It is a private driver header for the A3D block.

## Important APIs, Types, And Functions
The central type is `a3dsrc_t`, containing the parent `vortex` pointer, source/slice indices, two HRTF arrays, ITD/ILD arrays, ITD delay line, and atmospheric filter parameters. Type aliases include `a3d_Hrtf_t`, `a3d_ItdDline_t`, `a3d_atmos_t`, `a3d_LRGains_t`, `a3d_Itd_t`, and `a3d_Ild_t`. The register constants cover A and B source banks, slice VDB source/destination tables, slice control, and pointer registers. Address macros `a3d_addrA`, `a3d_addrB`, and `a3d_addrS` encode the slice/source register geometry.

## Control Flow
This header has no executable control flow. It drives all address arithmetic in the implementation: source setters combine `slice`, `source`, and a register constant to issue MMIO writes. The `CTRLID_*` constants are assigned to ALSA control `numid` fields during A3D control registration.

## State And Persistence
`a3dsrc_t` is allocated as part of the runtime `vortex_t` device structure. All fields are volatile driver state and are rebuilt on hardware init. The macro-defined register offsets describe persistent hardware address layout, not persistent data.

## Dependencies And Integration Points
The header expects kernel integer types to be available via including translation units. It is consumed by A3D implementation, core init, and any code that needs the `a3dsrc_t` shape inside `vortex_t`.

## Risks
The address macros rely on undocumented source/slice strides from reverse engineering. Comments note uncertain source sizes (`0x3A4`, `0x2C8`) and dangerous debug registers. Control IDs are not namespaced beyond this driver and are assigned directly to `id.numid`, which is unusual for ALSA controls.

## Test Signals
Build coverage should catch type and macro users. Runtime validation is indirect: A3D register writes must land in the expected source/slice, and all 16 sources should initialize without corrupting adjacent hardware blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3ddata.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3ddata.c

## Purpose
Provides constant A3D initialization data: zero, impulse, all-ones, saturation-test, delayed-impulse HRTF arrays, a zero ITD delay line, and default tracking time constants.

## Important APIs, Types, And Functions
The file defines data only. Used constants include `A3dHrirZeros`, `A3dHrirImpulse`, `A3dItdDlineZeros`, `GainTCDefault`, `ItdTCDefault`, `HrtfTCDefault`, and `CoefTCDefault`. Other arrays are marked `__maybe_unused` for experiments and diagnostics.

## Control Flow
There is no executable control flow. `au88x0_a3d.c` includes this `.c` file directly and consumes the arrays during reset and pass-through programming. `A3dHrirImpulse` creates an identity-like pass-through HRTF in `a3dsrc_ProgramPipe()`.

## State And Persistence
All objects are static constants in the compiled module. They do not change at runtime and are copied only by MMIO programming routines.

## Dependencies And Integration Points
The data depends on A3D typedefs from `au88x0_a3d.h`; it is not a standalone compilation unit in normal build flow. Integration is direct textual inclusion into `au88x0_a3d.c`.

## Risks
Directly including a `.c` data file couples declaration order tightly. Several constants are experimental and unused. The correctness of the HRTF and time-constant values is hardware-specific and not self-validating.

## Test Signals
Build should verify array dimensions match `HRTF_SZ` and `DLINE_SZ`. Runtime signal is successful A3D reset/pass-through without saturation, silence, or channel inversion when the impulse set is programmed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_a3ddata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_core.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_core.c

## Purpose
Contains the low-level Aureal Vortex hardware engine: mixer, sample-rate converters, FIFO control, ADB and WT DMA setup, ADB route graph, codec access, SPDIF setup, interrupt handling, resource management, and top-level core init/shutdown. Most routines are reverse-engineered from Aureal binary drivers and are internal to the au88x0 driver.

## Important APIs, Types, And Functions
Mixer functions manage input/output gains and route tables: `vortex_mix_setvolumebyte`, `vortex_mix_setinputvolumebyte`, `vortex_mix_enableinput`, `vortex_mix_disableinput`, `vortex_mixer_addWTD`, `vortex_mixer_delWTD`, and `vortex_mixer_init`. SRC functions include `vortex_src_setupchannel`, `vortex_src_addWTD`, `vortex_src_delWTD`, and `vortex_adb_setsrc`. FIFO/DMA functions include `vortex_fifo_setadbctrl`, `vortex_fifo_setwtctrl`, `vortex_adbdma_setbuffers`, `vortex_adbdma_setmode`, `vortex_adbdma_bufshift`, `vortex_adbdma_getlinearpos`, and equivalent WT DMA helpers. Routing/resource functions include `vortex_adb_init`, `vortex_route`, `vortex_routeLRT`, `vortex_connection_*`, `vortex_adb_checkinout`, `vortex_connect_default`, and `vortex_adb_allocroute`. Device lifecycle functions are `vortex_core_init`, `vortex_core_shutdown`, `vortex_interrupt`, `vortex_codec_read`, `vortex_codec_write`, `vortex_spdif_init`, and `vortex_alsafmt_aspfmt`.

## Control Flow
Probe code outside this file calls `vortex_core_init()`, which resets the chip, initializes the AC97 codec bus, clears IRQ state, initializes ADB DMA/FIFO/mixer/SRC blocks, programs EQ/SPDIF/A3D/WT where supported, sets the timer period, and initializes the spinlock. Default playback/capture/SPDIF/WT/A3D routes are created later through `vortex_connect_default()`. PCM hw_params calls `vortex_adb_allocroute()` to allocate DMA/SRC/mixer/A3D resources and install routes. PCM prepare calls `vortex_adbdma_setmode()` and `vortex_adb_setsrc()`. PCM trigger uses the FIFO start/pause/resume/stop helpers. IRQ handling acknowledges Vortex IRQ source bits, reports hardware errors, advances active DMA windows with `vortex_adbdma_bufshift()`/`vortex_wtdma_bufshift()`, and calls `snd_pcm_period_elapsed()`.

## State And Persistence
Driver state lives in `vortex_t` stream arrays (`dma_adb`, `dma_wt`), fixed resource bitmaps, mixer IDs, period tracking fields, SPDIF rate, codec pointer, and spinlock. Static `mchannels` and `rampchs` track mixer input enables across the driver instance and are reset by `vortex_mixer_init()`. DMA routines maintain virtual/real period positions and page-table refresh state for buffers with more than four periods. All state is volatile and rebuilt after init; MMIO state is explicitly cleared during shutdown.

## Dependencies And Integration Points
This file depends on `au88x0.h` for register constants, macros, `vortex_t`, `stream_t`, resource IDs, chip feature macros, and `hwwrite`/`hwread`. It also calls EQ, A3D, WT, ALSA AC97, ALSA PCM, MPU401, and kernel IRQ APIs. PCM, mixer, gameport, MIDI, and synth files rely on its static helpers because the driver is built by including implementation fragments.

## Risks
The resource allocator has complex rollback paths; several failure branches clear resource bitmaps without undoing routes already installed. DMA page shifting assumes hardware subbuffer reporting and powers-of-two period sizes; off-by-one errors would surface as period skips or stale DMA addresses. `mchannels`/`rampchs` are static globals, so multiple cards may share mixer bookkeeping. Many magic constants and chip-specific `#ifdef`s are reverse-engineered. IRQ handling calls period callbacks while temporarily dropping the spinlock; stream teardown races must be controlled by ALSA lifecycle locks. Codec polling has finite lifeboat loops and returns `0xffff` on read failure.

## Test Signals
Core tests require real or emulated AU88x0 hardware: init/shutdown without IRQ storms, AC97 read/write success, playback/capture at supported rates, SPDIF rate changes, quad-output routing, A3D/WT route allocation, and MIDI interrupts. Stress useful signals include long playback with many periods, simultaneous capture/playback, open/close churn, and no `lifeboat overflow`, `Src cvr fail`, FIFO, DMA, or fatal IRQ errors in dmesg.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eq.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eq.h -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eq.h

## Purpose
Defines private data structures for the AU88x0 hardware equalizer implementation.

## Important APIs, Types, And Functions
`auxxEqCoeffSet_t` stores left/right coefficient arrays and left/right gain arrays. `eqhw_t` stores hardware filter count and a coefficient sign/polarity flag. `eqlzr_t` wraps hardware state, bypass gain fields, band count, bypass flag, A3D bypass factors, active coefficient set, and the 20-value left/right gain cache.

## Control Flow
This header has no executable flow. `au88x0_eq.c` initializes and mutates the fields while programming registers and serving ALSA control callbacks.

## State And Persistence
Instances live inside `vortex_t` and are reset by `vortex_Eqlzr_init()`. Settings are in-memory only and not persisted across reloads.

## Dependencies And Integration Points
Depends on kernel integer typedefs from including files. It is tightly coupled to the reverse-engineered field naming in `au88x0_eq.c`.

## Risks
Field names such as `this04`, `this28`, and `this54` reflect translated binary layouts and obscure semantics. The structure layout is not hardware ABI, but mistaken interpretation can lead to wrong register programming or user control behavior.

## Test Signals
Build coverage verifies all fields used by the EQ implementation. Runtime tests for EQ enable, band gain changes, and peak readings exercise the structure state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eqdata.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eqdata.c

## Purpose
Provides static equalizer coefficient, gain, state, and peak-level initializer data consumed by `au88x0_eq.c`.

## Important APIs, Types, And Functions
Data includes `asEqCoefsZeros`, `asEqCoefsPipes`, `asEqCoefsNormal`, `eq_gains_normal`, `eq_gains_zero`, `eq_gains_current`, `eq_states_zero`, `asEqOutStateZeros`, and `eq_levels`. There are no functions.

## Control Flow
No executable flow. EQ init and reset copy these arrays into MMIO through the EQ hardware writer functions. `asEqCoefsNormal` is selected as the active ten-band coefficient set.

## State And Persistence
All arrays are static constants in module memory. They are immutable and serve as templates for volatile hardware programming.

## Dependencies And Integration Points
Depends on `auxxEqCoeffSet_t` from `au88x0_eq.h` and is directly included by `au88x0_eq.c`, not compiled independently.

## Risks
Coefficient correctness is entirely data-driven and hardware-specific. Comments point to additional coefficient sets in old Windows INF material, so this file likely represents one fixed profile. Array length mismatches would cause hardware programming beyond intended bands, but current loops are bounded by `eqhw->this04`.

## Test Signals
Successful EQ init, pass-through programming, and normal EQ behavior are the primary signals. Static analysis/build checks should confirm array initializers match declared sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_eqdata.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_game.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_game.c

## Purpose
Adds optional Linux gameport support for AU88x0 cards when `CONFIG_GAMEPORT` is reachable. It is based on old PCI gameport logic and maps joystick read/trigger/cooked mode operations to Vortex legacy game registers.

## Important APIs, Types, And Functions
Core callbacks are `vortex_game_read`, `vortex_game_trigger`, `vortex_game_cooked_read`, and `vortex_game_open`. Lifecycle helpers are `vortex_gameport_register` and `vortex_gameport_unregister`, with inline `-ENOSYS`/no-op stubs when gameport support is unavailable.

## Control Flow
Registration allocates a `struct gameport`, names it, attaches it to the PCI device, assigns callbacks, stores `vortex_t` as port data, and registers with the input gameport layer. Open switches raw/cooked mode by toggling `CTRL2_GAME_ADCMODE`; cooked reads return buttons from `VORTEX_GAME_LEGACY` and axes from `VORTEX_GAME_AXIS`.

## State And Persistence
State is `vortex->gameport` plus hardware ADC mode bits. It is cleaned by unregistering the port and setting the pointer to NULL. No persistent configuration exists.

## Dependencies And Integration Points
Depends on `linux/gameport.h`, PCI device data, Vortex MMIO macros, and register constants in `au88x0.h`. It integrates with the wider card probe/remove path through the static lifecycle helpers.

## Risks
This is legacy functionality and may be untested on modern kernels/hardware. `vortex_game_open()` returns `-1` instead of a specific errno for unsupported modes. Cooked axis values map `AXIS_RANGE` to `-1`, so hardware interpretation must match the input subsystem expectations.

## Test Signals
When enabled, `/sys`/input should show an AU88x0 gameport, raw and cooked reads should respond to joystick movement/buttons, and unregister should remove the port without use-after-free warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_game.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_mixer.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_mixer.c

## Purpose
Creates the ALSA AC97 mixer bus for the Vortex codec and performs small control cleanup after mixer creation.

## Important APIs, Types, And Functions
`remove_ctl()` removes named mixer controls by building a `snd_ctl_elem_id`. `snd_vortex_mixer()` creates an AC97 bus using `vortex_codec_write`/`vortex_codec_read`, instantiates the AC97 mixer, stores `vortex->codec`, detects quad support from the codec extended ID, and removes mono master controls.

## Control Flow
Probe code calls `snd_vortex_mixer()`. It creates an AC97 bus, zeroes an AC97 template, sets `private_data` to `vortex`, disables AC97 SPDIF capability in `scaps`, creates the AC97 mixer, updates `vortex->isquad`, and removes two unwanted controls.

## State And Persistence
Runtime state is `vortex->codec` and `vortex->isquad`. ALSA controls live on the card and are removed with card teardown. There is no persistence beyond ALSA mixer state.

## Dependencies And Integration Points
Depends on core codec accessors from `au88x0_core.c`, ALSA AC97 APIs, and `au88x0.h`. Quad detection affects PCM channel constraints and routing in other files.

## Risks
`remove_ctl()` ignores missing-control errors, which is acceptable cleanup but can hide unexpected mixer topology changes. `vortex->isquad` is set to zero if mixer creation leaves codec NULL; route/channel behavior depends on this flag.

## Test Signals
Expected signals are AC97 mixer creation, usable playback/capture mixer controls, absent mono master controls, and correct quad/stereo channel limits based on codec capabilities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_mixer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_mpu401.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_mpu401.c

## Purpose
Initializes the Vortex integrated MPU-401 UART MIDI interface, either via legacy I/O port fallback or native MMIO support when `MPU401_HW_AUREAL` is available.

## Important APIs, Types, And Functions
The only active entry point is `snd_vortex_midi(vortex_t *vortex)`. It programs `VORTEX_CTRL`, `VORTEX_CTRL2`, `VORTEX_MIDI_CMD`, and `VORTEX_IRQ_CTRL`, validates `MPU401_ACK`, creates an ALSA rawmidi device via `snd_mpu401_uart_new`, and stores it in `vortex->rmidi`.

## Control Flow
The function enables or disables the legacy MIDI port depending on compile-time support, sets the MIDI clock divisor and UART mode, sends reset, reads the ACK byte, enables MIDI interrupts, creates the MPU401 ALSA device, sets native command port for MMIO mode, names the rawmidi device, and returns success/failure.

## State And Persistence
Runtime state is hardware MIDI enable bits, IRQ enable bits, and `vortex->rmidi`. No MIDI settings persist across unload. On `snd_mpu401_uart_new()` failure, MIDI hardware enable is rolled back.

## Dependencies And Integration Points
Depends on ALSA rawmidi/MPU401 helpers, core interrupt handling (`vortex_interrupt()` dispatches `IRQ_MIDI` to `snd_mpu401_uart_interrupt()`), and Vortex register constants.

## Risks
Legacy mode hardcodes port `0x330`, with comments discouraging use. Failure to receive ACK aborts MIDI setup. IRQ enable is shared with core interrupt configuration; ordering must ensure Vortex interrupts are enabled globally.

## Test Signals
Successful rawmidi device creation, ACK during init, MIDI input/output through ALSA sequencer/rawmidi tools, and IRQ_MIDI dispatch without interrupt storms are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_mpu401.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_pcm.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_pcm.c

## Purpose
Implements ALSA PCM devices for AU88x0 playback/capture paths: ADB analog PCM, SPDIF, A3D, WT, and I2S names. It maps ALSA hw_params/prepare/trigger/pointer callbacks to core DMA, route, SRC, FIFO, and mixer-volume helpers.

## Important APIs, Types, And Functions
Hardware descriptors are `snd_vortex_playback_hw_adb`, `snd_vortex_playback_hw_a3d`, `snd_vortex_playback_hw_spdif`, and `snd_vortex_playback_hw_wt`. ALSA PCM callbacks are `snd_vortex_pcm_open`, `snd_vortex_pcm_close`, `snd_vortex_pcm_hw_params`, `snd_vortex_pcm_hw_free`, `snd_vortex_pcm_prepare`, `snd_vortex_pcm_trigger`, and `snd_vortex_pcm_pointer`. Control callbacks include SPDIF status get/put/mask and per-subdevice PCM volume get/put/info. `snd_vortex_new_pcm()` creates PCM devices, chmaps, SPDIF controls, and per-subdevice volume controls.

## Control Flow
On open, the code applies integer/power-of-two/step constraints and chooses a hardware descriptor based on a stored PCM type byte. hw_params allocates or reallocates ADB/WT routes, configures DMA buffers, and activates PCM volume controls for ADB streams. prepare maps ALSA format to Vortex format, writes DMA mode/start buffer, and sets SRC rate except for SPDIF. trigger starts/stops/pauses/resumes the relevant FIFO. pointer reads core DMA position and converts bytes to frames. Control writes update SPDIF sample rate via `vortex_spdif_init()` or active playback mixer input gains.

## State And Persistence
State is in each `stream_t`, `substream->runtime->private_data`, `vortex->pcm[]`, `vortex->pcm_vol[]`, `vortex->spdif_sr`, and core route/DMA structures. PCM volume values remain in memory while the card exists but are not persisted by this driver. The PCM type is stored in `pcm->name[40]`, a deliberate private hack.

## Dependencies And Integration Points
Depends heavily on core helpers in `au88x0_core.c` and WT helpers in `au88x0_synth.c`, plus ALSA PCM/control/chmap APIs and `snd_pcm_set_managed_buffer_all`. Interrupt period completion is handled in core IRQ code.

## Risks
Using `pcm->name[40]` for the PCM type is fragile and depends on `struct snd_pcm` name storage. The same ops are used for capture and playback, with direction handled at runtime. WT support is explicitly marked not fully working. SPDIF open constrains rates to `vortex->spdif_sr`, and changing SPDIF control while streams are active could conflict with runtime constraints. pointer wraps to zero if beyond buffer size, which may mask bad hardware positions.

## Test Signals
ALSA should expose expected PCM devices and controls. Playback/capture should work with allowed formats, rates, channels, and period sizes; ADB quad channel constraints should apply on AU8830; SPDIF control changes should update accepted rates; per-subdevice PCM volume controls should become active only while a stream is allocated; long-running playback should have stable period elapsed callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_synth.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_synth.c

## Purpose
Programs the Vortex wavetable (WT) engine and route connections. The file notes that the WT DMA engine was intended for wavetable synthesis and remains incomplete/problematic for actual DMA playback.

## Important APIs, Types, And Functions
Key helpers are `vortex_wt_setstereo`, `vortex_wt_setdsout`, `vortex_wt_allocroute`, `vortex_wt_connect`, `vortex_wt_SetReg`, and `vortex_wt_init`. Disabled experimental helpers include WT register reads, volume programming, and frequency conversion.

## Control Flow
`vortex_core_init()` calls `vortex_wt_init()` on non-AU8810 chips to initialize bank and voice registers. `vortex_connect_default()` calls `vortex_wt_connect()` to allocate fixed mixer inputs, route WT outputs to playback mixers, and mark WT voices running. PCM hw_params for WT calls `vortex_wt_allocroute()`, which initializes the WT FIFO, marks it valid, sets stereo mode, enables mixdown, writes ramp/parameter/delay registers, and stores initial voice parameter values.

## State And Persistence
State is MMIO WT registers plus `vortex->wt_voice[]`, `vortex->mixwt[]`, and WT DMA stream state in core. It is volatile and reset on driver init. Voice parameters `parm0` and `parm1` are cached in `wt_voice_t`.

## Dependencies And Integration Points
Depends on `au88x0_wt.h` register macros, core FIFO functions, ADB route helpers, mixer connections, and `vortex_adb_checkinout`. PCM WT support in `au88x0_pcm.c` invokes this route allocator and core WT DMA routines.

## Risks
Comments state WT channels do not run yet and DMA transfers remain stuck. Many WT parameters are magic constants from reverse engineering. `vortex_wt_SetReg()` has bank/voice range checks that differ by register ID; wrong IDs can silently return zero. Route setup is fixed and may not reflect real wavetable synthesis semantics.

## Test Signals
Build and probe should initialize WT without register errors. If tested on hardware, WT PCM open/hw_params/trigger should not hang the system, and any WT playback attempt should be watched for stuck FIFO, missing IRQs, or no audio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_synth.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_wt.h -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_wt.h

## Purpose
Defines register address macros and voice state for the AU88x0 wavetable engine.

## Important APIs, Types, And Functions
Macros include `NR_WT_PB`, `WT_BAR`, `WT_BANK`, bank registers `WT_CTRL`, `WT_SRAMP`, `WT_DSREG`, `WT_MRAMP`, `WT_GMODE`, `WT_ARAMP`, and voice registers `WT_STEREO`, `WT_MUTE`, `WT_RUN`, `WT_PARM`, and `WT_DELAY`. The parameter enum names `param0` through `delay`. `wt_voice_t` caches four WT parameter words.

## Control Flow
No executable flow. `au88x0_synth.c` uses these macros to calculate MMIO addresses for all WT initialization, routing, and register writes.

## State And Persistence
`wt_voice_t` state lives in `vortex_t`; register macros target volatile hardware state. No persistent storage exists.

## Dependencies And Integration Points
Consumed by WT/synth code and indirectly by PCM WT setup. It assumes `NR_WT` and Vortex MMIO access exist in the including environment.

## Risks
Address macros encode bank and voice layout through shifts and masks; mistakes would corrupt adjacent WT or FIFO registers. The header has no validation for voice range, leaving checks to callers such as `vortex_wt_SetReg()`.

## Test Signals
Compile coverage and successful WT init are the main signals. Runtime validation requires WT register writes to affect expected voices/banks and not interfere with ADB playback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_wt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_xtalk.c -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_xtalk.c

## Purpose
Programs the AU88x0 crosstalk cancellation block used by A3D output. It contains coefficient tables for pipe, wide, narrow, and Diamond speaker modes, and writes EQ/XT filters, gains, delays, delay lines, state, sample rate, and enable bits.

## Important APIs, Types, And Functions
Static data includes mode-specific coefficient/gain/delay constants. Hardware writers include `vortex_XtalkHw_SetLeftEQ`, `vortex_XtalkHw_SetRightEQ`, `vortex_XtalkHw_SetLeftXT`, `vortex_XtalkHw_SetRightXT`, state setters, `vortex_XtalkHw_SetGains`, `vortex_XtalkHw_SetDelay`, delay-line setters, `vortex_XtalkHw_SetSampleRate`, `vortex_XtalkHw_Enable`, `vortex_XtalkHw_Disable`, `vortex_XtalkHw_ZeroIO`, `vortex_XtalkHw_ZeroState`, and mode program functions `vortex_XtalkHw_ProgramPipe`, `vortex_XtalkHw_ProgramXtalkWide`, `vortex_XtalkHw_ProgramXtalkNarrow`, `vortex_XtalkHw_ProgramDiamondXtalk`, plus `vortex_XtalkHw_init`.

## Control Flow
A3D initialization calls `vortex_XtalkHw_init()`, `vortex_XtalkHw_SetGainsAllChan()`, a mode-specific programming helper based on `v->xt_mode`, `vortex_XtalkHw_SetSampleRate()`, and `vortex_XtalkHw_Enable()`. A3D shutdown disables the block. Hardware programming is direct MMIO writes over dense coefficient arrays and fixed register offsets.

## State And Persistence
All coefficient tables are static constants. Runtime XTALK state is only in hardware registers and `vortex->xt_mode`; it is zeroed and reprogrammed on A3D initialization. No user persistence exists.

## Dependencies And Integration Points
Depends on `au88x0_xtalk.h`, `au88x0.h`, and MMIO helpers. Integrated through `au88x0_a3d.c`, where XTALK output is routed to playback mixers.

## Risks
The file is dominated by magic coefficients and offsets; audio correctness depends on undocumented hardware behavior. Some right-channel constants exist but are unused, and right XT programming often reuses left-XT data. `vortex_XtalkHw_ZeroState()` writes delay lines twice. Readback helpers are disabled, making runtime verification harder.

## Test Signals
A3D playback through XTALK should be audible in pipe/headphone mode and should change spatial character in speaker/diamond modes. Dmesg should remain clean during A3D enable/disable. A hardware register trace or audible test can validate sample-rate and delay programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_xtalk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_xtalk.h -->
# sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_xtalk.h

## Purpose
Declares XTALK constants, array typedefs, output mode IDs, and static function prototypes for the crosstalk hardware implementation.

## Important APIs, Types, And Functions
Defines `XTDLINE_SZ`, `XTGAINS_SZ`, `XTINST_SZ`, mode IDs `XT_HEADPHONE`, `XT_SPEAKER0`, `XT_SPEAKER1`, and `XT_DIAMOND`, and array types `xtalk_dline_t`, `xtalk_gains_t`, `xtalk_instate_t`, `xtalk_coefs_t`, and `xtalk_state_t`. It also declares static XTALK programming helpers consumed by the same compilation unit pattern.

## Control Flow
No executable flow. The prototypes let A3D code call XTALK helpers when implementation fragments are composed together.

## State And Persistence
Only type and constant definitions. Runtime state is held in the implementation and hardware registers.

## Dependencies And Integration Points
Includes `au88x0.h` for `vortex_t` and integer types. Used by `au88x0_xtalk.c` and `au88x0_a3d.c`.

## Risks
The header has duplicate `vortex_XtalkHw_ProgramPipe()` declarations. All declared functions are `static`, reflecting a nonstandard include/compilation model; if build organization changes, linkage would need cleanup.

## Test Signals
Build coverage confirms prototype consistency. Runtime signals are indirect through A3D/XTALK initialization and playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/au88x0/au88x0_xtalk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/Makefile -->
# sources/distributed-fs/ceph-client/sound/pci/aw2/Makefile

## Purpose
Defines the kernel build objects for the Audiowerk2 ALSA driver.

## Important APIs, Types, And Functions
No code APIs. It sets `snd-aw2-y := aw2-alsa.o aw2-saa7146.o` and adds `snd-aw2.o` to `obj-$(CONFIG_SND_AW2)`.

## Control Flow
Kbuild compiles the ALSA module from the top-level ALSA wrapper and the SAA7146 helper when `CONFIG_SND_AW2` is enabled. `aw2-tsl.c` is not listed because it is included directly by `aw2-saa7146.c`.

## State And Persistence
No runtime state. Build configuration determines whether the module exists.

## Dependencies And Integration Points
Depends on the kernel ALSA PCI Kconfig selecting `CONFIG_SND_AW2` and on the two object files resolving each other's symbols.

## Risks
Because `aw2-tsl.c` is textually included, adding it to the object list would duplicate definitions. Missing either object would break module linkage.

## Test Signals
`make M=sound/pci/aw2` or full kernel builds with `CONFIG_SND_AW2=m/y` should produce `snd-aw2.o`/module without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-alsa.c -->
# sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-alsa.c

## Purpose
Provides the ALSA PCI driver wrapper for Emagic Audiowerk2 cards based on the Philips SAA7146. It handles module parameters, PCI probe, card allocation, IRQ setup, PCM device creation, PCM callbacks, and a capture route mixer control.

## Important APIs, Types, And Functions
Private structures are `aw2_pcm_device` and `aw2`. Module data includes `index`, `id`, `enable`, `snd_aw2_ids`, and `aw2_driver`. Lifecycle functions include `snd_aw2_free`, `snd_aw2_create`, and `snd_aw2_probe`. PCM callbacks include open/close/prepare/trigger/pointer for playback and capture. `snd_aw2_new_pcm()` creates analog playback, digital playback, and capture PCMs. Mixer control callbacks are `snd_aw2_control_switch_capture_info`, `get`, and `put`.

## Control Flow
`module_pci_driver()` registers `aw2_driver`. On matching SAA7146 PCI ID, probe checks card enablement, allocates a devm ALSA card, initializes PCI/MMIO/IRQ through `snd_aw2_create()`, sets names and locks, creates three PCM devices plus the capture route control, registers the card, and stores driver data. PCM prepare locks `chip->mtx`, computes period/buffer bytes, programs SAA7146 DMA, and installs period callbacks. Trigger locks `reg_lock` and starts/stops the selected SAA7146 stream. Pointer reads the helper-reported hardware byte position and converts to frames. Capture route control toggles SAA7146 GPIO between analog and digital input.

## State And Persistence
Runtime state is in `struct aw2`: embedded SAA7146 state, PCI/MMIO pointers, IRQ number, locks, ALSA card, and PCM device descriptors. ALSA runtime DMA buffers are managed by the PCM core. No driver-specific settings persist; capture route is reflected in GPIO state only.

## Dependencies And Integration Points
Depends on kernel PCI, DMA, IRQ, MMIO, module, ALSA core/PCM/control APIs, `saa7146.h`, and `aw2-saa7146.h`. It delegates all hardware register work to `aw2-saa7146.c`.

## Risks
The PCI ID matches generic Philips SAA7146 vendor/device without subsystem filtering, so probe could bind non-Audiowerk2 SAA7146 hardware if Kconfig/device matching is broad. `snd_aw2_new_pcm()` return is ignored in probe, so PCM creation failure may not abort card registration. Capture control variable is misspelled `is_disgital` but behavior is clear. The ALSA hardware descriptors require 44.1 kHz and continuous DMA buffers; unsupported runtime combinations should be rejected by ALSA constraints.

## Test Signals
Expected signals include successful probe only on real Audiowerk2 hardware, three PCM devices with correct names, 44.1 kHz S16_LE playback/capture, period callbacks on all streams, capture route control switching, and clean devm cleanup on unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-alsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-saa7146.c -->
# sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-saa7146.c

## Purpose
Implements the Audiowerk2-specific SAA7146 hardware programming layer: setup/reset, DMA base/limit programming, start/stop triggers, IRQ dispatch to ALSA period callbacks, hardware pointer calculation, and analog/digital capture input switching.

## Important APIs, Types, And Functions
Public functions include `snd_aw2_saa7146_setup`, `snd_aw2_saa7146_free`, `snd_aw2_saa7146_pcm_init_playback`, `snd_aw2_saa7146_pcm_init_capture`, callback registration helpers, playback/capture trigger start/stop helpers, `snd_aw2_saa7146_interrupt`, pointer getters, `snd_aw2_saa7146_use_digital_input`, and `snd_aw2_saa7146_is_using_digital_input`. Internal state consists of global callback arrays for playback and capture streams. Register access uses `WRITEREG` and `READREG` macros over `chip->base_addr`.

## Control Flow
Setup disables IRQs, resets the chip, configures audio port word-selects and endian swaps, writes PCI burst/threshold settings, enables audio pins/I2C/interrupts, configures ACON2, selects analog input by default, and writes TSL tables. PCM prepare calls the init functions, which disable the SAA7146 MMU, compute a DMA limit exponent from period size, write Page/Base/Prot registers for A2/A1 playback or A1 capture, and leave transfer start to trigger. Trigger functions set/clear MC1 transfer-enable bits and update ACON1 word-select output bits. IRQ handler checks ISR, acknowledges bits, clears I2C status, and invokes registered period callbacks for A1_out, A2_out, and A1_in. Pointer getters subtract ALSA buffer start from current PCI adapter pointer and wrap exact end to zero.

## State And Persistence
`chip->base_addr` is the only per-device field in `struct snd_aw2_saa7146`. Period callbacks are stored in file-scope arrays, not in the chip, so they are shared across devices. Hardware state is volatile SAA7146 registers. Input route is stored only in GPIO low byte.

## Dependencies And Integration Points
Depends on `saa7146.h` register/bit definitions, included `aw2-tsl.c` TSL arrays, ALSA PCM period callback type, and the `aw2-alsa.c` wrapper for locking, IRQ request, and runtime DMA addresses.

## Risks
Global callback arrays are unsafe for multiple cards and can retain stale substream pointers if streams close without clearing callbacks. Pointer calculation subtracts a CPU virtual DMA area pointer (`runtime->dma_area`) from PCI adapter register values in the caller path, while DMA programming used physical `runtime->dma_addr`; this looks suspicious and may report wrong positions on some architectures. Input switching has an explicit FIXME for white-noise/synchronization issues. IRQ handler always returns `IRQ_HANDLED` for any nonzero ISR even if no known audio bit was serviced. `snd_aw2_saa7146_get_limit()` does not cap the value to documented hardware maximum.

## Test Signals
Hardware tests should verify all three streams generate period interrupts, pointers are monotonic and wrap correctly, simultaneous playback/capture works, digital/analog input switching is stable, no stale callback fires after close, and teardown disables IRQs/reset without interrupt-after-free warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-saa7146.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-saa7146.h -->
# sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-saa7146.h

## Purpose
Declares the Audiowerk2 SAA7146 helper interface used by the ALSA wrapper.

## Important APIs, Types, And Functions
Defines stream counts and stream IDs for two playback streams and one capture stream. Declares `snd_aw2_saa7146_it_cb`, `snd_aw2_saa7146_cb_param`, and `struct snd_aw2_saa7146` with `base_addr`. Prototypes cover setup/free, PCM init, callback registration, trigger start/stop, IRQ handler, pointer getters, and digital-input controls.

## Control Flow
No executable flow. It defines the contract between `aw2-alsa.c` and `aw2-saa7146.c`: ALSA prepares streams, registers callbacks, triggers transfers, and queries pointers through this API.

## State And Persistence
The only declared device state is MMIO base address. Callback state is declared in the `.c` file rather than this structure. No persistence.

## Dependencies And Integration Points
Requires `struct snd_pcm_substream` forward declaration and kernel MMIO pointer types. It is private to the aw2 driver.

## Risks
The minimal device struct makes helper-global callback arrays more likely, limiting multi-card safety. API uses `unsigned long` for DMA addresses and sizes, while ALSA/kernel DMA types may be more precise on some architectures.

## Test Signals
Build coverage verifies callers match prototypes. Runtime tests through the ALSA wrapper validate the helper contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-saa7146.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-tsl.c -->
# sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-tsl.c

## Purpose
Defines SAA7146 Time Slot List bit constants and two eight-entry TSL programs for Audiowerk audio routing/timing.

## Important APIs, Types, And Functions
Bit macros encode word-select outputs, A1/A2 disable/data-width/bit-select/frame/last-frame/data-output-delay/low/EOS fields. `tsl1[8]` programs analog/digital input and analog/digital output timing for A1, and `tsl2[8]` programs A2 output timing.

## Control Flow
No functions. `aw2-saa7146.c` includes this file and writes `tsl1[i]` to `TSL1 + i*4` and `tsl2[i]` to `TSL2 + i*4` during setup.

## State And Persistence
Static const arrays are immutable module data. Runtime hardware TSL registers are volatile and loaded on setup.

## Dependencies And Integration Points
Integrated by textual inclusion into `aw2-saa7146.c`; it relies on SAA7146 register definitions from the including file context for where arrays are written.

## Risks
The comments mention Audiowerk8 setup while this driver targets Audiowerk2, implying reused timing knowledge. TSL values are low-level hardware timing data; small mistakes can produce channel swaps, silence, or corrupted I2S timing.

## Test Signals
Audio channel mapping is the key signal: analog and digital playback/capture should use the expected left/right slots at 44.1 kHz, with no word-select phase errors or channel swaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/aw2-tsl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/saa7146.h -->
# sources/distributed-fs/ceph-client/sound/pci/aw2/saa7146.h

## Purpose
Provides SAA7146 register offsets and bit definitions used by the Audiowerk2 hardware helper.

## Important APIs, Types, And Functions
Defines register offsets for PCI burst threshold, I2C, A1/A2 input/output DMA base/protect/page, IRQ enable/status, GPIO, audio config, main control, PCI adapter pointers, level reporting, frame buffers, and TSL memory. Bit groups cover PSR/ISR/IER, SSR, PCI burst/threshold, MC1/MC2, ACON1/ACON2, IICSTA/IICTFR, and I2C operation codes.

## Control Flow
No executable flow. Constants are consumed by `aw2-saa7146.c` for MMIO reads/writes.

## State And Persistence
The header models hardware register layout only. Runtime state resides in SAA7146 registers and driver structures.

## Dependencies And Integration Points
Private to the aw2 driver. It must match Philips SAA7146 documentation and the Audiowerk2 board wiring assumed by `aw2-saa7146.c` and `aw2-tsl.c`.

## Risks
`ERR` and `BUSY` are defined in both IICSTA and IICTFR sections, creating macro redefinition risk if compiler warnings are enabled. All constants are global preprocessor names without a prefix, which can collide if included more broadly. Incorrect bit definitions can affect DMA, IRQ, I2C, or GPIO behavior.

## Test Signals
Build without macro warning regressions, successful hardware setup, correct IRQ bit decoding, DMA pointer reads, and stable GPIO/I2C behavior during analog/digital capture switching validate this header indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/pci/aw2/saa7146.h -->
