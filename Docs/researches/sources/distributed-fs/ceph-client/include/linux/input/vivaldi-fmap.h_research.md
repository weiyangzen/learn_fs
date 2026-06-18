<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/vivaldi-fmap.h -->
# sources/distributed-fs/ceph-client/include/linux/input/vivaldi-fmap.h

Purpose: Defines ChromeOS Vivaldi keyboard function-row physical map data and sysfs formatting.

Important APIs/types/functions: `VIVALDI_MAX_FUNCTION_ROW_KEYS` caps maps at 24 entries. `struct vivaldi_data` stores function-row physical scancodes/HID usages in left-to-right order and a count. `vivaldi_function_row_physmap_show()` formats the map into a buffer.

Control flow: Keyboard drivers populate `vivaldi_data` and expose/show the function row map for userspace policy.

State/persistence: The map persists as keyboard metadata for the device lifetime.

Dependencies/integration: Depends on input keyboard drivers and ChromeOS top-row key semantics.

Risks: Incorrect order or count breaks userspace key labeling and remapping.

Test signals: Sysfs/show output, max-key boundary, HID/scancode mapping order, and devices without custom function rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/input/vivaldi-fmap.h -->
