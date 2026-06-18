# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/sev.c

## Purpose
`sev.c` implements AMD SEV, SEV-ES, and SEV-SNP support for KVM SVM. It manages encrypted-guest feature enablement, ASID allocation/recycling, firmware command dispatch, launch/update/measurement flows, migration and mirrored encryption contexts, encrypted memory registration, SEV-ES GHCB exits, SNP guest requests, AP creation, RMP transitions, guest_memfd private memory integration, VMSA encryption/decryption, and hardware setup/teardown.

## Important APIs, types, and functions
- Feature and ASID management: `sev_hardware_setup()`, `sev_hardware_unsetup()`, `sev_set_cpu_caps()`, `sev_asid_new()`, `sev_alloc_asid()`, `sev_asid_free()`, `sev_flush_asids()`, and `__sev_recycle_asids()`.
- VM lifecycle: `sev_vm_init()`, `sev_vm_destroy()`, `sev_vcpu_create()`, `sev_free_vcpu()`, `sev_init_vmcb()`, `sev_es_init_vmcb()`, and `pre_sev_run()`.
- User ABI dispatch: `sev_mem_enc_ioctl()` dispatches `KVM_SEV_*` and `KVM_SEV_SNP_*` commands.
- SEV/SEV-ES launch: `sev_guest_init()`, `sev_guest_init2()`, `sev_launch_start()`, `sev_launch_update_data()`, `sev_launch_update_vmsa()`, `sev_launch_measure()`, `sev_launch_finish()`, `sev_launch_secret()`, and attestation/debug helpers.
- Migration/mirroring: send/receive helpers, `sev_vm_move_enc_context_from()`, `sev_vm_copy_enc_context_from()`, `sev_migrate_from()`, and VM-pair locking helpers.
- SNP launch and memory: `snp_context_create()`, `snp_launch_start()`, `snp_launch_update()`, `sev_gmem_post_populate()`, `snp_launch_update_vmsa()`, `snp_launch_finish()`, and `snp_decommission_context()`.
- GHCB/VMGEXIT: `sev_handle_vmgexit()`, `sev_handle_vmgexit_msr_protocol()`, `sev_es_validate_vmgexit()`, `sev_es_sync_from_ghcb()`, `sev_es_sync_to_ghcb()`, `setup_vmgexit_scratch()`, and `sev_es_unmap_ghcb()`.
- SNP runtime: `snp_begin_psc()`, `snp_begin_psc_msr()`, `snp_complete_*()`, `sev_snp_ap_creation()`, `sev_snp_init_protected_guest_state()`, `snp_handle_guest_req()`, and `snp_handle_ext_guest_req()`.
- RMP/gmem: `kvm_rmp_make_shared()`, `snp_page_reclaim()`, `sev_handle_rmp_fault()`, `sev_gmem_prepare()`, `sev_gmem_invalidate()`, and `sev_gmem_max_mapping_level()`.
- Debug/VMSA: `sev_decrypt_vmsa()` and `sev_free_decrypted_vmsa()`.

## Control flow
Hardware setup validates NPT, NRIPS, decode assists, flush-by-ASID, PSP/SEV initialization, ASID ranges, SEV-ES requirements, SNP platform state, policy bits, ciphertext hiding ASID partitioning, and supported VMSA features. VM creation records the intended protected VM type; `KVM_SEV_INIT*` later allocates an ASID, charges the misc cgroup, initializes firmware, allocates SNP guest request buffers when needed, and inhibits APICv.

For classic SEV, userspace launches through `LAUNCH_START`, pins and encrypts memory through `LAUNCH_UPDATE_DATA`, optionally encrypts VMSAs for SEV-ES, measures, injects secrets, and finishes. SEV-ES VMSA sync copies KVM register/FPU state into a separate VMSA page, then firmware encrypts it and KVM marks guest state protected.

For SNP, launch start creates a firmware guest context and binds the ASID. Launch update populates guest_memfd private pages under `slots_lock`, validates RMP state, copies source data when needed, transitions PFNs private, and issues `SNP_LAUNCH_UPDATE`. Launch finish measures VMSAs, optionally passes ID/auth blocks, finalizes firmware state, and allows private pre-faulting.

