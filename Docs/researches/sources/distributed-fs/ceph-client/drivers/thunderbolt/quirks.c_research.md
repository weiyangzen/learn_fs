<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/quirks.c -->
# sources/distributed-fs/ceph-client/drivers/thunderbolt/quirks.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/thunderbolt/quirks.c` centralizes router-specific workarounds matched by hardware/vendor/device IDs. It mutates `struct tb_switch` fields after switch identification to compensate for known platform or firmware issues. The source was read as a complete 144-line file.

## Important APIs, Types, and Functions

The public function is `tb_check_quirks()`. `struct tb_quirk` describes match fields and a hook. Hooks are `quirk_force_power_link()`, `quirk_dp_credit_allocation()`, `quirk_clx_disable()`, `quirk_usb3_maximum_bandwidth()`, and `quirk_block_rpm_in_redrive()`. The `tb_quirks[]` table covers Dell WD19TB self-authentication, Titan Ridge CLx, Intel Goshen Ridge DP buffer reporting, selected Intel USB4 host/hub bandwidth limits, Barlow Ridge DP redrive runtime PM behavior, and AMD Yellow Carp/Pink Sardine CLx.

## Control Flow

`tb_check_quirks()` scans the table and applies every entry whose nonzero hardware vendor/device and vendor/device fields match the switch. Hooks set switch quirk bits, reduce DP main credits from 56 to 18, disable CL states except for Titan Ridge firmware >= 0x65, cap downstream USB3 max bandwidth on non-ICM routers, or mark DP redrive runtime PM as blocked.

## State and Persistence Behavior

State changes are in-memory fields on `struct tb_switch` and its ports: `sw->quirks`, `sw->min_dp_main_credits`, and `port->max_bw`. They persist until the switch object is removed and are recomputed on rediscovery.

## Dependencies and Integration Points

The file depends on `tb.h` for switch/port helpers and PCI ID constants. It is called from `tb_switch_add()` after DROM/ports are initialized and before later link/tunnel policy relies on those fields.

## Risks and Edge Cases

Quirks can stack because the scan does not stop at first match. ID matching must distinguish NHI IDs, bridge IDs, USB4 vendor IDs, and DROM vendor/device IDs. Incorrectly applying bandwidth or CLx quirks can reduce performance or power savings; failing to apply them can cause unstable links, bad DP allocation, or broken wake/authentication flows.

## Test Signals

Unit-style table match tests, boot logs on affected docks/controllers, DP tunnel allocation on Goshen Ridge, CLx entry/exit on Titan Ridge and AMD platforms, USB3 bandwidth reporting on listed Intel hosts, and runtime PM behavior in Barlow Ridge DP redrive mode are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/thunderbolt/quirks.c -->
