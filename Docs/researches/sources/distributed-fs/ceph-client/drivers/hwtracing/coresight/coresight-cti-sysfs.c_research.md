# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-sysfs.c

## Purpose
`coresight-cti-sysfs.c` exposes CTI state and controls through static and dynamically generated sysfs attribute groups. It lets users enable CTIs, inspect management/programming registers, program trigger-to-channel routing, gate channels, emit software channel events, configure output filtering, and inspect firmware-described trigger connections.

## Important APIs, Types, And Functions
Static attributes include `enable`, `powered`, `ctmid`, and `nr_trigger_cons`. Management/register attributes use `coresight_cti_reg*()` helpers. Cached programming helpers `cti_reg32_show()` and `cti_reg32_store()` read active hardware or cached state and write through when active. Channel operations are parsed by `cti_trig_op_parse()` and `chan_op_parse()` and call core APIs such as `cti_channel_trig_op()`, `cti_channel_gate_op()`, and `cti_channel_setop()`.

Dynamic connection sysfs is built by `cti_create_cons_sysfs()`, `cti_create_con_attr_set()`, and `cti_create_con_sysfs_attr()`. Each connection gets a `triggers<N>` group with `name`, signal masks, and signal type names as applicable.

## Control Flow
At CTI probe, after platform parsing has populated the connection list, `cti_create_cons_sysfs()` allocates the combined group pointer table, installs static group pointers, then walks each `cti_trig_con` to create a dynamic `triggers<N>` group. During normal operation, sysfs writes parse user input, validate indexes or bitmasks through CTI core helpers, update cached config under the CTI spinlock, and write hardware only if the CTI is currently active. `enable_store()` handles runtime PM and calls CTI enable/disable helper paths.

## State And Persistence
Most sysfs programming updates `drvdata->config`, which persists while the device exists and is replayed by `cti_write_all_hw_regs()` on enable. Dynamic attributes store a pointer to the relevant `cti_trig_con` in `dev_ext_attribute.var`. `ctiinout_sel` and `xtrig_rchan_sel` are selector state used by several show/store attributes.

## Dependencies And Integration Points
The file depends on CTI core APIs, runtime PM, CoreSight register offsets, sysfs helpers, and platform-populated connection metadata. The exported `coresight_cti_groups` array is consumed by CTI core registration as the device's sysfs groups.

## Risks
Sysfs inputs directly affect cross-trigger routing; validation must prevent out-of-range channels/triggers and filtered output triggers unless filtering is intentionally disabled. Some show paths use `sprintf()` into sysfs buffers, though outputs are small. `pm_runtime_get_sync()` return handling in register reads does not check negative errors before register access. Dynamic attributes rely on devm lifetime and correct group-array sizing.

## Test Signals
Tests should inspect all static groups, dynamic `triggers<N>` groups for varied connection shapes, enable/disable runtime PM behavior, register visibility when ASICCTL is absent, attach/detach validation, filter enforcement, channel list rendering, reset behavior while active/inactive, and lockdep under concurrent sysfs access.
