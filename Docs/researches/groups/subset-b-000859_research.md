# subset-b-000859 research

Work item `subset-b-000859` covers x86 confidential-computing guest support for AMD SEV/SNP and Intel TDX plus adjacent x86 accelerated crypto build and algorithm files. Each file section is bounded by exact reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/core.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/sev/core.c

## Purpose
Central runtime and early-boot implementation for AMD SEV-ES/SEV-SNP guests. It owns GHCB setup, SNP page-state transitions, AP startup through VMGEXIT or SVSM, kexec cleanup, Secure AVIC accessors, SNP guest-message setup, platform-device registration, VMPL/sysfs reporting, and Secure TSC initialization.

## Important APIs, Types, And Functions
Global state includes `sev_hv_features`, `sev_secrets_pa`, `snp_vmpl`, `ghcb_version`, `boot_ghcb`, per-CPU `runtime_data`, per-CPU `sev_vmsa`, and Secure TSC scale/offset/frequency caches. Public or cross-file APIs include `snp_set_memory_shared()`, `snp_set_memory_private()`, `snp_accept_memory()`, `snp_kexec_begin()`, `snp_kexec_finish()`, `snp_set_wakeup_secondary_cpu()`, `sev_es_setup_ap_jump_table()`, `sev_es_efi_map_ghcbs_cas()`, Secure AVIC helpers, `setup_ghcb()`, `sev_es_init_vc_handling()`, `snp_dmi_setup()`, `sev_show_status()`, `snp_msg_alloc()`, `snp_msg_init()`, `snp_msg_free()`, `snp_send_guest_request()`, `snp_secure_tsc_prepare()`, and `snp_secure_tsc_init()`.

## Control Flow And State
SNP page conversion builds `snp_psc_desc` entries, rescinds validation before shared conversion, asks the hypervisor to update RMP state via `SVM_VMGEXIT_PSC`, then validates after private conversion. If no GHCB exists, it falls back to the early MSR protocol and SVSM CAA addresses. VMSA/AP startup allocates an aligned VMSA page, initializes architectural reset fields, marks the page as VMSA via SVSM or `RMPADJUST`, then issues AP create/destroy VMGEXITs. Kexec paths first stop conversions, destroy/untag AP VMSAs, convert all shared direct-map and decrypted BSS memory back to private, then switch GHCB pages back to private last. SNP guest requests serialize on `snp_cmd_mutex`, encrypt payloads with AES-GCM using VMPCK keys and sequence numbers from the secrets page, issue GHCB guest-request VMGEXITs, retry BUSY responses, and disable the VMPCK on ambiguous firmware/host errors to avoid IV reuse.

## Dependencies And Integration
Depends on GHCB protocol helpers, `vc-shared.c` hypervisor calls, `internal.h`, SVSM helpers, RMP/PVALIDATE instructions, x86 page-table encryption APIs, memblock, CPU/APIC startup hooks, EFI page tables, platform devices (`sev-guest`, `tpm-svsm`), crypto AES-GCM, and UAPI SNP guest request structures.

## Risks And Test Signals
High-risk areas are GHCB availability during early boot, IRQ-disabled per-CPU GHCB usage, PSC descriptor retry semantics, 2M-to-4K PVALIDATE fallback, cache-coherency mitigation ordering, VMSA page tagging leaks, Secure TSC termination behavior, kexec shared-memory accounting, and VMPCK sequence-number handling. Signals include SEV-ES/SNP boot, AP hotplug and kexec/kdump tests, SNP guest driver attestation/TSC requests, Secure AVIC paths, EFI runtime with GHCB mappings, sysfs VMPL exposure, and crypto selftests for guest-message AES-GCM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/internal.h -->
# sources/distributed-fs/ceph-client/arch/x86/coco/sev/internal.h

## Purpose
Private SEV/SNP CoCo header shared by core, noinstr, VC handling, and SVSM code. It defines the per-CPU GHCB runtime state, cross-file globals, internal prototypes, GHCB MSR accessors, SVSM CAA selectors, and fatal PVALIDATE handling.

