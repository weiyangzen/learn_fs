# sources/distributed-fs/ceph-client/drivers/misc/smpro-errmon.c

## Purpose
`smpro-errmon.c` exposes Ampere Altra SMpro/PMPRO RAS error, warning, event, overflow, and DIMM syndrome data through sysfs attributes backed by the parent SMpro regmap.

## Important APIs, Types, and Functions
`struct smpro_errmon` stores the parent `regmap`. `struct smpro_error_hdr` maps count/length/data registers and maximum counts for 48-byte CE/UE classes. `struct smpro_int_error_hdr` maps internal SMpro/PMPRO error and warning registers. Read helpers are `smpro_event_data_read()`, `smpro_overflow_data_read()`, `smpro_error_data_read()`, `smpro_internal_err_read()`, `smpro_internal_warn_read()`, and `smpro_dimm_syndrome_read()`. Attribute macros generate overflow, error, event, and DIMM syndrome sysfs files. `smpro_errmon_probe()` obtains the parent regmap and the driver uses `ATTRIBUTE_GROUPS(smpro_errmon)`.

## Control Flow
Probe allocates private data, attaches it to the platform device, and retrieves the parent regmap. Sysfs reads perform direct register transactions: event reads fetch and clear nonzero event data; overflow reads inspect bit 8 in the count register; 48-byte error reads validate count and length, perform a no-increment block read, then clear by writing `0x100` to the count register. Internal error/warning reads first check `GPI_RAS_ERR`, inspect the type register, assemble high/low words, optionally read extended data, and clear the consumed bit. DIMM syndrome reads only proceed in boot stage 4, select a DIMM slot, and emit the syndrome register.

## State and Persistence
State is almost entirely device-register backed. Several sysfs reads are destructive because they clear event, error, or warning bits after reporting them. The driver keeps only a regmap pointer and static register tables; no cache or suspend persistence is implemented.

## Dependencies and Integration Points
It is a platform child named `smpro-errmon`, integrated with an MFD or parent device that exposes a regmap. It depends on Linux sysfs device attribute groups, `regmap_read()`, `regmap_write()`, and `regmap_noinc_read()`.

## Risks and Edge Cases
`smpro_error_data_read()` masks `err_count` before checking `ret`, so a failed `regmap_read()` leaves `err_count` undefined before the function returns the error. Reads returning `0` for absent events produce empty sysfs reads rather than formatted zero values in some paths. Destructive read semantics can surprise polling tools and lose events if multiple readers race. Count and length validation relies on firmware-provided limits.

## Test Signals
Validate each generated sysfs file against known register fixtures, destructive clear-on-read behavior, overflow bit reporting, max-count and length clamping, SMpro/PMPRO internal warning/error formatting, DIMM syndrome stage gating, and regmap error propagation.
