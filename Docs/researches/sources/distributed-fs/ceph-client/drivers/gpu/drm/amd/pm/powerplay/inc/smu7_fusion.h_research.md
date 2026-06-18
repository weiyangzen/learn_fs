# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/smu7_fusion.h

## Purpose
`smu7_fusion.h` defines SMU7 APU/fusion packed table layouts. It differs from discrete layouts by modeling shared CPU/GPU thermal entities, NB voltage, GIO/LCLK DPM, and fusion-specific clock breakdown rather than discrete memory voltage rails.

## Important APIs, Types, And Constants
- DTE dimensions are fusion-specific: 5 iterations, 5 sources, 3 sinks, 2 CPU TEs, 1 GPU TE, and 2 non-TEs.
- `SMU7_SoftRegisters` provides ref clock, PM timer, feature enables, handshake disables, display PHY configs, enabled DPM masks, log addresses, and ULV counters.
- Fusion level types include `SMU7_Fusion_GraphicsLevel`, `SMU7_Fusion_GIOLevel`, `SMU7_Fusion_UvdLevel`, `SMU7_Fusion_ExtClkLevel`, `SMU7_Fusion_ACPILevel`, `SMU7_Fusion_NbDpm`, and `SMU7_Fusion_StateInfo`.
- `SMU7_Fusion_DpmTable` contains system flags, graphics/GIO PID controllers, counts and arrays for graphics/media clocks, boot levels, intervals, graphics clock slow controls, display CAC, low-SCLK interrupt threshold, and DRAM log buffer addresses.
- `SMU7_Fusion_GIODpmTable` separately models LCLK/GIO levels, voltage changes, target/current state, thermal throttle status, and high/low temperature limits.

## Control Flow And Data Flow
Host code fills fusion DPM tables for integrated graphics and GIO, then firmware uses enabled level counts, NB voltage requirements, clock divider/bypass controls, and thermal throttle settings to select states. GIO has a separate target/current state path from graphics/media clocks.

## State And Persistence
Tables are volatile packed firmware state. There are no discrete rail fuse tables here; voltage policy centers on NB voltage and VID fields. DRAM log fields describe runtime buffers.

## Dependencies And Integration Points
- Includes `smu7.h`.
- Integrates with APU-specific powerplay code, display PHY configuration, UVD/VCE/ACP/SAMU media clock management, and NB/GIO DPM.
- Shares `SMU7_SoftRegisters` name with the discrete header but with a different layout, so the include path determines ABI.

## Risks
- Name reuse with `smu7_discrete.h` can cause accidental layout confusion.
- GIO/LCLK and NB fields have platform-specific semantics and should not be copied into discrete flows.
- Packed layout and count fields must match firmware; no runtime bounds protection is expressed here.

## Test Signals
- Compile fusion/APU configurations that include this header alone.
- Runtime: graphics and GIO DPM transitions, NB voltage changes, media clock levels, thermal throttle status, and display watermark behavior.
