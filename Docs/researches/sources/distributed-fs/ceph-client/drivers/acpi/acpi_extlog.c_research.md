# sources/distributed-fs/ceph-client/drivers/acpi/acpi_extlog.c

## Purpose
`acpi_extlog.c` implements Extended MCA Logging support. It maps firmware-provided eMCA L1 and error-log tables, opts the OS into handling, consumes error records during machine-check decode, prints or traces CPER sections, and clears firmware record status for reuse.

## Important APIs, Types, And Functions
Important structures and state include `struct extlog_l1_head`, physical/virtual L1 and elog addresses, `elog_buf`, `l1_entry_base`, and `l1_percpu_entry`. Main functions are `extlog_elog_entry_check()`, `__print_extlog_rcd()`, `print_extlog_rcd()`, `extlog_print_pcie()`, `extlog_cxl_cper_handle_prot_err()`, `extlog_print()`, `extlog_get_l1addr()`, `extlog_init()`, and `extlog_exit()`. The notifier `extlog_mce_dec` registers at `MCE_PRIO_EXTLOG`.

## Control Flow
Init verifies CPU eMCA capability through `MSR_IA32_MCG_CAP`, obtains the L1 directory physical address via a `_DSM` on `\_SB`, validates 4 KiB alignment, reserves and maps the L1 header, reads table sizes and elog base/length, reserves/maps full L1 and elog regions, allocates a 4 KiB record buffer, registers the MCE decode notifier, and sets the OS opt-in flag. On an MCE, `extlog_print()` indexes the L1 entry by physical CPU ID and bank, checks valid bits and CPER status, skips CEC-handled records, copies the record to `elog_buf`, clears firmware `block_status`, and either prints the CPER record or emits trace/nonstandard/PCIe/CXL events. Exit unregisters the notifier, clears opt-in, unmaps memory, releases regions, and frees the buffer.

## State And Persistence
Mapped firmware memory and the L1 opt-in flag are persistent while the module is loaded. Individual records are transient: copied to `elog_buf`, then firmware status is cleared. Trace events and printk output are the durable diagnostic outputs.

## Dependencies And Integration Points
It depends on x86 MCE, ACPI DSM, CPER/APEI/GHES helpers, EDAC/RAS tracepoints, optional PCIe AER and CXL CPER handlers, MSR access, and ACPI OS iomem mapping. Kconfig ties it to `X86_MCE`, local APIC, EDAC, UEFI CPER, APEI, and GHES.

## Risks
Firmware table addresses and lengths are trusted after limited validation; bad firmware can cause mapping failures or invalid record access. Rate limiting protects logs but may hide repeated corrected events. The CXL helper currently returns early when `cxl_cper_sec_prot_err_valid(prot_err)` is true, which should be reviewed against helper semantics. Correct clearing of `block_status` is important to avoid losing or repeatedly reporting records.

## Test Signals
Validation should cover systems without eMCA capability, missing/invalid DSM address, mapping reservation conflicts, valid corrected and uncorrected records, CEC-handled records, userspace RAS consumers present/absent, PCIe and CXL CPER sections, and module unload cleanup.