## Important APIs, Types, And Functions
`struct sev_es_runtime_data` contains the active GHCB page, backup GHCB for nested #VC/NMI cases, activity flags, and cached DR7. `struct ghcb_state` records whether a backup GHCB was used. The header declares per-CPU `runtime_data`, `sev_vmsa`, `svsm_caa`, and `svsm_caa_pa`, plus `sev_hv_features`, `sev_secrets_pa`, `boot_svsm_ca_page`, and `boot_svsm_caa_pa`. Inline helpers include `sev_es_rd_ghcb_msr()`, `sev_es_wr_ghcb_msr()`, `svsm_get_caa()`, `svsm_get_caa_pa()`, and `__pval_terminate()`.

## Control Flow And State
The header itself is declarative, but it encodes the core state model: GHCBs can be boot-time or per-CPU runtime resources; nested GHCB use must save/restore through `ghcb_state`; SVSM CAA selection switches from boot CAA to per-CPU CAA when `sev_cfg.use_cas` is enabled; and unrecoverable PVALIDATE failures terminate the guest.

## Dependencies And Integration
It depends on x86 SEV/GHCB definitions, native MSR access, per-CPU storage, and SNP/SVSM structures exposed through architecture headers. It is included by all SEV files in this subset, so changing field layout or inline semantics affects VC exception entry, page-state conversion, SVSM calls, Secure AVIC, and SNP guest messaging.

## Risks And Test Signals
Risks include struct layout assumptions for page alignment, missing IRQ-disabled constraints around `__sev_get_ghcb()`, DR7 cache semantics, and boot-vs-runtime CAA address selection. Compile coverage with `CONFIG_AMD_MEM_ENCRYPT`, SEV-ES boot with NMI/#VC nesting, SVSM boot, and PVALIDATE failure injection are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/noinstr.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/sev/noinstr.c

## Purpose
Noinstr-safe low-level support for SEV-ES #VC handling. It protects the #VC IST stack during NMI nesting, notifies the hypervisor when NMI handling is complete, and arbitrates per-CPU GHCB ownership without instrumentation.

## Important APIs, Types, And Functions
`__sev_es_ist_enter()` and `__sev_es_ist_exit()` adjust and restore the VC IST entry when NMI hits an active #VC stack. `__sev_es_nmi_complete()` sends `SVM_VMGEXIT_NMI_COMPLETE`. `__sev_get_ghcb()` returns the active GHCB and optionally saves current contents into `backup_ghcb`; `__sev_put_ghcb()` restores or invalidates it. `on_vc_stack()` identifies kernel-mode stack frames in the VC IST range.

## Control Flow And State
The GHCB acquisition path requires interrupts disabled. Before runtime GHCB initialization it returns `boot_ghcb`. After initialization it marks the per-CPU GHCB active. If a nested #VC occurs, the original GHCB content is copied to `backup_ghcb` and later restored. A second nested use with both GHCBs active panics after clearing flags to preserve panic output ability. IST enter always stores the old IST below the new top so exit can unroll unconditionally.

## Dependencies And Integration
Depends on TSS/IST layout, per-CPU `runtime_data`, GHCB invalidation helpers, VMGEXIT, native physical-address macros safe for noinstr paths, and NMI entry code. Runtime #VC handlers in `vc-handle.c` and core GHCB setup rely on these functions.

## Risks And Test Signals
Risks are recursive instrumentation, stack overwrite under NMI/#VC nesting, invalid GHCB reuse, and incorrect interrupt-state assumptions. Signals include objtool/noinstr validation, SEV-ES boot under tracing-disabled paths, NMI storm tests, nested #VC cases such as NMI over MMIO/MSR emulation, and panic-path output when GHCB backup exhaustion is forced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/noinstr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/svsm.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/sev/svsm.c

## Purpose
SVSM support for SEV-SNP guests running above VMPL0. It implements GHCB/MSR call routing to the Secure VM Service Module, SVSM-assisted PVALIDATE batching, SVSM attestation requests, and SVSM vTPM probing/command forwarding.

## Important APIs, Types, And Functions
Exports `snp_issue_svsm_attest_req()`, `snp_svsm_vtpm_send_command()`, and `snp_svsm_vtpm_probe()`. Internal entry points include `svsm_perform_call_protocol()`, `svsm_perform_ghcb_protocol()`, `svsm_pval_pages()`, `svsm_build_ca_from_psc_desc()`, and `svsm_build_ca_from_pfn_range()`. Persistent state consists of `boot_svsm_ca_page`, `boot_svsm_caa_pa`, and per-CPU `svsm_caa`/`svsm_caa_pa`.

