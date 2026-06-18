## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs_mtl_reg.h

### Purpose
`ivpu_hw_btrs_mtl_reg.h` maps Meteor Lake/Arrow Lake buttress registers and bit masks.

### Important APIs, Types, And Functions
It defines interrupt type/status, workpoint payload/command/download/current PLL, PLL enable/status, FMIN/FMAX fuses, tile fuse/SKU, local/global interrupt masks, VPU ready/idle status, D0i3 control, IP reset, telemetry registers, ATS error logs/clear, and UFI error log/clear fields.

### Control Flow
No executable logic exists. MTL buttress implementation uses these constants for PLL workpoints, D0i3, reset, idle/frequency queries, interrupt handling, telemetry, and diagnostics.

### State, Persistence, And Dependencies
State lives in BAR4 buttress registers. The header depends on Linux bit macros and MTL register layout.

### Integration Points
It supports MTL and ARL devices selected by `ivpu_hw_btrs_gen() == IVPU_HW_BTRS_MTL`.

### Risks
MTL has an interrupt-clear-with-zero workaround detection path; status semantics must be exact. UFI/ATS error fields feed recovery decisions, so incorrect masks reduce diagnostics or miss fatal errors.

### Test Signals
Test workpoint payload programming, PLL lock/status polling, interrupt status clearing behavior, ATS/UFI error log decode, telemetry fields, and D0i3/IP reset transitions on MTL-class hardware.
