# sources/distributed-fs/ceph-client/drivers/firmware/efi/cper-arm.c

Purpose: decodes and prints ARM processor sections in UEFI Common Platform Error Records for APEI/GHES/RAS diagnostics.

Important APIs/types/functions: exports `cper_print_proc_arm()`. Internal string tables describe ARM register contexts, transaction types, cache/TLB/bus operations, bus participation, and address spaces. `cper_print_arm_err_info()` decodes validation-bit-controlled ARM error-info fields.

Control flow: `cper_print_proc_arm()` prints MIDR and optional MPIDR, affinity, and running state fields, validates that `section_length` fits within the CPER payload, then iterates error-info structures and context-info structures. Error types are converted through `cper_bits_to_str()` and further decoded for cache, TLB, and bus records. Context register payloads are hex-dumped after type and length validation; any remaining bytes are treated as vendor-specific data.

State and persistence behavior: no persistent state; output goes to kernel logs.

Dependencies and integration points: called from `cper.c` when a CPER section GUID matches `CPER_SEC_PROC_ARM` and ARM/ARM64 support is enabled. Depends on CPER structures, printk, hex dump, and shared CPER error-type strings.

Risks and test signals: malformed firmware records can claim impossible section lengths or invalid context types; the code detects these and stops decoding. Test signals are readable GHES/BERT logs for ARM processor records, graceful handling of short sections, and correct bus/cache/TLB field decoding under synthetic CPER records.
