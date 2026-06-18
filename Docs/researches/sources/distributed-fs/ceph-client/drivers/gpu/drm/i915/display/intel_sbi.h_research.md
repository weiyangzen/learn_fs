<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.h

## Purpose
`intel_sbi.h` declares the i915 display Sideband Interface API and destination selector used for LPT/WPT IOSF sideband register access.

## Important APIs, Types, And Functions
The key type is `enum intel_sbi_destination` with `SBI_ICLK` and `SBI_MPHY`. The API exposes init/fini, explicit lock/unlock, and `intel_sbi_read()`/`intel_sbi_write()`.

## Control Flow
The header defines the expected caller pattern: initialize during display driver setup, lock around one or more sideband operations, perform reads/writes to a selected destination, unlock, and destroy during teardown.

## State And Persistence Behavior
No state is declared here. The backing mutex lives in `struct intel_display` and hardware side effects live in sideband registers.

## Dependencies And Integration Points
It includes Linux integer types and forward-declares `struct intel_display`. Users include display driver init/fini and PCH refclock programming.

## Risks
The API exposes manual locking, so callers can omit or mis-balance locks. Read/write functions do not return errors, making log monitoring important for failures.

## Test Signals
Build coverage validates API consumers. Runtime signals include lockdep, SBI timeout logs, and refclock stability on affected chipsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sbi.h -->
