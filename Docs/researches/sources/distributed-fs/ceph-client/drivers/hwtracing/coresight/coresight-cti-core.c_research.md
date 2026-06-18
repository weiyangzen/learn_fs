# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-cti-core.c

## Purpose
`coresight-cti-core.c` implements the Arm CoreSight Cross Trigger Interface helper. It manages CTI hardware programming, CoreSight helper enable/disable, trigger/channel operations, CTI-to-device associations, and AMBA driver registration.

## Important APIs, Types, And Functions
`ect_net` tracks all CTI devices; `ect_mutex` protects that list. `cti_write_all_hw_regs()` writes cached CTI trigger, gate, ASIC, and app-set registers to hardware while enabling the CTI. `cti_enable_hw()` and `cti_disable_hw()` claim/disclaim hardware and maintain `enable_req_count`. Register access helpers include `cti_read_single_reg()`, `cti_write_single_reg()`, and `cti_write_intack()`.

Metadata functions include `cti_set_default_config()`, `cti_allocate_trig_con()`, `cti_add_connection_entry()`, and `cti_add_default_connection()`. Programming APIs exposed to sysfs are `cti_channel_trig_op()`, `cti_channel_gate_op()`, and `cti_channel_setop()`. Association callbacks `cti_add_assoc_to_csdev()` and `cti_remove_assoc_from_csdev()` integrate with CoreSight registration.

## Control Flow
Probe maps the AMBA resource, initializes CTI device metadata, reads hardware DEVID to set max triggers/channels/default gates, obtains platform connection data, chooses a CPU-bound or system CTI name, creates dynamic sysfs groups, clears stale self-claim tags, registers as helper subtype `ECT_CTI`, adds itself to `ect_net`, and fixes associations to already-registered CoreSight devices. CoreSight core calls CTI association callbacks whenever other devices register/unregister, allowing CTIs declared before their associated devices to be connected later.

On helper enable, CTI is claimed and all cached registers are written if it was inactive; subsequent enables increment a refcount. Disable decrements and only disables hardware at zero. Sysfs channel operations update cached register state under the spinlock and write through if active.

## State And Persistence
Per-device state is in `struct cti_drvdata`, especially `ctidev.trig_cons` and `config`. The config cache persists trigger/channel programming across inactive periods so enabling can restore it. `enable_req_count` tracks active users. Association state persists as CoreSight helper links and CTI sysfs cross-links.

## Dependencies And Integration Points
The driver depends on AMBA discovery, CoreSight helper registration, firmware/platform connection parsing from `coresight-cti-platform.c`, dynamic sysfs creation from `coresight-cti-sysfs.c`, CoreSight claim tags, and optional CTI association callbacks in the core.

## Risks
Reference-count imbalance can leave CTI enabled or return `-EINVAL` on disable. Trigger filtering prevents unsafe outputs such as PE debug request, but disabling filters via sysfs can expose disruptive signals. Association fixup depends on firmware node names and sysfs link success; failures leave `con_dev` NULL. Hardware max trigger/channel values from DEVID are trusted after clamping trigger count.

## Test Signals
Tests should cover probe with v8 architectural, implementation-defined, and default connections; dynamic sysfs group creation; channel attach/detach/gate/app operations while inactive and active; enable/disable refcounting; CTI association before and after associated CoreSight device registration; removal cleanup; and lockdep coverage around sysfs/hardware paths.
