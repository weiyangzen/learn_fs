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