## Control Flow And State
Call protocol disables interrupts, chooses the runtime GHCB, boot GHCB, or early MSR protocol, then retries `-EAGAIN` SVSM results. GHCB protocol populates protocol metadata, emits `SVM_VMGEXIT_SNP_RUN_VMPL`, issues `svsm_issue_call()`, verifies exception information, and converts SVSM result codes. PVALIDATE builds up to `SVSM_PVALIDATE_MAX_COUNT` entries in the CAA buffer, invokes core call ID 1, stores failed 2M entries that need 4K fallback, and terminates on unrecoverable failure. Attestation copies the input request to the CAA buffer and propagates returned buffer lengths from output registers. vTPM probe requires nonzero `snp_vmpl`, performs `SVSM_VTPM_QUERY`, and checks TPM command bit 8.

## Dependencies And Integration
Integrates with `internal.h`, GHCB exception verification from `vc-shared.c`, SVSM call ABI definitions, SNP PSC descriptors, vTPM driver registration in `core.c`, and exported attestation/vTPM consumers.

## Risks And Test Signals
Risks include early-boot address-mode confusion between boot and per-CPU CAAs, stale interrupt state, CAA buffer overwrite, 2M fallback array bounds, incorrect length propagation for attestation, and accepting SVSM availability without `snp_vmpl`. Signals include SVSM guest boot, page-state transitions at VMPL1+, attestation ioctl paths, tpm-svsm device creation, and negative tests for missing SVSM or unsupported vTPM command bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/svsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/vc-handle.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/sev/vc-handle.c

## Purpose
Runtime and early #VC exception handling for SEV-ES/SNP guests. It decodes intercepted instructions, performs GHCB hypervisor calls, emulates MMIO and port I/O, handles CPUID/MSR/TSC/debug-register cases, and dispatches kernel/user #VC entry behavior.

## Important APIs, Types, And Functions
External entry points include `__vc_handle_msr()`, `vc_forward_exception()`, `exc_vmm_communication` IDT handlers, and `handle_vc_boot_ghcb()`. Important helpers are `vc_decode_insn()`, `vc_read_mem()`, `vc_write_mem()`, `vc_handle_mmio()`, `vc_do_mmio()`, `vc_handle_dr7_read/write()`, `vc_handle_rdpmc()`, `vc_handle_vmmcall()`, `vc_handle_exitcode()`, `vc_raw_handle_exception()`, and Secure TSC/SVSM CAA MSR handlers. It also includes `vc-shared.c`, binding shared emulation helpers to runtime memory and logging primitives.

## Control Flow And State
The raw handler obtains a GHCB, invalidates it, initializes an emulation context, validates opcode bytes, dispatches by SVM exit code, releases the GHCB, then either advances RIP, forwards a real exception, retries, terminates, or signals user space. Kernel #VC runs in NMI-entry context and terminates/panics on unsupported hypervisor communication. User #VC runs in IRQ context and raises SIGBUS on unrecoverable emulation. MMIO handling translates guest virtual addresses through current CR3, rejects encrypted mappings, uses GHCB shared buffer, and handles string MOVS by splitting into ordinary memory accesses. MSR handling has special cases for SVSM CAA, Secure TSC, and Secure AVIC.

## Dependencies And Integration
Depends on x86 instruction decoding, exception forwarding, GHCB helpers, SNP CPUID table logic, EFI memory-mode detection, FPU/XCR helpers, IO bitmap checks, APIC/Secure AVIC integration, and architecture IDT macros.

## Risks And Test Signals
Risks include incorrect instruction-length advancement, unsafe user/EFI instruction decoding, encrypted MMIO rejection, nested string-instruction #VC recursion, Secure TSC intercept termination, DR7 debug-swap semantics, and kernel #VC from invalid stack context. Signals include SEV-ES boot, MMIO/PIO-heavy drivers, EFI runtime calls, userspace I/O permission tests, CPUID table tests, debug/NMI paths, and objtool coverage for entry/exit constraints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/vc-handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/vc-shared.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/sev/vc-shared.c

## Purpose
Shared SEV-ES #VC emulation code included by both normal kernel and early/compressed contexts. It validates intercepted opcode bytes, initializes/finishes emulation contexts, handles port I/O, verifies GHCB exception information, performs GHCB hypervisor calls, handles CPUID/RDTSC, registers GHCBs, and negotiates GHCB protocol.

