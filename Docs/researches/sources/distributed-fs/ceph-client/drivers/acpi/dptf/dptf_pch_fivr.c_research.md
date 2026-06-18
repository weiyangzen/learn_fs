# sources/distributed-fs/ceph-client/drivers/acpi/dptf/dptf_pch_fivr.c

## Purpose
Implements the Intel DPTF PCH FIVR participant driver. It exposes PCH Fully Integrated Voltage Regulator switching-frequency telemetry and controls through a sysfs attribute group for supported INTC10xx ACPI devices.

## Important APIs, Types, And Functions
`struct pch_fivr_resp` represents two-integer AML method responses: status and result. `pch_fivr_read()` evaluates a method, extracts a two-integer package, and succeeds only when the returned status is zero. `PCH_FIVR_SHOW()` defines read attributes backed by AML methods `GFC0`, `GFC1`, `GEMI`, `GFCS`, and `GFFS`. `PCH_FIVR_STORE()` defines write attributes backed by `RFC0` and `RFC1`.

The sysfs group `pch_fivr_switch_frequency` contains `freq_mhz_low_clock`, `freq_mhz_high_clock`, `ssc_clock_info`, `fivr_switching_freq_mhz`, and `fivr_switching_fault_status`. Probe/remove are `pch_fivr_add()` and `pch_fivr_remove()` in a platform driver matching several `INTC` ACPI IDs.

## Control Flow
Probe gets the ACPI companion, evaluates `PTYP`, and binds only participant type `0x05`. It creates the sysfs group and stores the ACPI device as platform driver data. Reads call the relevant `G*` method and print the result. Writes parse an unsigned integer and execute the relevant `R*` method. Remove deletes the sysfs group.

## State And Persistence
The driver stores only the ACPI device pointer in platform driver data. FIVR settings and telemetry live in firmware/platform hardware and are accessed on demand through AML methods.

## Dependencies And Integration Points
Depends on ACPI platform-device enumeration, AML method evaluation/extraction, sysfs groups, and DPTF firmware participant semantics. It integrates with user-space thermal/power policy daemons through `/sys/.../pch_fivr_switch_frequency/`.

## Risks
The driver trusts participant type to distinguish the correct function among shared INTC IDs. AML response packages that are not exactly two numeric values or that report nonzero status return `-EFAULT`. Writes accept any `u32` and rely on firmware to validate the frequency request. `sprintf()` is used instead of `sysfs_emit()`, though outputs are small.

## Test Signals
Signals include binding only to `PTYP == 0x05`, presence of the sysfs group, successful reads of all telemetry attributes, successful writes to low/high clock controls with firmware-visible effects, and clean group removal on unbind. Negative tests should cover missing ACPI companion, wrong `PTYP`, malformed method packages, and failed AML writes.
