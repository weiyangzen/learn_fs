# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/wbrf.c

## Purpose
`wbrf.c` provides AMD ACPI WBRF, the Wi-Fi Band RFI mitigation interface. It lets producer devices publish active frequency ranges to BIOS, lets consumer devices retrieve the active range list, and provides a blocking notifier chain so consumers such as graphics drivers can react when producer frequency bands change.

## Important APIs, Types, and Functions
The exported API consists of `acpi_amd_wbrf_add_remove()`, `acpi_amd_wbrf_supported_producer()`, `acpi_amd_wbrf_supported_consumer()`, `amd_wbrf_retrieve_freq_band()`, `amd_wbrf_register_notifier()`, and `amd_wbrf_unregister_notifier()`. Internal helper `wbrf_record()` formats input ranges into the ACPI `_DSM` package for add/remove actions. `struct amd_wbrf_ranges_out` mirrors the packed firmware output buffer for retrieval, while public input/output uses `struct wbrf_ranges_in_out` and `struct freq_band_range` from `linux/acpi_amd_wbrf.h`.

## Control Flow
Producers first check support using `acpi_amd_wbrf_supported_producer()`, which requires an ACPI companion and checks `_DSM` function bit `WBRF_RECORD`. To publish a range update, `acpi_amd_wbrf_add_remove()` obtains the ACPI companion, calls `wbrf_record()`, and broadcasts `WBRF_CHANGED` on success. `wbrf_record()` validates that `in->num_of_ranges` matches the number of non-zero start/end range entries, builds an ACPI package containing range count, action, and start/end integer pairs, evaluates the WBRF record `_DSM`, and requires an integer zero result.

Consumers check support with `acpi_amd_wbrf_supported_consumer()`, register a notifier, and retrieve active ranges with `amd_wbrf_retrieve_freq_band()`. Retrieval evaluates the `_DSM` retrieve function with an empty string parameter, validates returned buffer length, copies it into the packed local representation, then transfers count and band list into caller storage.

## State and Persistence
This file keeps only the global blocking notifier chain `wbrf_chain_head`. Frequency-band state is cached by firmware/BIOS through `_DSM`, not by this driver. Consumers that register late are expected to call retrieve to obtain the current BIOS-cached state.

## Dependencies and Integration Points
The implementation depends on ACPI companion devices, `acpi_check_dsm()`, `acpi_evaluate_dsm()`, the AMD WBRF GUID, and Linux blocking notifier chains. The expected integration is between Wi-Fi or other radio producers and RFI-sensitive consumers, with comments identifying amdgpu as a current consumer.

## Risks and Test Signals
Risk points include malformed ACPI buffers, mismatched range counts, and firmware returning non-integer or non-zero status. Retrieval checks maximum and minimum buffer length but copies the full fixed `band_list` to the caller regardless of returned count; callers must honor `num_of_ranges`. Tests should cover support probing without ACPI companion, add/remove with empty, mismatched, and valid range lists, notifier delivery only after successful firmware recording, retrieve zero-entry and multi-entry buffers, and invalid buffer lengths from mocked ACPI.
