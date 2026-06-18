# sources/distributed-fs/ceph-client/include/linux/raid_class.h

Purpose: defines the generic SCSI transport-style RAID class used to expose RAID level, state, resync progress, and components through the device model.

Important APIs and types: `struct raid_template` wraps a `transport_container`. `struct raid_function_template` supplies driver callbacks for RAID detection, resync, and state refresh. `enum raid_state` and `enum raid_level` classify exported status. `struct raid_data` stores component list/count, level, state, and resync value. `DEFINE_RAID_ATTRIBUTE()` generates inline setter/getter helpers for `level`, `resync`, and `state`. `raid_class_attach()` and `raid_class_release()` manage templates.

Control flow: a lower driver attaches a RAID class template, class devices are associated with real devices, callbacks refresh state, and generated setters/getters update the class device's `raid_data`.

State and persistence: state is device-model runtime state; real RAID metadata and persistence are owned by the hardware, firmware, or MD layer.

Dependencies and integration points: depends on `transport_class.h`, device model attributes, driver data, and component lists. It integrates SCSI/storage drivers with user-visible RAID status.

Risks and test signals: risks include missing class device causing `BUG_ON`, stale resync/state values, component list lifetime, and mismatch between driver callback output and class attributes. Test attach/release, sysfs attribute reads, hot-unplug during reads, resync progress updates, and all RAID level/state mappings.
