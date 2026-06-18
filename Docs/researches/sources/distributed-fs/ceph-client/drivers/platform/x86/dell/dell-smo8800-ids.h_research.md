# sources/distributed-fs/ceph-client/drivers/platform/x86/dell/dell-smo8800-ids.h

Purpose: Shared ACPI match table for Dell SMO88xx freefall/accelerometer devices.

Important APIs/types/functions: Static `smo8800_ids` table with `SMO8800`, `SMO8801`, `SMO8810`, `SMO8811`, `SMO8820`, `SMO8821`, `SMO8830`, and `SMO8831`, plus `MODULE_DEVICE_TABLE(acpi, ...)`.

Control flow/state/persistence: Header-only static data.

Dependencies/integration: Included by `dell-smo8800.c` and `dell-lis3lv02d.c`.

Risks/test signals: Missing IDs prevent binding/autoload. Test ACPI modalias autoload and both freefall and I2C companion paths.
