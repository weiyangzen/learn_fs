<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-zynq.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-zynq.c

## Purpose

`cpuidle-zynq.c` is a minimal Xilinx Zynq cpuidle platform driver. It advertises two states: standard ARM WFI and a nominal `RAM_SR` state intended to combine WFI with DDR self refresh.

## Important APIs, Types, And Functions

`zynq_idle_driver` contains the two states and uses `zynq_enter_idle()` for `RAM_SR`. The enter routine currently only calls `cpu_do_idle()` and returns the selected index; comments mark where DDR self-refresh programming would belong.

## Control Flow

The builtin platform driver binds to `cpuidle-zynq`, logs startup from `zynq_cpuidle_probe()`, and calls `cpuidle_register()`. State 0 is the ARM cpuidle WFI macro. State 1 has low exit latency, long target residency, and no timer-stop or RCU-idle flags.

## State And Persistence Behavior

There is no driver-private dynamic state, no suspend/resume path, and no explicit hardware register persistence. The only persistent state is the registered cpuidle driver and its counters in the core.

## Dependencies And Integration Points

It depends on the ARM cpuidle helper macros, `cpu_do_idle()`, platform driver registration, and the cpuidle core. Integration is via the platform device name rather than OF match data in this file.

## Risks And Test Signals

The principal risk is that `RAM_SR` does not implement RAM self refresh despite its name, so it may mislead power validation. Test by checking state registration, verifying actual DDR/self-refresh hardware behavior externally, comparing residency counters, and ensuring no timer or interrupt behavior is assumed beyond WFI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-zynq.c -->
