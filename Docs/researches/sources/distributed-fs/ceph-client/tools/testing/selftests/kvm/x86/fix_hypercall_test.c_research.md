# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/x86/fix_hypercall_test.c

Purpose: Tests `KVM_X86_QUIRK_FIX_HYPERCALL_INSN`, which patches a guest hypercall instruction from the wrong vendor opcode to the native opcode. It verifies both enabled and disabled quirk behavior.

Important APIs/types/functions: `guest_ud_handler()` catches invalid-opcode fallback, opcode arrays `vmx_vmcall[]` and `svm_vmmcall[]` model vendor hypercalls, `do_sched_yield()` calls a mutable `hypercall_insn` blob, `guest_main()` validates the patched bytes and return value, and `test_fix_hypercall()` toggles `KVM_CAP_DISABLE_QUIRKS2`. It uses `KVM_ONE_VCPU_TEST` harness macros.

Control flow: The guest writes the non-native hypercall opcode into its instruction blob and executes `KVM_HC_SCHED_YIELD`. With the quirk enabled, KVM patches the instruction and the hypercall succeeds. With the quirk disabled, the guest gets `#UD`, the handler returns `-EFAULT`, and the bytes remain unmodified.

State and persistence behavior: The test mutates executable guest memory at `hypercall_insn` and syncs the global `quirk_disabled` flag into the guest. APIC mapping is added for APIC ID lookup. No data persists beyond the VM.

Dependencies and integration points: Depends on KVM paravirtual hypercalls, disable-quirks capability, APIC ID access, exception handling, and the selftest harness.

Risks and maintenance notes: The instruction size is hardcoded to three bytes and must match both `VMCALL` and `VMMCALL`. Host vendor detection controls expected native opcode. Quirk ABI must remain stable for older VMM compatibility.

Test signals: Passing proves KVM patches wrong-vendor hypercalls only when the quirk is enabled and cleanly lets `#UD` occur when disabled. Failures identify paravirt hypercall patching or quirk gating regressions.
