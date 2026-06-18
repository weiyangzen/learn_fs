# sources/distributed-fs/ceph-client/arch/x86/boot/startup/sev-shared.c

Purpose: shared SEV/SNP/SVSM early-boot implementation included into both compressed boot and startup/runtime PI code.

Important APIs and state: provides `sev_es_terminate()`, `get_hv_features()`, `svsm_process_result_codes()`, `svsm_issue_call()`, `svsm_perform_msr_protocol()`, `snp_cpuid_get_table()`, `snp_cpuid()`, `do_vc_no_ghcb()`, `find_cc_blob_setup_data()`, `setup_cpuid_table()`, `svsm_setup_ca()`, and page-state internals including `__page_state_change()` and `pvalidate_4k_page()`. Static persistent state includes `cpuid_table_copy`, CPUID range maxima, and `sev_snp_needs_sfw`.

Control flow: termination writes GHCB MSR termination requests and halts. HV features and CPUID can use the GHCB MSR protocol. SNP CPUID handling validates firmware table entries, computes XSAVE sizes, post-processes dynamic APIC/OSXSAVE/PKE/topology values via hypervisor callbacks, and supports sparse zero leaves. The no-GHCB #VC handler only accepts CPUID, fills registers, validates SEV leaves, advances RIP, or terminates. Page-state changes pvalidate before/after GHCB PSC requests depending on shared/private direction, with SVSM-mediated PVALIDATE for non-VMPL0 guests.

Dependencies and integration: included directly into `compressed/sev.c` and startup `sev-startup.c`. Depends on GHCB MSR operations supplied by the includer, SNP CC blob structures, setup_data lists, SVSM calling area structures, CPUID helpers, and raw early interrupt/MSR primitives.

Risks and test signals: this is security-critical. CPUID table validation prevents hypervisor spoofing; page-state ordering must match SNP RMP semantics; SVSM CA setup must correctly identify VMPL0 vs non-VMPL0 via RMPADJUST. Test SEV-ES CPUID #VC before GHCB, SNP sparse CPUID tables, unsupported CPUID table entries, VMPL0 and SVSM guests, PSC failure termination, and cache-eviction mitigation when `sev_snp_needs_sfw` is set.
