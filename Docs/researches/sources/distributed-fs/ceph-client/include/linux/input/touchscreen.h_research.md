<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/touchscreen.h -->
# sources/distributed-fs/ceph-client/include/linux/input/touchscreen.h

Purpose: Provides common touchscreen property parsing and coordinate transformation helpers.

Important APIs/types/functions: `struct touchscreen_properties` stores max X/Y, invert flags, and axis swap flag. `touchscreen_parse_properties()` reads standard properties into the struct. `touchscreen_set_mt_pos()` transforms raw X/Y into an `input_mt_pos`. `touchscreen_report_pos()` reports transformed single-touch or multitouch positions.

Control flow: Drivers parse properties at probe and apply transformations to every contact report.

State/persistence: Parsed properties persist in driver state; no state is owned by the header.

Dependencies/integration: Integrates input abs axes, multitouch helpers, firmware properties, and touchscreen drivers.

Risks: Transform order and max values must match hardware orientation; wrong multitouch flag changes reported event type.

Test signals: Invert X/Y, swap axes, max-boundary coordinates, single-touch versus multitouch reporting, and property absence defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/touchscreen.h -->