## Important APIs, Types, And Functions
Key functions are `vc_check_opcode_bytes()`, `vc_init_em_ctxt()`, `vc_finish_insn()`, `vc_ioio_exitinfo()`, `vc_handle_ioio()`, `verify_exception_info()`, `sev_es_ghcb_hv_call()`, `vc_handle_cpuid()`, `vc_handle_rdtsc()`, `snp_register_ghcb_early()`, `sev_es_check_cpu_features()`, and `sev_es_negotiate_protocol()`. The file relies on includer-provided `vc_decode_insn()`, `vc_read_mem()`, `vc_write_mem()`, `vc_ioio_check()`, `sev_printk`, and feature macros.

## Control Flow And State
For decode-required exits, the shared code decodes the instruction and checks that opcode bytes match the hardware-reported exit code. Port I/O builds GHCB exit-info fields for scalar and string I/O, chunks repeated string operations through the GHCB shared buffer, updates RSI/RDI/RCX according to direction and REP, and returns `ES_RETRY` until complete. GHCB calls populate protocol metadata and exit fields, execute VMGEXIT, then interpret `sw_exit_info_1/2` as success, forwarded #GP/#UD, or VMM error. CPUID uses SNP CPUID tables first, falling back to GHCB CPUID with XCR0/XSS inputs; RDTSC/RDTSCP are rejected under Secure TSC.

## Dependencies And Integration
Included by `vc-handle.c` and boot/compressed SEV code. It depends on GHCB field accessors, SVM exit-code definitions, x86 instruction decoder, SNP CPUID validation, native MSR/VMGEXIT primitives, and exception metadata formats.

## Risks And Test Signals
Risks include opcode/exit mismatches, IOIO bitfield errors, off-by-one REP string state, trusting invalid GHCB output-valid bits, CPUID hypervisor fallback bypassing SNP policy, and GHCB protocol version negotiation failures. Signals include SEV-ES early and runtime boot, port I/O console tests, CPUID conformance, GHCB registration under SNP, Secure TSC intercept tests, and negative VMM response tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/sev/vc-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/Makefile

## Purpose
Build manifest for x86 Intel TDX guest support under `arch/x86/coco/tdx`.

## Important APIs, Types, And Functions
No runtime APIs are defined here. The manifest unconditionally adds `debug.o`, `tdcall.o`, `tdx.o`, and `tdx-shared.o` to `obj-y` when the directory is selected by the surrounding kernel build.

## Control Flow And State
The Makefile has no control flow beyond kbuild object composition. It keeps assembly TDCALL wrappers, shared memory acceptance/hypercall code, debug attribute printing, and main TDX guest logic in one linked unit.

## Dependencies And Integration
Depends on parent Kconfig/build selection for TDX guest code and on each listed object compiling with matching symbols: `tdx.o` consumes `__tdcall*` and `tdx_accept_memory()`, while debug helpers are called during TDX announcement.

## Risks And Test Signals
Risks are omitted objects causing unresolved symbols or dead TDX functionality. Signals are allyesconfig/allmodconfig x86 builds and TDX guest boot reaching `tdx_early_init()` and attribute reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/debug.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/debug.c

## Purpose
Initialization-time debug reporting for TDX TD attributes and TD controls. It translates known metadata bits into names for boot logs.

## Important APIs, Types, And Functions
`tdx_dump_attributes()` prints recognized `TDX_TD_ATTR_*` bits and any unknown remainder. `tdx_dump_td_ctls()` prints recognized `TD_CTLS_*` bits and unknown remainder. Static string tables are indexed by bit number using `DEF_TDX_TD_ATTR_NAME()` and `DEF_TD_CTLS_NAME()`.

## Control Flow And State
Both functions iterate over sparse name arrays, print names for set known bits, clear consumed bits from the local copy, and print a hex unknown mask for remaining bits. State is read-only `__initdata`; there is no persistence after init.

## Dependencies And Integration
Depends on `<asm/tdx.h>` bit definitions and printk. `tdx_announce()` in `tdx.c` invokes these helpers after `TDG_VP_INFO` and `TDCS_TD_CTLS` reads.

## Risks And Test Signals
Risks are stale bit names, array indexes that no longer match architecture definitions, and misleading unknown masks. Signals are TDX guest boot logs on debug and non-debug TDs, plus compile failures when TDX bit definitions change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdcall.S -->
# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdcall.S

