# sources/distributed-fs/ceph-client/drivers/firmware/efi/cper-x86.c

Purpose: decodes IA32/x64 processor sections in UEFI CPER records, including cache, TLB, bus, micro-architectural checks, CPUID data, local APIC IDs, and register context arrays.

Important APIs/types/functions: exports `cper_print_proc_ia()`. Helpers include `cper_get_err_type()`, `print_err_info()`, `print_err_info_ms()`, and `print_bool()`. Local GUIDs identify IA error structure types and macros extract validation, operation, level, overflow, and context counts.

Control flow: `cper_print_proc_ia()` prints validated LAPIC and CPUID fields, iterates the number of error-info structures encoded in validation bits, maps each error-info GUID to a known error type, prints check-info details when valid, and outputs target/requestor/responder/IP identifiers. It then iterates context structures, prints context type and array size, handles MSR/MMIO-specific addresses, delegates MSR machine-check records to `arch_apei_report_x86_error()` when possible, and hex-dumps remaining register arrays.

State and persistence behavior: no retained state; this is a log formatter.

Dependencies and integration points: used by `cper.c` under `CONFIG_UEFI_CPER_X86` for `CPER_SEC_PROC_IA` sections. Integrates with APEI x86 machine-check reporting and shared CPER processor error strings.

Risks and test signals: record sizes are trusted more than in the ARM decoder, so malformed context counts can affect traversal. Unknown GUIDs fall back to GUID printing. Test signals include correct logs from GHES IA processor errors, MSR context handoff to x86 APEI, and graceful output for unknown error/context types.
