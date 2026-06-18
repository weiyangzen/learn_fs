# sources/distributed-fs/ceph-client/drivers/greybus/bundle.c

Purpose: Greybus bundle device management. A bundle groups interface CPorts and exposes device-model state for Greybus protocol drivers.

Important APIs and functions: sysfs attributes expose `bundle_class`, `bundle_id`, and writable `state`. `gb_bundle_create()`, `gb_bundle_add()`, and `gb_bundle_destroy()` manage lifecycle. Runtime PM helpers suspend/resume bundles, disable/enable all connections when protocol PM callbacks are absent, and notify the interface control protocol.

Control flow: creation validates bundle ID uniqueness, initializes device fields and connection list, links into the interface bundle list, and traces creation. Add registers the device. Destroy deletes the device if registered, removes it from the interface list, and drops the device reference. Runtime suspend calls driver PM if available or disables all connections, then sends control bundle suspend; on failure it resumes/enables connections.

State and persistence: each `gb_bundle` owns class/id/version fields, `state` string, CPort descriptors, device object, and connection list. Sysfs `state_store` replaces the stored state string and notifies userspace.

Dependencies and integration: depends on Greybus bus/device types, control protocol, connection APIs, runtime PM, sysfs, and tracepoints.

Risks: sysfs state is free-form and allocated from user input. Runtime PM rollback must match whichever path suspended the bundle. Bundle IDs are assumed serialized during interface initialization.

Test signals: device registration under Greybus bus, sysfs attribute behavior, runtime suspend/resume of bundles, connection disable/enable traces, and control PM operation results.
