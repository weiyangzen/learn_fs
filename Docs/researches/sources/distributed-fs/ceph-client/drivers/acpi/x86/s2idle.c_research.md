# sources/distributed-fs/ceph-client/drivers/acpi/x86/s2idle.c

### Purpose
`s2idle.c` provides x86 ACPI Low Power S0 Idle support. It discovers the LPS0 device, validates platform `_DSM` interfaces, sequences entry/exit notifications around suspend-to-idle, optionally checks device constraints, and lets other drivers register LPS0 callbacks.

### Important APIs, Types, And Functions
The setup API is `acpi_s2idle_setup()`. Exported registration APIs are `acpi_register_lps0_dev()` and `acpi_unregister_lps0_dev()`. Internal helpers include `validate_dsm()`, `lps0_device_attach()`, `lpi_device_get_constraints()`, `lpi_device_get_constraints_amd()`, `lpi_check_constraints()`, and the platform s2idle ops wrappers.

### Control Flow
ACPI scan attaches to `PNP0D80`, validates Microsoft, AMD, or generic LPS0 DSM UUIDs, handles AMD function-mask quirks, sets suspend-to-idle as default when FADT Low Power S0 is set and S3 was not chosen, and marks EC GPE wake-capable. At suspend begin, constraints are fetched once if requested. Late prepare checks constraints, sends screen-off and LPS0/Modern Standby entry DSM calls, then invokes registered prepare callbacks. Restore invokes registered callbacks, then sends exit, display-on intent, Modern Standby exit, and screen-on DSM calls.

### State, Persistence, And Dependencies
Global state records the LPS0 handle, DSM GUIDs and masks, current DSM state, revision ID, constraint table, and registered device ops list. Module parameters `sleep_no_lps0` and `check_lps0_constraints` persist as runtime policy. Dependencies include ACPI DSM evaluation, suspend core `platform_s2idle_ops`, FADT flags, CPU vendor detection, EC wake handling, system sleep locking, and ACPI power-state data.

### Integration Points
This file links ACPI firmware LPS0 contracts with Linux suspend-to-idle. Drivers needing platform-specific hooks can register `acpi_s2idle_dev_ops`, and ACPI core sleep ops provide begin/prepare/check/wake/restore/end plumbing.

### Risks
DSM function ordering is firmware-sensitive and differs between AMD, Microsoft, and generic UUIDs. AMD Picasso-style off-by-one masks are corrected heuristically. Constraint parsing trusts nested package shapes enough to inspect them, so malformed firmware can disable useful diagnostics. Registered callback lists are protected by system sleep locks, not general-purpose list locks.

### Test Signals
Signals include LPS0 selected by default only when expected, DSM function masks logged correctly, suspend/resume DSM call order on AMD and non-AMD platforms, constraint warnings when devices stay above required D-states, EC wake behavior, and registered device callbacks running in prepare/check/restore phases.
