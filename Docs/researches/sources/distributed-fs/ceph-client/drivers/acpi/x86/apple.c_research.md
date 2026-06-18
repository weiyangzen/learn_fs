# sources/distributed-fs/ceph-client/drivers/acpi/x86/apple.c

### Purpose
`apple.c` converts Apple's custom ACPI `_DSM` property package format into Linux's standard `_DSD`-style software node property representation for Apple x86 machines.

### Important APIs, Types, And Functions
The exported function is `acpi_extract_apple_properties(struct acpi_device *adev)`. It uses the Apple property GUID, `acpi_evaluate_dsm_typed()`, bitmaps to track valid key/value pairs, ACPI object allocation, and `acpi_data_add_props()`.

### Control Flow
The function returns unless `x86_apple_machine` is true. It evaluates `_DSM` function 0 as a buffer, requires version byte 3, then evaluates function 1 as a package. The package is parsed as alternating key/value objects, accepting string keys and integer, buffer, or string values. Valid properties are copied into a newly allocated top-level package of two-element key/value packages and attached to `adev->data`.

### State, Persistence, And Dependencies
Converted properties are stored in `adev->data.pointer` and added under the Apple GUID, persisting with the ACPI device. Temporary ACPI objects and bitmaps are freed. Dependencies include Apple-specific firmware contracts, ACPI object layout, bitmap helpers, and the ACPI device property subsystem.

### Integration Points
This runs during ACPI device setup for Apple hardware so normal Linux drivers can consume firmware properties without understanding Apple's nonstandard `_DSM` encoding.

### Risks
The function trusts package count pairing and sizes its output buffer manually. Incorrect size accounting or invalid firmware object types could drop properties; the final `WARN_ON()` catches layout drift. It only supports protocol version 3.

### Test Signals
Test on Apple hardware with known `_DSM` properties, verify invalid properties are skipped with diagnostics, properties are visible through fwnode/property APIs, and no leaks occur when version or allocation checks fail.
