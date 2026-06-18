# sources/distributed-fs/ceph-client/drivers/misc/xilinx_tmr_inject.c

## Purpose
Platform driver for Xilinx TMR Inject IP. It programs fault-injection registers and exposes debugfs controls for MicroBlaze TMR error injection.

## Important APIs, Types, And Functions
- `struct xtmr_inject_dev` stores MMIO base and validated magic value.
- `xtmr_inject_set()` accepts debugfs value `1` and calls `xmb_inject_err()`.
- `xtmr_inject_init()` enables injection and programs address/instruction injection offsets.
- `xtmr_init_debugfs()` creates the `xtmr_inject` debugfs tree.
- `xtmr_inject_probe()` maps resources, reads `xlnx,magic`, initializes hardware, and stores driver data.

## Control Flow
Probe allocates state, maps MMIO, validates `xlnx,magic <= 255`, initializes TMR Inject control/address registers, creates debugfs, and binds data. A debugfs write of `1` triggers the MicroBlaze injection helper. Remove deletes the debugfs tree.

## State And Persistence
State is the mapped register base, magic value, global debugfs root, and fault-injection attributes. Hardware register state persists until reset or reprogramming. No disk state is used.

## Dependencies And Integration Points
Depends on platform/OF, debugfs, fault injection, MMIO, and `asm/xilinx_mb_manager.h`. Integrates with `xmb_inject_err()` and `XMB_INJECT_ERR_OFFSET`.

## Risks And Edge Cases
Fault injection is intentionally disruptive and should remain privileged. The global debugfs root assumes a single instance. Debugfs creation failures are not propagated. Invalid magic values are rejected.

## Test Signals
Build on an architecture with Xilinx MicroBlaze manager support. Runtime checks: matching `xlnx,tmr-inject-1.0` probe, debugfs creation, rejection of values other than `1`, and visible TMR manager error changes after injection.
