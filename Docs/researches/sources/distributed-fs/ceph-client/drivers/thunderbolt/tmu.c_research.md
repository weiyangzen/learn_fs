# sources/distributed-fs/ceph-client/drivers/thunderbolt/tmu.c

## Purpose

`tmu.c` implements Thunderbolt/USB4 Time Management Unit support. It discovers router and lane-adapter TMU capabilities, records the current TMU mode, configures requested modes, posts grandmaster time to newly attached USB4 routers, enables or disables time synchronization, and rolls hardware back when a mode transition fails.

## Important APIs, Types, and Functions

Public entry points are `tb_switch_tmu_init()`, `tb_switch_tmu_post_time()`, `tb_switch_tmu_disable()`, `tb_switch_tmu_enable()`, and `tb_switch_tmu_configure()`. They operate on `struct tb_switch` and its `sw->tmu` substructure, whose mode enum is declared in `tb.h`. Internal data tables `tmu_rates[]` and `tmu_params[]` map `TB_SWITCH_TMU_MODE_OFF`, `LOWRES`, `HIFI_UNI`, `HIFI_BI`, and `MEDRES_ENHANCED_UNI` to timestamp intervals and averaging/replay parameters.

Important helpers include `tmu_mode_name()`, `tb_switch_tmu_enhanced_is_supported()`, `tb_switch_set_tmu_mode_params()`, `tb_switch_tmu_ucap_is_supported()`, `tb_switch_tmu_rate_read()`, `tb_switch_tmu_rate_write()`, `tb_port_tmu_set_unidirectional()`, `tb_port_tmu_enhanced_enable()`, `tb_port_set_tmu_mode_params()`, `tb_port_tmu_rate_write()`, `tb_port_tmu_time_sync_enable()/disable()`, `tb_switch_tmu_set_time_disruption()`, `tmu_mode_init()`, and rollback helpers `tb_switch_tmu_off()` and `tb_switch_tmu_change_mode_prev()`.

## Control Flow

Initialization skips ICM-managed switches, locates router TMU and lane time capabilities, reads the current timestamp interval, checks unidirectional and enhanced mode flags, and derives `sw->tmu.mode`, `mode_request`, and `has_ucap` without changing hardware. Configuration only validates and stores the requested mode. Enable first marks time disrupted, then either writes only the host router rate or, for device routers, selects an off-to-unidirectional, off-to-bidirectional, off-to-enhanced, or non-off mode-change sequence. Each sequence programs parent/child rates, router parameters, lane-adapter unidirectional or enhanced bits, and time-sync disable bits in a strict order. Failure paths attempt to restore off or previous mode.

`tb_switch_tmu_post_time()` reads the root switch grandmaster local time, converts the register representation to nanoseconds, asserts time disruption on the target, writes Post Local Time and Post Time registers, polls until completion, and clears disruption. Disable turns off the local router rate, disables adapter time sync, clears unidirectional or enhanced state where applicable, and updates `sw->tmu.mode` to off.

## State and Persistence Behavior

Persistent software state is limited to `sw->tmu.cap`, per-port `port->cap_tmu`, `sw->tmu.mode`, `sw->tmu.mode_request`, and `sw->tmu.has_ucap`. Hardware-visible state is stored in TMU router and adapter config registers such as `TMU_RTR_CS_*`, `TMU_ADP_CS_*`, and Titan Ridge VSEC time registers. There is no disk persistence; state is reconstructed by `tb_switch_tmu_init()` and modified during router attach, enable, disable, and mode changes.

## Dependencies and Integration Points

The file depends on `tb.h`, config-space accessors `tb_sw_read/write()` and `tb_port_read/write()`, router helpers such as `tb_route()`, `tb_switch_parent()`, `tb_upstream_port()`, `tb_switch_downstream_port()`, `tb_switch_is_usb4()`, `tb_switch_is_icm()`, `tb_switch_is_titan_ridge()`, and `usb4_switch_version()`. The connection manager in `tb.c` chooses TMU modes, calls configure/enable during discovery, disables TMU on unplug, and initializes low-resolution mode on the root switch.

## Risks and Edge Cases

TMU mode changes touch both sides of a link and can leave partially programmed hardware if a write fails after upstream state was changed. Rollback intentionally ignores some errors, which avoids masking the original failure but may leave stale hardware state after unplug or transient config-space failure. Enhanced mode requires both parent and child support; incorrect version detection can return `-EOPNOTSUPP` or attempt unsupported register writes. Time posting relies on a bounded poll and disruption bit cleanup; timeout or cleanup failure affects synchronization quality. There is no direct KUnit coverage in this file.

## Test Signals

Useful signals include compile coverage, mocked config-space tests for mode validation and rollback ordering, attach/resume tests that confirm `sw->tmu.mode` and hardware rates match, fault injection for read/write failures in each transition step, USB4 v1/v2 and Titan Ridge hardware validation, and tracing/debug logs showing time disruption is cleared on success and failure.
