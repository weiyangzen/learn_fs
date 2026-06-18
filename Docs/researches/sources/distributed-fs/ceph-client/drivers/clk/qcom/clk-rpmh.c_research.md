# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-rpmh.c

## Purpose
Implements Qualcomm RPMh clock providers for modern platforms. It exposes ARC/VRM on-off clocks and BCM rate-vote clocks, resolves RPMh resource names through command DB, sends TCS commands to sleep, wake, and active-only RPMh states, and supplies many SoC-specific clock tables for RPMh-enabled Qualcomm chips.

## Important APIs, Types, And Functions
- `struct clk_rpmh` holds the common-clock handle, command-DB resource name, divider, resolved RPMh address, on value, local and aggregate state masks, last sent aggregate state, valid state mask, BCM unit, device pointer, and peer.
- `struct clk_rpmh_desc` maps dt-binding indexes to `clk_hw` pointers and marks platforms where `clka*` resources may be absent.
- `clk_rpmh_send_aggregate_command` compares `aggr_state` against `last_sent_aggr_state`, sends only changed sleep/wake/active state commands, and mirrors last-sent state to the peer.
- `clk_rpmh_aggregate_state_send_command`, `clk_rpmh_prepare`, and `clk_rpmh_unprepare` maintain peer aggregation for normal and always-on RPMh clocks.
- `clk_rpmh_bcm_set_rate`, `clk_rpmh_bcm_prepare`, and `clk_rpmh_bcm_send_cmd` implement Bus Clock Manager active-only votes using command-DB auxiliary unit data.
- `clk_rpmh_probe` resolves every clock resource through `cmd_db_read_addr`, reads optional `struct bcm_db` aux data, registers clocks, and adds the OF provider.

## Control Flow
Probe chooses a descriptor by compatible string, then walks its indexed `clk_hw` table. For each non-null clock it resolves the command-DB resource address, optionally tolerates missing `clka*` resources on descriptors with `clka_optional`, reads auxiliary data, stores the device pointer, and registers the hardware. For ARC/VRM clocks, prepare sets the clock's state to its valid mask, ORs it with the peer state, and sends only state transitions. Non-AO clocks vote sleep, wake, and active states; AO peers vote wake and active only. Active-state sends wait when a nonzero aggregate active vote is present; other sends can be asynchronous. For BCM clocks, set-rate stores a scaled aggregate state, and prepare/unprepare sends one active-only `BCM_TCS_CMD` because RPMh can reuse active state when sleep/wake votes are unset.

## State And Persistence
Each `clk_rpmh` caches command DB resolution (`res_addr`), message scaling (`unit`), current local state, aggregate peer state, and last state actually sent. Persistent state is the RPMh vote stored by firmware for the resource address in each RPMh state. For BCM clocks, `aggr_state` is a numeric bandwidth/clock vote rather than a bitmask. Static clock definitions are shared across descriptors, so state is process-global within the kernel image.

## Dependencies And Integration Points
The driver depends on `soc/qcom/cmd-db` for resource address and aux data, `soc/qcom/rpmh` and `soc/qcom/tcs` for command submission, RPMh dt-bindings for public clock indexes, and the common clock framework. It integrates with RPMh firmware resources such as `xo.lvl`, `qphy.lvl`, `rfclka*`, `clka*`, and BCM resources like `CE0`, `IP0`, `HK0`, `PKA0`, and `QP0`.

## Risks And Edge Cases
Command DB names must match firmware exactly; a missing resource fails probe except for explicitly optional `clka*` entries. State-change filtering relies on `last_sent_aggr_state`, so errors must not update it. Failed enable attempts roll back local state but aggregate state can be transiently stale until the next operation. BCM rate votes are clamped to `BCM_TCS_CMD_VOTE_MASK`, so high rates can saturate. Static objects reused across many compatible tables require only one RPMh clock device instance. Sleep/wake/active ordering matters for suspend behavior.

## Test Signals
Test signals include successful command-DB resolution for every non-optional entry, missing optional `clka*` entries being nulled without probe failure, prepare/unprepare sending only changed RPMh states, AO and non-AO peers aggregating correctly, BCM `set_rate` affecting prepared clocks immediately, active sends waiting when enabling, and recalc rates returning parent/divider or `aggr_state * unit` as expected.
