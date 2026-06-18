<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/clk-xlnx-clock-wizard.c -->
# sources/distributed-fs/ceph-client/drivers/clk/xilinx/clk-xlnx-clock-wizard.c

## Purpose

`clk-xlnx-clock-wizard.c` is the common clock driver for Xilinx Clocking Wizard IP. It supports classic and Versal register layouts, dynamic reconfiguration, optional full MMCM parameter programming, fractional output 0, up to seven outputs, and suspend/resume of the AXI interface clock.

## Important APIs, Types, And Functions

`struct clk_wzrd` stores MMIO base, input clocks, internal multiplier/divider clocks, speed grade, suspend flag, notifier, and onecell data. `struct clk_wzrd_divider` stores divider register metadata plus computed M/D/O fractional fields. The file implements classic and Versal recalc, determine, and set-rate callbacks; divisor search functions; dynamic reconfiguration with lock polling; fractional output programming; output-clock registration; clock-rate notifier; and PM ops.

## Control Flow

Probe reads `xlnx,nr-outputs`, maps MMIO, enables `s_axi_aclk`, validates AXI rate, and if not `xlnx,static-config`, gets `clk_in1`, registers output clocks, adds an OF provider, and optionally registers notifiers for speed-grade limits. Output registration either exposes a single divider or builds internal multiplier/divider clocks and per-output dividers, choosing Versal or classic callbacks by compatible match.

## State And Persistence Behavior

Clock configuration persists in the IP registers. Runtime state caches computed divisors in the divider object during rate calculation. `suspended` suppresses notifier rejections while AXI is disabled.

## Dependencies And Integration Points

It depends on platform/OF probing, CCF, MMIO, polling helpers, device PM, input clocks `s_axi_aclk` and `clk_in1`, and Xilinx DT properties including `xlnx,nr-outputs`, `xlnx,static-config`, and `xlnx,speed-grade`.

## Risks And Test Signals

Risks include dynamic reconfiguration timeout, complex classic/Versal field math, `min_t()` cap not assigned in one path, fractional rounding errors, static-config mode registering no provider, and speed-grade arrays indexed by validated grade only. Test single and multi-output designs, Versal and classic compatibles, fractional output0 rates, suspend/resume, invalid AXI/input rates, and lock timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/xilinx/clk-xlnx-clock-wizard.c -->
