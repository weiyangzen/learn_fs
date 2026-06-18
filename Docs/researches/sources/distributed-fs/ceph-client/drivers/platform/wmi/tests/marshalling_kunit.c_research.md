# sources/distributed-fs/ceph-client/drivers/platform/wmi/tests/marshalling_kunit.c

Purpose: KUnit suite validating ACPI-object to WMI-buffer unmarshalling and WMI-string to ACPI-string marshalling.

Important APIs and types: Parameter structures describe valid ACPI object cases, valid string cases, invalid ACPI object cases, and invalid string cases. Tests call `wmi_unmarshal_acpi_object()` and `wmi_marshal_string()` through `../internal.h`; `KUNIT_ARRAY_PARAM` supplies named cases.

Control flow: Valid unmarshal tests transform integer, string, buffer, simple package, and complex package objects and compare exact bytes plus 8-byte data alignment. Valid marshal tests convert normal and padded WMI strings and compare ACPI string length/content. Failure tests assert rejection of nested packages, reference/processor/power objects, empty/oversized/undersized/non-ASCII WMI strings, and undersized `min_size` results.

State and persistence: Test data is static. Allocated results are registered with KUnit cleanup actions or freed on failure. No persistent state leaves the suite.

Dependencies and integration points: Depends on KUnit, ACPI object definitions, WMI structures, KUnit resource cleanup, and the KUnit export namespace from `marshalling.c`.

Risks: The suite exercises exact layout, so it is sensitive to intentional ABI changes. It does not cover allocation failure or every ACPI object type. Test source includes one non-ASCII-free path only by rejecting a sample above 0x7f.

Test signals: Suite name `wmi_marshalling`; all parameter descriptions identify the failing conversion case; failures indicate regressions in alignment, length accounting, byte order, padding, or validation.
