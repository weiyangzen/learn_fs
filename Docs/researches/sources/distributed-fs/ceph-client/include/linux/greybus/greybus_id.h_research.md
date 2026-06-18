<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_id.h -->
# sources/distributed-fs/ceph-client/include/linux/greybus/greybus_id.h

Purpose: This header defines Greybus bundle-driver match records and match flag bits.

Important APIs/types/functions: `struct greybus_bundle_id` contains `match_flags`, vendor, product, class, class major/minor, and driver-private data. Match bits distinguish vendor, product, class, class major, and class minor. `GREYBUS_DEVICE()` and `GREYBUS_DEVICE_CLASS()` in the umbrella header populate this structure for common matches.

Control flow, state, and persistence: Greybus bus matching scans a driver's id table and compares only fields selected by `match_flags`. Matched entries provide optional `driver_info` to the probing driver.

Dependencies/integration: It integrates with Greybus bus registration and Linux module device table generation for Greybus drivers.

Risks and test signals: Under-specified flags can overmatch unrelated bundles; over-specified version fields can prevent binding. Tests should cover vendor/product match, class-only match, class-version match, sentinel termination, and `driver_info` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/greybus/greybus_id.h -->
