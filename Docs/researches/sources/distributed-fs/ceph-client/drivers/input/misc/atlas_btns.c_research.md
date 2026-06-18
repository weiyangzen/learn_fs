<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atlas_btns.c -->
## sources/distributed-fs/ceph-client/drivers/input/misc/atlas_btns.c

Purpose: ACPI address-space based button driver for Atlas wallmount touchscreen systems.

Important APIs/types/functions: `atlas_acpi_button_probe()` allocates a global input device, builds an F1-F9 keymap, registers it, and installs ACPI address-space handler `0x81`. `acpi_atlas_button_handler()` treats ACPI writes as scan events and reports press/release based on address bits. Remove unregisters the handler and input device.

Control flow and state: ACPI firmware writes to the custom region; the handler extracts low-nibble scan code and bit 4 key state, reports `MSC_SCAN`, key state, and sync. Probe/remove are platform-driver callbacks matched by ACPI ID `ASIM0000`.

State and persistence behavior: global `atlas_keymap` and `input_dev` persist for the device lifetime. Firmware owns button state; the driver reports events immediately without debouncing.

Dependencies and integration points: depends on ACPI companion device, ACPI address-space handler APIs, Linux input, and platform driver binding.

Risks: global input pointer assumes one device. Handler ignores reads and returns `AE_BAD_PARAMETER`. ACPI callbacks can race with remove if firmware still accesses the region after handler removal errors.

Test signals: test ACPI ID binding, address-space install/remove, all F1-F9 scan codes, key up/down address bit behavior, unexpected ACPI read handling, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/atlas_btns.c -->
