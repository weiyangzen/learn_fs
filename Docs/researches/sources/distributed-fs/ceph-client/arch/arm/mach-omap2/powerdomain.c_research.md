# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/powerdomain.c

## Purpose
`powerdomain.c` implements the generic OMAP powerdomain framework. It registers SoC-specific operation callbacks and powerdomain descriptors, tracks state counters, associates clockdomains, validates requested states, programs next power states, manages transition bookkeeping, and saves/restores powerdomain context for AM43xx RTC-DDR suspend.

## Important APIs, Types, and Functions
Public APIs include `pwrdm_register_platform_funcs()`, `pwrdm_register_pwrdms()`, `pwrdm_complete_init()`, `pwrdm_lookup()`, `pwrdm_for_each()`, `pwrdm_add_clkdm()`, `pwrdm_set_next_pwrst()`, read/set helpers for logic and memory states, `pwrdm_enable_hdwr_sar()`, `pwrdm_state_switch_nolock()`, `pwrdm_pre_transition()`, `pwrdm_post_transition()`, `pwrdm_get_valid_lp_state()`, and `omap_set_pwrdm_state()`.

## Control Flow
SoC data files first register `struct pwrdm_ops`, then arrays of `struct powerdomain`, then call complete init. Registration validates names, PRCM partitions, voltage-domain links, initializes locks and counters, reads current state, and appends to `pwrdm_list`. State changes validate support, optionally wake the first associated clockdomain, program next state through arch ops, then restore clockdomain behavior and update counters.

## State and Persistence Behavior
Core state is `pwrdm_list`, `arch_pwrdm`, per-powerdomain locks, current state, state counters, logic/memory off counters, voltage-domain links, clockdomain arrays, and optional context snapshots. Hardware state is all PRM/CM powerdomain state controlled through `arch_pwrdm` callbacks.

## Dependencies and Integration Points
It depends on CPU PM notifiers, tracepoints, clockdomain and voltage frameworks, SoC detection, and the SoC-specific `pwrdm_ops` implementations in PRM/CM code. PM files call pre/post transition hooks and state setters during idle/suspend.

## Risks
The framework assumes the first clockdomain can be forced awake for some transitions. Unsupported power states are often degraded rather than hard-failed, which can hide data-table problems. Missing arch callbacks return errors or leave stale state. Context save/restore is only registered for AM43xx when off-mode is enabled.

## Test Signals
Boot each SoC family and verify powerdomain registration, no duplicate names, valid voltage-domain links, and no transition timeouts. Use PM debug counters/tracepoints to confirm target versus achieved states. Suspend/resume should preserve context and not emit state mismatch warnings.
