## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs_lnl_reg.h

### Purpose
`ivpu_hw_btrs_lnl_reg.h` maps Lunar Lake/newer buttress registers and bit masks.

### Important APIs, Types, And Functions
It defines interrupt status/masks for frequency, ATS, CFI, IMR, and survivability errors; local/global interrupt masks; ATS and error log/clear registers; port arbitration weights; PCODE mailbox status/shadow; workpoint payload/command; PLL/CDYN; tile fuse; VPU status; IP reset; D0i3; telemetry; and FMIN/FMAX fuses.

### Control Flow
No executable code exists. `ivpu_hw_btrs.c` uses these constants to implement LNL-class PLL, reset, D0i3, IRQ, telemetry, tile-fuse, DCT, and platform operations.

### State, Persistence, And Dependencies
State persists in BAR4 buttress registers. The header depends on Linux bit macros and accurate LNL register offsets.

### Integration Points
It supports LNL, PTL-P, WCL, and NVL buttress flows selected by `ivpu_hw_btrs_gen()`.

### Risks
Masks are used with generic field macros; any typo changes hardware behavior. Platform, clock relinquish, and telemetry fields are consumed by firmware boot and PM, so wrong decoding propagates outside buttress code.

### Test Signals
Validate interrupt decoding, tile-fuse valid/config fields, PLL ratio reads, D0i3/IP reset polling, PCODE DCT command/status exchange, telemetry boot-param values, and platform field decoding.