At run time, `pre_sev_run()` installs the guest ASID, tracks CPUs that have run the guest for later cache writeback, and flushes ASID TLBs when a CPU/VMCB pairing changes. SEV-ES/SNP exits use either GHCB MSR protocol or a mapped GHCB page. KVM validates required GHCB fields for each exit code, synchronizes register state, handles MMIO, string IO, AP reset hold, AP jump table, SNP page-state changes, SNP guest requests, AP creation, or falls back to normal SVM exit handlers.

Teardown unregisters encrypted regions, flushes or writes back encrypted caches, decommissions firmware contexts, returns RMP entries to shared state, frees ASIDs, and handles mirror VMs without double-freeing owner state.

## State and persistence behavior
`struct kvm_sev_info` holds persistent VM encryption state: active/ES/SNP flags, ASID, firmware handle or SNP context, policy, PSP fd, GHCB version, VMSA features, locked-page accounting, misc cgroup, encrypted-region list, mirror-owner/list metadata, CPU-run cpumask, SNP guest request buffers, AP jump table, SNP cert-exit enablement, and migration-in-progress flag. Each `vcpu_svm` holds SEV-ES state such as VMSA pointer, GHCB map, scratch-area buffer, valid bitmap snapshot, AP reset hold type, SNP guest VMSA GPA, PSC progress, and whether the first SIPI was received.

Global state includes feature enable booleans, ASID ranges and bitmaps, reclaim bitmap, encryption bit/mask, supported SNP policy bits, supported VMSA feature bits, and locks for ASID bitmap and DEACTIVATE/DF_FLUSH ordering. User memory pinning is tracked per VM to enforce memlock limits and release pages on unregister/destroy. SNP RMP state persists in firmware/hardware and must be explicitly reclaimed or made shared.

## Dependencies and integration points
This file is a nexus for KVM x86 core, SVM VMCB code, PSP/SEV firmware commands, Linux mm/gup, misc cgroups, guest_memfd, RMP/SNP platform helpers, GHCB protocol definitions, CPUID/capability setup, APICv inhibit, KVM userspace exits, MMU invalidation and page fault handling, host CPU cache flush mechanisms, and tracepoints. It also integrates with migration through KVM fd validation and with userspace policy through `KVM_EXIT_HYPERCALL`, `KVM_EXIT_SNP_REQ_CERTS`, and `KVM_EXIT_SYSTEM_EVENT`.

## Risks and edge cases
- ASID recycling requires correct DEACTIVATE/DF_FLUSH/WBINVD ordering; failures can leak ASIDs or leave stale encrypted cache/TLB state.
- User memory pinning must enforce overflow, memlock, page dirtying, and cache coherency, especially on non-coherent SME systems.
- Firmware command errors must distinguish guest-visible firmware status from host infrastructure failures.
- SNP RMP transitions are security-critical; failed reclaim or shared/private updates intentionally leak pages rather than reusing protected memory unsafely.
- GHCB validation is the trust boundary for SEV-ES guests; missing validity checks can consume attacker-controlled stale state.
- AP creation rejects 2M-aligned VMSA GPAs to avoid an SNP erratum involving hugepage/RMP collisions.
- Mirrored encryption contexts and intra-host migration require careful lock ordering, refcounting, cgroup transfer, and vCPU state transfer.
- Debug decrypt paths must obey SEV/SNP policy bits and reclaim SNP firmware pages after use.

## Test signals
Test coverage should include SEV/SEV-ES/SNP initialization and failure paths, ASID exhaustion/recycling, memlock enforcement, launch update/measure/finish, VMSA encryption, SNP guest_memfd population, RMP fault PSMASH behavior, page-state-change exits, GHCB MSR and page protocols, SNP guest requests with and without certificate userspace exits, AP creation/destroy flows, migration/mirror ioctls, debug decrypt policy enforcement, and teardown leak/error paths. Runtime signals include SEV firmware return codes, `trace_kvm_vmgexit_*`, `trace_kvm_rmp_fault`, cache flush behavior, and KVM exits delivered to userspace.
