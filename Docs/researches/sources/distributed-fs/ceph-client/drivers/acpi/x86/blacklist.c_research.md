# sources/distributed-fs/ceph-client/drivers/acpi/x86/blacklist.c

### Purpose
`blacklist.c` handles early x86 ACPI firmware blacklisting and optional DMI-based `_REV` override quirks for machines whose firmware behavior depends on Windows-like ACPI revision reporting.

### Important APIs, Types, And Functions
The main API is `acpi_blacklisted()`. It uses `acpi_match_platform_list()` against `acpi_blacklist`, calls `early_acpi_osi_init()`, and optionally scans `acpi_rev_dmi_table`. With `CONFIG_ACPI_REV_OVERRIDE_POSSIBLE`, `dmi_enable_rev_override()` calls `acpi_rev_override_setup(NULL)`.

### Control Flow
During early ACPI setup, the code matches OEM table IDs/revisions against known broken DSDTs. A match logs vendor, table, reason, and recoverability and returns the critical flag. It then initializes early OSI handling and applies DMI `_REV` overrides for selected Dell systems.

### State, Persistence, And Dependencies
The blacklist table is `__initdata`; DMI revision table is `__initconst`. Persistent effects are the return value controlling ACPI continuation and global `_REV` override state set by `acpi_rev_override_setup()`.

### Integration Points
This is part of early ACPI boot policy. It coordinates with ACPI table matching, DMI, OSI initialization, audio/ethernet quirks on Dell systems, and kernel config options controlling whether `_REV` override is possible.

### Risks
False positives can disable ACPI or alter firmware paths unnecessarily; false negatives can boot with known nonrecoverable firmware defects. DMI `_REV` override is machine-specific because it can change device exposure and method behavior.

### Test Signals
Boot logs should show blacklist and `_REV` notices only on matching hardware. ACPI disabled/continued behavior should match critical flags, and Dell listed systems should expose expected audio/network devices under the override.
