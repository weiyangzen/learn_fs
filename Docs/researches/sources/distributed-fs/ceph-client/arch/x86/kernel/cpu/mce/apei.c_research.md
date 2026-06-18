# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/mce/apei.c

Purpose: bridges ACPI APEI/GHES/ERST hardware error reporting with the x86 MCE logging format.

Important APIs and flow: `apei_mce_report_mem_error()` converts CPER memory errors with physical addresses into synthetic `struct mce` records and queues them with severity-dependent UC/PCC bits. `apei_smca_report_x86_error()` imports SMCA register arrays from CPER processor context, maps the LAPIC ID to a CPU, decodes fixed SMCA register layout fields, and logs the record. `apei_write_mce()` serializes a fatal MCE into a CPER record and writes it to ERST. `apei_read_mce()`, `apei_check_mce()`, and `apei_clear_mce()` support legacy mcelog reads of persistent records after reboot.

State and persistence: normal GHES reports are queued in memory through MCE logging. Fatal records can persist across reboot in ERST until read and cleared.

Dependencies and integration: depends on ACPI APEI, GHES, CPER structures, ERST storage, common MCE prep/log helpers, and SMCA feature checks.

Risks and test signals: address-mask handling and SMCA register-count validation are key correctness points. Signals include GHES corrected-memory reports appearing as MCE records, ERST write/read/clear behavior after fatal MCE, and BERT/CPER SMCA import tests with valid and invalid register layouts.
