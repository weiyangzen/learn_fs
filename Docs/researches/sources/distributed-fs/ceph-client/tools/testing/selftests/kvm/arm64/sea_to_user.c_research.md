# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/arm64/sea_to_user.c

Purpose: this arm64 KVM selftest validates `KVM_CAP_ARM_SEA_TO_USER`: when host APEI cannot handle a synchronous external abort, KVM exits to userspace with `KVM_EXIT_ARM_SEA`; userspace then injects a synchronous external data abort back into the guest.

Important APIs and functions: address helpers `translate_hva_to_hpa()`, EINJ writers `write_einj_entry()` and `inject_uer()`, SIGBUS handling, guest `guest_code()`, guest `expect_sea_handler()`, `vcpu_inject_sea()`, `run_vm()`, `vm_create_with_sea_handler()`, and `vm_inject_memory_uer()` form the test. Global state records EINJ GPA/HVA/HPA and whether FAR is invalid.

Control flow: `main()` requires `KVM_CAP_ARM_SEA_TO_USER`, installs a SIGBUS handler, creates a VM with a 1GB hugetlb-backed region mapped at `START_GVA`, enables SEA-to-user, poisons a selected HPA using ACPI EINJ notrigger, and runs the vCPU. The first run should exit with `KVM_EXIT_ARM_SEA`; host validates ESR/FAR/GPA information, sets guest expectation state, injects an external abort through vCPU events, and resumes until the guest handler reports done.

State and persistence: it writes to firmware/kernel debugfs EINJ control files and consumes a real injected memory error. Runtime globals expose expected FAR validity to the guest via synced memory. No project files are persisted.

Dependencies and integration points: depends on ACPI EINJ firmware table, debugfs EINJ files, notrigger support, hugepage backing, `/proc/self/pagemap`, KVM SEA-to-user capability, and host APEI not claiming the SEA. The SIGBUS handler skips when host APEI handles the error instead.

Risks: this is highly platform-dependent and potentially disruptive because it injects a real recoverable uncorrectable memory error. It requires privileges, debugfs setup, hugepages, and specific firmware behavior. FAR may be invalid, and the test explicitly handles FnV.

Test signals: skip signals come from missing capability/EINJ/APEI behavior. Success requires `KVM_EXIT_ARM_SEA`, correct ESR class/FSC fields, optional matching GVA/GPA, and clean guest handling of the injected SEA.
