## sources/distributed-fs/ceph-client/arch/x86/boot/compressed/mem_encrypt.S

### Purpose
`compressed/mem_encrypt.S` supplies early assembly support for AMD SME/SEV before the full decompressor C environment and SEV runtime are ready.

### Important APIs, Types, And Functions
Exported symbols include `get_sev_encryption_bit`, `startup32_load_idt`, `startup32_check_sev_cbit`, `sme_me_mask`, `sev_status`, and `sev_check_data`. Local helpers include `sev_es_req_cpuid`, `startup32_vc_handler`, and `startup32_set_idt_entry`. It also includes `sev_verify_cbit.S` for 64-bit verification.

### Control Flow
`get_sev_encryption_bit()` uses CPUID leaf `0x8000001f` and `MSR_AMD64_SEV` to return the active encryption C-bit position or zero. `startup32_vc_handler()` handles early SEV-ES #VC CPUID exits through the GHCB MSR protocol, validates critical CPUID responses, skips the trapped CPUID instruction, or terminates the guest. `startup32_load_idt()` installs that #VC handler into a small 32-bit IDT. `startup32_check_sev_cbit()` writes RDRAND values while paging is disabled, enables paging with the selected C-bit, compares memory against registers, and halts if the encryption bit is wrong.

### State, Persistence, And Dependencies
Persistent early state includes `sme_me_mask`, `sev_status`, the temporary 32-bit IDT, and C-bit check data. Dependencies include CPUID, MSRs, GHCB MSR protocol, RDRAND, boot GDT selectors, trap numbers, and the 64-bit SEV verification include.

### Integration Points
`head_64.S` calls these routines while building encrypted page tables and before entering long-mode decompressor code. Later C SEV code reads and refines `sev_status` and `sme_me_mask`.

### Risks
This code runs before ordinary exception handling. Bad C-bit selection makes memory unreadable and intentionally halts. The early #VC handler only supports CPUID exits needed during startup; unexpected exits terminate the guest.

### Test Signals
Boot SME, SEV, SEV-ES, and SEV-SNP guests through the 32-bit entry path, test hypervisor CPUID response validation, verify C-bit mismatch failure under instrumentation, and boot non-SEV systems where the routines return zero/no-op.
