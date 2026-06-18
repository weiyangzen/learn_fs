# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/coresight-sysfs.c

## Purpose
This file implements CoreSight sysfs controls and connection links. It allows users to mark sinks active, enable/disable sources through sysfs-created paths, expose labels and management-register attributes, and create bidirectional sysfs symlinks that describe topology.

## Important APIs, Types, And Functions
`coresight_simple_show_pair()` and `coresight_simple_show32()` read management registers under runtime PM and back the `coresight_simple_reg*` macros. `coresight_enable_sysfs()` validates a source, finds an activated sink, builds a path, assigns a trace ID, enables path and source, and stores the path either per CPU or in `path_idr`. `coresight_disable_sysfs()` reverses the operation, dropping source refcounts, retrieving the stored path, disabling, and releasing it. Sysfs attributes include `enable_sink`, `enable_source`, optional `label`, and `connections/nr_links`. Link helpers are `coresight_create_conns_sysfs_group()`, `coresight_add_sysfs_link()`, `coresight_make_links()`, and their removal counterparts.

## Control Flow And State
`coresight_mutex` serializes sysfs path state. Processor sources store one sysfs path per CPU in `tracer_path`; software, TPDM, and other sources store paths in `path_idr` keyed by a hash of the device name. Software sources may increment refcount when already enabled, supporting multiple applications. Sink selection recursively walks output connections until it finds `sysfs_sink_activated` on a sink or linksink.

## Dependencies And Integration Points
The file depends on CoreSight path operations, trace-id helpers, runtime PM, sysfs, IDR, firmware label properties, and device type registration. It exports helpers used by component drivers for management register groups and topology symlink creation.

## Risks And Test Signals
The path IDR uses a hashed device name as a fixed ID, so name collisions would break path lookup. Enable error unwinds must disable the path and release it in the right order. Source validation excludes unsupported source subtypes. Sysfs link removal decrements link counts and frees devm-allocated names. Test signals include sysfs path enable/disable for processor and software sources, multiple STM users, missing activated sink returning `-EINVAL`, perf/sysfs mode conflict, label visibility, link creation/removal, and management-register reads while runtime suspended.
