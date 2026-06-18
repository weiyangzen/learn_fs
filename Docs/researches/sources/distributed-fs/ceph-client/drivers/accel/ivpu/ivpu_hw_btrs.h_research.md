## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs.h

### Purpose
`ivpu_hw_btrs.h` declares the buttress hardware API and shared constants for profiling frequency and DCT defaults.

### Important APIs, Types, And Functions
It exposes `PLL_PROFILING_FREQ_DEFAULT`, `PLL_PROFILING_FREQ_HIGH`, `DCT_DEFAULT_ACTIVE_PERCENT`, `DCT_PERIOD_US`, and prototypes for buttress info/frequency/power/reset/idle/IRQ/DCT/telemetry/diagnostic/platform functions.

### Control Flow
The header has no logic. Callers invoke these APIs through `ivpu_hw.c` or inline wrappers in `ivpu_hw.h` to perform generation-specific buttress work.

### State, Persistence, And Dependencies
State is maintained in hardware registers and `vdev->hw` by the implementation. The header depends on driver, 37xx/40xx register maps, and register I/O helpers.

### Integration Points
This is the interface boundary between common hardware orchestration and MTL/LNL buttress register programming.

### Risks
The API assumes callers have selected the correct buttress generation and that BAR4 is mapped. Constants must match firmware/PM expectations for profiling clock and DCT behavior.

### Test Signals
Compile coverage for every prototype, runtime tests of each public hook through common hardware/PM/debugfs flows, and generation selection checks.