## Purpose
Assembly wrappers for TDX guest TDCALL and TDVMCALL operations. They provide C-callable noinstr entry points around the shared `TDX_MODULE_CALL` macro.

## Important APIs, Types, And Functions
Defines `__tdcall()`, `__tdcall_ret()`, and `__tdcall_saved_ret()`. The first issues a TDX module call without saving output registers, the second saves RCX/RDX/R8-R11 outputs to `struct tdx_module_args`, and the third saves all argument registers for TDVMCALL-style interactions. Inputs are passed as leaf ID in RDI and args pointer in RSI.

## Control Flow And State
Each wrapper moves the leaf into RAX via the macro implementation, exposes the configured register set, executes TDCALL, and returns the status in RAX or the TDVMCALL error path convention. The file lives in `.noinstr.text`, so it avoids instrumentation and must preserve ABI expectations exactly.

## Dependencies And Integration
Includes `../../virt/vmx/tdx/tdxcall.S` for the macro body and depends on offsets for `struct tdx_module_args`. `tdx.c` and `tdx-shared.c` rely on these wrappers for TD metadata reads/writes, #VE info retrieval, memory acceptance, attestation, and hypercalls.

## Risks And Test Signals
Risks are register ABI drift, CFI/unwind mismatch, noinstr violations, and incorrect saved-register masks exposing private state to the VMM. Signals are objtool validation, TDX guest boot, TDREPORT/RTMR calls, TDVMCALL failures, and low-level ABI tests around all output registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdcall.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdx-shared.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdx-shared.c

## Purpose
Shared TDX helpers for accepting private memory and issuing TDVMCALL hypercalls. This code is small enough to be shared with early contexts.

## Important APIs, Types, And Functions
`tdx_accept_memory()` accepts a physical range using `TDG_MEM_PAGE_ACCEPT`, trying 1G, then 2M, then 4K chunks through `try_accept_one()`. `__tdx_hypercall()` wraps `__tdcall_saved_ret(TDG_VP_VMCALL)` and returns the TDVMCALL leaf status from R10.

## Control Flow And State
Memory acceptance advances `start` only when a module call succeeds for an aligned chunk. If no page size succeeds, it returns false and leaves the remaining range unaccepted. Hypercall setup overwrites `args->rcx` with the shared-register exposure mask, treats failure of the TDCALL mechanism itself as fatal via `__tdx_hypercall_failed()`, and otherwise returns the VMM-provided leaf result.

## Dependencies And Integration
Depends on `__tdcall()` and `__tdcall_saved_ret()` from `tdcall.S`, TDX leaf IDs, page-level sizing, and `cc_mkdec()/cc_mkenc()` users in `tdx.c`. `tdx_enc_status_changed()` calls `tdx_accept_memory()` for shared-to-private conversion; most TDX emulation paths call `__tdx_hypercall()`.

## Risks And Test Signals
Risks include alignment mistakes, accepting only part of a range, interpreting module failure as VMM leaf failure, and wrong RCX exposure mask. Signals include memory hotplug/acceptance tests, shared-private conversion tests, TDX boot on systems supporting large SEPT pages, and TDVMCALL error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdx-shared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdx.c -->
# sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdx.c

## Purpose
Main Intel TDX guest implementation. It detects TDX, configures CoCo masks and TD controls, emulates #VE exits, provides TDX attestation/quote helpers, handles shared/private page conversion callbacks, and prepares safe halt/kexec behavior.

## Important APIs, Types, And Functions
Exports `tdx_kvm_hypercall()` when KVM guest support is enabled, `tdx_mcall_get_report0()`, `tdx_mcall_extend_rtmr()`, `tdx_hcall_get_quote()`, `tdx_get_ve_info()`, `tdx_handle_virt_exception()`, `tdx_halt()`, `tdx_early_handle_ve()`, and `tdx_early_init()`. Important internals include `tdcall()`, `tdg_vm_rd()`, `tdg_vm_wr()`, `tdx_setup()`, `disable_sept_ve()`, `reduce_unnecessary_ve()`, `handle_mmio()`, `handle_io()`, `read_msr()`, `write_msr()`, `handle_cpuid()`, `tdx_map_gpa()`, and kexec callbacks.

