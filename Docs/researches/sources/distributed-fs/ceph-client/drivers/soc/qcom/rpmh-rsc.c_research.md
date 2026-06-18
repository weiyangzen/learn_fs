# sources/distributed-fs/ceph-client/drivers/soc/qcom/rpmh-rsc.c

## Purpose

`rpmh-rsc.c` is the Qualcomm RPMh Resource State Coordinator driver. It discovers RSC/TCS hardware, programs Trigger Command Sets, handles active-transfer completion IRQs, writes cached sleep/wake votes before low-power transitions, and populates RPMh child devices.

## Important APIs, Types, and Functions

Public-to-internal functions are `rpmh_rsc_send_data()`, `rpmh_rsc_write_ctrl_data()`, `rpmh_rsc_invalidate()`, and `rpmh_rsc_write_next_wakeup()`. Key helpers include register offset tables for RSC versions 2.7 and 3.0, TCS register accessors, `tcs_invalidate()`, `get_tcs_for_msg()`, `tcs_tx_done()`, `__tcs_buffer_write()`, `check_for_req_inflight()`, `claim_tcs_for_req()`, `find_slots()`, PM callbacks, `rpmh_probe_tcs_config()`, and `rpmh_rsc_probe()`.

## Control Flow

Probe waits for command DB readiness, allocates `struct rsc_drv`, reads `qcom,drv-id` and label, maps the named `drv-N` resource, reads RSC version, selects register offsets, parses `qcom,tcs-offset` and `qcom,tcs-config`, initializes locks and waitqueue, requests the per-DRV IRQ, installs CPU PM or genpd notifiers unless hardware solver mode is present, enables active TCS IRQs, initializes RPMh caches, stores drvdata, and populates children. Active requests claim a free non-conflicting TCS under lock, write commands, and trigger AMC mode. IRQ completion clears trigger/enable, releases TCS ownership, wakes waiters, and calls `rpmh_tx_done()`. Sleep/wake requests are written into slots without triggering and are used by firmware during low power entry.

## State and Persistence Behavior

Driver state tracks TCS group ownership, software in-use bits, slot bitmaps, active request pointers, cached RPMh client votes, and PM notifier state. Hardware TCS command registers persist until invalidated or overwritten. `rpmh_rsc_write_next_wakeup()` writes control-TCS wakeup timestamp data for low-power coordination.

## Dependencies and Integration Points

It depends on platform resources, command DB, DT TCS configuration, IRQs, CPU PM, genpd, PM runtime, arch timer, RPMh internal API, TCS public definitions, and child platform devices. Client drivers under the RSC use `rpmh.c` APIs to submit votes.

## Risks and Edge Cases

`rpmh_rsc_send_data()` waits indefinitely for a free TCS; missing interrupts can hang callers. Borrowed wake TCSes for active transfers require careful invalidation before later wake usage. PM callbacks rely on being the last CPU or serialized genpd transition and require interrupts disabled for `rpmh_flush()`. TCS config validation must match hardware; bad DT can miscompute masks and offsets. There is no explicit remove path to unregister CPU PM notifiers for dynamically removed devices, likely mitigated by suppressing bind attrs and initcall-style platform use.

## Test Signals

Test RSC version selection, invalid `qcom,tcs-config`, active transfer completion, TCS exhaustion, same-address conflict waiting, missing active TCS with wake borrowing, sleep/wake flush, batch slot exhaustion, CPU PM/genpd notifier failure, hardware solver mode, next-wakeup programming, IRQ storm handling, and child population failure unwinding.
