
# sources/distributed-fs/ceph-client/drivers/firmware/efi/libstub/tpm.c

Purpose: handles EFI reset-attack mitigation and copies TPM2/TCG1.2/Confidential Computing event logs into a Linux EFI configuration table for the kernel.

Important APIs/types/functions: conditionally exports `efi_enable_reset_attack_mitigation()` and always exports `efi_retrieve_eventlog()`. Internal `efi_retrieve_tcg2_eventlog()` calculates event-log size and handles final-events-table accounting.

Control flow: reset mitigation checks the MemoryOverwriteRequestControl variable and sets it to request memory clearing on next reboot. Event-log retrieval first tries TCG2 protocol with TCG2 format, falls back to TCG1.2 format, or uses the CC measurement protocol. It calculates the final entry size, optionally totals preboot final events, allocates ACPI reclaim memory, copies the log, records version and sizes, and installs `LINUX_EFI_TPM_EVENT_LOG_GUID`.

State and persistence behavior: the copied event log persists as an EFI configuration table. Reset mitigation writes a nonvolatile/runtime EFI variable when supported.

Dependencies and integration points: depends on EFI TCG2, EFI CC Measurement Protocol, TPM event-log size helpers, final events tables, EFI variables, and configuration-table install. Common and x86 stubs call it before ExitBootServices.

Risks and test signals: malformed event logs can produce zero event sizes; firmware may return only last-entry pointers; final-events parsing depends on the first log entry's algorithms. Test signals include TPM2 logs, TCG1.2 fallback, CC logs, empty logs, final-events preboot size, allocation failure, and MemoryOverwriteRequestControl behavior.