## Control Flow And State
Early init checks the TDX CPUID signature, forces TDX/TSC capabilities, reads TD info to derive the shared-bit mask, disables unwanted notifications and SEPT #VE where possible, reduces unnecessary #VEs, updates `physical_mask`, installs encryption conversion callbacks, replaces halt pv_ops, disables parallel CPU bringup, and logs TD metadata. #VE handling retrieves VEINFO immediately, dispatches user CPUID-only handling or kernel HLT/MSR/CPUID/MMIO/IO handling, and advances RIP by decoded or module-provided length. Page conversion maps GPA ranges through TDVMCALL MapGPA, accepts memory on shared-to-private, and accounts shared pages in `nr_shared`. Kexec finish walks the direct map, clears shared PTEs, converts pages private, flushes TLBs, and reports accounting mismatch.

## Dependencies And Integration
Integrates TDX module calls, GHCI TDVMCALL ABI, x86 CoCo vendor/mask APIs, paravirt halt hooks, set-memory encryption callbacks, instruction decoder/MMIO helpers, kexec, KVM hypercall export, and TDX guest driver attestation APIs.

## Risks And Test Signals
Risks include leaving SEPT #VE enabled, private GPA EPT violations, unsafe HLT with interrupts enabled, user-mode #VE beyond CPUID, MMIO instruction split-page handling, MapGPA retry validation, shared-page accounting drift, and kexec with leftover shared mappings. Signals include TDX guest boot, TD quote/report/RTMR tests, MMIO/PIO drivers, CPUID hypervisor leaves, suspend/idle halt behavior, kexec/kdump, and set_memory decrypted/encrypted stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/coco/tdx/tdx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/Kconfig

## Purpose
Kconfig menu for x86 accelerated cryptographic algorithms. It exposes selectable CPU-specific cipher and AEAD implementations and declares their architecture and crypto-core dependencies.

## Important APIs, Types, And Functions
This is configuration rather than code. Symbols include `CRYPTO_AES_NI_INTEL`, Blowfish/Camellia/CAST/Serpent/SM4/Twofish/ARIA accelerated variants, and `CRYPTO_AEGIS128_AESNI_SSE2`. Dependencies gate 64-bit-only implementations, while `select` and `imply` pull in crypto API, common cipher, mode, and library support such as `CRYPTO_AEAD`, `CRYPTO_SKCIPHER`, `CRYPTO_LIB_AES`, `CRYPTO_LIB_GF128MUL`, `CRYPTO_SM4`, and `CRYPTO_ARIA`.

## Control Flow And State
The menu determines which modules or built-in objects the Makefile can build. It does not perform CPU feature runtime checks itself; those are handled in glue modules. The help text documents expected instruction-set prerequisites and parallel block counts.

## Dependencies And Integration
Feeds `arch/x86/crypto/Makefile`, the kernel crypto API, module aliasing, and architecture feature-specific glue code. `CRYPTO_AES_NI_INTEL` enables AES-NI/VAES implementations including CTR, XCTR, XTS, and GCM assembly in this work item. `CRYPTO_AEGIS128_AESNI_SSE2` enables the AEGIS glue and assembly pair.

## Risks And Test Signals
Risks include missing `select` dependencies, enabling x86_64-only code on 32-bit builds, stale feature descriptions, and inadvertently selecting mode helpers with recursive dependency issues. Signals are Kconfig dependency checks, randconfig/allmodconfig builds, module load tests, and crypto selftests under each enabled symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/Makefile

## Purpose
Kbuild manifest mapping x86 crypto Kconfig symbols to object modules and their glue/assembly components.

## Important APIs, Types, And Functions
No runtime APIs are defined. Important object groupings include `aegis128-aesni-y := aegis128-aesni-asm.o aegis128-aesni-glue.o` and `aesni-intel-$(CONFIG_64BIT)` adding `aes-ctr-avx-x86_64.o`, `aes-gcm-aesni-x86_64.o`, VAES GCM variants, and AES-XTS AVX code to the AES-NI module.

## Control Flow And State
Kbuild uses `obj-$(CONFIG_...)` to include modules and `*-y` variables to compose multi-object modules. This file preserves source/module boundaries: common glue objects register algorithms, while architecture assembly objects provide hot paths.

## Dependencies And Integration
Consumes Kconfig symbols from `Kconfig`, integrates with the kernel crypto module build, and defines link composition that glue C files depend on for external assembly symbols.

