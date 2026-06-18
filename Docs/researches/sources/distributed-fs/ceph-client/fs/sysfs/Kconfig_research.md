# sources/distributed-fs/ceph-client/fs/sysfs/Kconfig

## Purpose
This Kconfig entry controls `CONFIG_SYSFS`, the virtual filesystem used to expose kernel objects, attributes, and relationships to userspace.

## Important APIs, Types, and Functions
The option is `bool "sysfs file system support" if EXPERT`, defaults to `y`, and selects `KERNFS`. Its help text documents sysfs as a core interface for devices, drivers, subsystem tuning, hotplug policy, and boot discovery.

## Control Flow and State
There is no runtime control flow in this file. Build-time selection enables compilation of sysfs sources and the kernfs dependency. Because the prompt is hidden unless `EXPERT`, normal kernel configurations keep sysfs enabled by default.

## Persistence, Dependencies, and Integration
Sysfs is deeply integrated with kobjects, driver core, block device discovery, and userspace device managers. The entry explicitly notes that disabling sysfs can force root-device specification by major/minor numbers.

## Risks and Test Signals
Disabling sysfs is high blast radius and mainly relevant to constrained embedded builds. Build tests should cover both default-enabled and expert-disabled configurations, while runtime boot tests should verify device discovery and hotplug consumers when enabled.
