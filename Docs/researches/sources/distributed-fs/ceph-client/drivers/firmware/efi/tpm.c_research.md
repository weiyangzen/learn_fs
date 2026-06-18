# sources/distributed-fs/ceph-client/drivers/firmware/efi/tpm.c

Purpose: Reserves EFI TPM event log memory early and calculates the TPM 2.0 final events table size so later TPM event-log consumers can safely access firmware-provided logs.

Important APIs/types/functions: `efi_tpm_final_log_size` is exported for consumers. `tpm2_calc_event_log_size()` walks a fixed number of TPM2 event records using `__calc_tpm2_event_size()`. `efi_tpm_eventlog_init()` maps the EFI TPM log table, reserves it with memblock, optionally maps/parses the final events table, reserves that memory, and records the final log size.

Control flow: If `efi.tpm_log` is absent, initialization returns success without work. Otherwise it early-maps the event log header, reserves the header plus log payload, validates final-events prerequisites, maps the final table header, calculates event payload size from the original log's algorithm info, reserves final-events memory, and unmaps temporary mappings.

State and persistence behavior: Mutates global EFI table addresses on mapping failure and writes exported `efi_tpm_final_log_size`. It reserves physical ranges in memblock but does not alter firmware logs.

Dependencies and integration points: Uses EFI configuration table addresses, early ioremap, memblock, TPM event-log parsing helpers, and TCG2 table structures. Later TPM log drivers depend on the reserved ranges staying intact.

Risks and test signals: Firmware can report malformed event sizes or unsupported formats; calculation failure returns `-EINVAL`. A notable risk is final-table `events` pointer arithmetic based on physical table address conventions. Test signals include EFI boots with TPM2 final events, malformed table injection, memblock reservation visibility, and TPM event log users seeing the expected final log length.