## Risks And Test Signals
Risks are missing assembly objects for declared glue symbols, incorrect module grouping causing duplicate or unresolved exports, and 64-bit object leakage into 32-bit builds. Signals include x86 randconfig builds, module link tests, `modprobe` of AES-NI and AEGIS modules, and crypto selftests verifying registered driver names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aegis128-aesni-asm.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aegis128-aesni-asm.S

## Purpose
AES-NI/SSE4.1 assembly implementation of the AEGIS-128 AEAD primitive. It provides state initialization, associated-data absorption, encryption/decryption, tail handling, and tag finalization for the C glue.

## Important APIs, Types, And Functions
Defines `aegis128_aesni_init()`, `aegis128_aesni_ad()`, `aegis128_aesni_enc()`, `aegis128_aesni_dec()`, `aegis128_aesni_enc_tail()`, `aegis128_aesni_dec_tail()`, and `aegis128_aesni_final()`. Macros `aegis128_update`, `load_partial`, `store_partial`, `encrypt_block`, and `decrypt_block` implement the repeated AESENC-based state transform and partial-block I/O.

## Control Flow And State
The state is five XMM blocks. Initialization mixes key, IV, and two constants through ten update rounds. AD and crypt loops process five blocks per unrolled iteration, rotating the logical state by storing different XMM registers on each exit path. Encryption computes keystream from state words, writes ciphertext, updates state with plaintext; decryption reverses keystream use and updates with plaintext. Tail decrypt masks unused bytes before state absorption. Finalization injects bit lengths, runs seven updates, XORs all state blocks into the caller-provided tag buffer.

## Dependencies And Integration
Called only under `kernel_fpu_begin()` from `aegis128-aesni-glue.c`. Requires AES-NI and SSE4.1 instructions, x86_64 ABI register conventions, and 16-byte-aligned constants.

## Risks And Test Signals
Risks include partial load/store overlap errors, tail decrypt authentication mismatch, state rotation mistakes, length block bit-count errors, ABI clobbering, and missing FPU protection in callers. Signals include AEGIS known-answer tests across AD/plaintext tail sizes, in-place encryption/decryption, truncated tags, crypto fuzzing, and SIMD register state tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aegis128-aesni-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aegis128-aesni-glue.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aegis128-aesni-glue.c

## Purpose
C glue registering the AES-NI/SSE4.1 AEGIS-128 AEAD implementation with the kernel crypto API. It handles scatterlists, FPU ownership, key/authsize validation, tag placement, and module lifecycle.

## Important APIs, Types, And Functions
Defines `struct aegis_block`, `struct aegis_state`, and `struct aegis_ctx`, declares the assembly routines, and registers `crypto_aegis128_aesni_alg`. Key functions are `crypto_aegis128_aesni_setkey()`, `crypto_aegis128_aesni_setauthsize()`, `crypto_aegis128_aesni_encrypt()`, `crypto_aegis128_aesni_decrypt()`, `crypto_aegis128_aesni_crypt()`, `crypto_aegis128_aesni_process_ad()`, and `crypto_aegis128_aesni_process_crypt()`.

## Control Flow And State
Setkey stores a 16-byte key in aligned context. Encrypt/decrypt set up a skcipher walk, enter kernel FPU context, initialize assembly state, absorb AD from scatterlists with zero-padded final AD block, process full blocks and tails, finalize the tag, and leave FPU context around `skcipher_walk_done()` calls. Encryption writes the produced tag after ciphertext. Decryption preloads the transmitted tag, finalizes by XORing computed tag into it, and returns `-EBADMSG` when any authenticated byte differs from zero.

## Dependencies And Integration
Depends on crypto AEAD/skcipher internals, scatterwalk helpers, module registration, CPU feature checks for AES/SSE4.1/SSE xfeatures, and the assembly symbols from `aegis128-aesni-asm.S`.

## Risks And Test Signals
Risks include scatterlist boundary buffering, FPU begin/end imbalance, authsize limits, context alignment, tag comparison length, and cryptlen underflow if callers violate AEAD decrypt contract. Signals include `tcrypt`/crypto manager selftests, random scatterlist layouts, all auth sizes 8-16, empty AD/plaintext cases, CPU feature gating, and module unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aegis128-aesni-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-ctr-avx-x86_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aes-ctr-avx-x86_64.S

## Purpose
x86_64 assembly implementations of AES-CTR and AES-XCTR for AES-NI+AVX, VAES+AVX2, and VAES+AVX512BW/VL+BMI2 CPUs. It supplies high-throughput length-preserving stream encryption/decryption for AES glue.

