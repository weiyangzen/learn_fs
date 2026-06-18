<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_amd_wbrf.h -->
# sources/distributed-fs/ceph-client/include/linux/acpi_amd_wbrf.h

## Purpose
`acpi_amd_wbrf.h` declares AMD ACPI Wifi Band Exclusion/WBRF interfaces for producers and consumers of active frequency band ranges.

## Important APIs, types, and functions
Constants define up to `MAX_NUM_OF_WBRF_RANGES`, record actions `WBRF_RECORD_ADD` and `WBRF_RECORD_REMOVE`, and notifier action `WBRF_CHANGED`. `struct freq_band_range` stores start/end frequencies in Hz. `struct wbrf_ranges_in_out` carries a count and fixed band array. Enabled APIs include producer/consumer support checks, add/remove, frequency-band retrieval, and notifier register/unregister. Disabled stubs return false or `-ENODEV`.

## Control flow
Producer devices publish or remove frequency ranges. Consumers check support, retrieve active ranges, and subscribe to notifier updates to react to changes.

## State and persistence behavior
Active WBRF records are platform/ACPI-managed state outside this header. The fixed-size array bounds the persisted record payload exchanged with firmware.

## Dependencies and integration points
It depends on `struct device` and Linux notifier blocks. Integration points are AMD ACPI platform code, Wi-Fi/radio consumers, and frequency-conflict mitigation logic.

## Risks and test signals
Risks include range count overflow, Hz unit mistakes, stale consumer state after notifier failure, and disabled stubs being ignored. Test signals include ACPI WBRF producer/consumer probe paths, notifier update tests, max-range validation, and non-AMD/non-WBRF builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/acpi_amd_wbrf.h -->