## Important APIs, Types, And Functions
Exports `aes_ctr64_crypt_aesni_avx()`, `aes_xctr_crypt_aesni_avx()`, `aes_ctr64_crypt_vaes_avx2()`, `aes_xctr_crypt_vaes_avx2()`, `aes_ctr64_crypt_vaes_avx512()`, and `aes_xctr_crypt_vaes_avx512()`. The `_aes_ctr_crypt` macro generates all functions for vector lengths 16, 32, and 64 bytes. Helper macros abstract vector moves, XORs, broadcast, partial-block load/store, counter preparation, AES rounds, and tail XOR.

## Control Flow And State
The functions load AES key length and round keys from `struct crypto_aes_ctx`, broadcast the initial counter or XCTR IV, generate counter vectors, AES-encrypt them, XOR keystream with source, and store destination. Main loops process eight vectors at a time. Tail paths generate enough keystream for the remaining bytes, handle full vectors first, then use masked AVX512 stores or scalar overlapping partial loads/stores for sub-vector tails. CTR uses big-endian block counters but leaves carry handling and counter writeback to the caller; XCTR uses little-endian counter semantics starting from the provided scalar counter.

## Dependencies And Integration
Built into the AES-NI module on 64-bit. Requires callers to select functions based on CPU features, manage kernel FPU/SIMD state, split CTR at low-64-bit carry boundaries, and update multi-part counters externally.

## Risks And Test Signals
Risks include counter endian mistakes, missing carry splitting in callers, incorrect AES round-key pointer math for AES-128/192/256, AVX/SSE transition issues, partial-block overwrite, and CFI prototype mismatch. Signals include AES CTR/XCTR known-answer tests, non-multiple lengths 1-15 and around vector boundaries, in-place operation, AES key sizes, AVX2/AVX512 CPU feature dispatch, and SIMD state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-ctr-avx-x86_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-aesni-x86_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-aesni-x86_64.S

## Purpose
AES-NI/PCLMULQDQ x86_64 assembly implementation of AES-GCM for CPUs with SSE4.1 or AVX. It provides GHASH precomputation, AAD update, encrypt/decrypt update, and final tag generation/verification.

## Important APIs, Types, And Functions
Exports non-AVX and AVX variants: `aes_gcm_precompute_aesni[_avx]()`, `aes_gcm_aad_update_aesni[_avx]()`, `aes_gcm_enc_update_aesni[_avx]()`, `aes_gcm_dec_update_aesni[_avx]()`, `aes_gcm_enc_final_aesni[_avx]()`, and `aes_gcm_dec_final_aesni[_avx]()`. Macros implement PCLMUL abstraction, byte swap, partial block load/store, single-block GHASH multiply, Karatsuba multi-block GHASH, 8-block CTR generation, update loops, and final tag logic.

## Control Flow And State
Precompute encrypts zero to obtain H, byte-reflects and adjusts it for GHASH arithmetic, stores H powers H^1..H^8, XORed halves, and H*x^64 in `struct aes_gcm_key_aesni`. AAD update GHASHes full and partial AAD blocks. Encrypt/decrypt update loads the little-endian counter and GHASH accumulator, processes 8-block chunks by interleaving AES rounds and GHASH multiplication, then handles 1-block and partial tails. Encryption GHASHes ciphertext after producing it; decryption GHASHes source ciphertext before/while writing plaintext. Final builds the length block, multiplies by H, AES-encrypts counter block 1, returns the tag for encryption or constant-time compares a truncated tag for decryption.

## Dependencies And Integration
Integrated into `aesni-intel.o`; callers provide an expanded key layout with offsets matching this file, manage FPU/SIMD state, buffer non-final updates to multiples of 16 where required, and dispatch based on AES/PCLMUL/SSE4.1 or AVX features.

## Risks And Test Signals
Risks include key-struct offset drift, GHASH bit-reflection/reduction errors, AES key-length branch mistakes, counter increment overflow, partial final block masking, constant-time tag check regressions, and AVX/non-AVX macro divergence. Signals include AES-GCM known-answer tests for all key sizes, AAD-only and plaintext-only cases, truncated tags 4-16 bytes, in-place decrypt, unaligned buffers, cross-boundary lengths around 16 and 128 bytes, and crypto fuzz tests versus generic GCM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-aesni-x86_64.S -->
