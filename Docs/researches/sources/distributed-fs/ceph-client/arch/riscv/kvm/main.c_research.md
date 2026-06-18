# sources/distributed-fs/ceph-client/arch/riscv/kvm/main.c

Purpose: This file is the RISC-V KVM module entry point and per-CPU virtualization enable/disable hook. It validates architectural and SBI prerequisites, initializes optional NACL/AIA acceleration, detects G-stage mode and VMID width, registers KVM core, and tears everything down on exit.

Important APIs/types/functions: `DEFINE_STATIC_KEY_FALSE(kvm_riscv_vsstage_tlb_no_gpa)` records an Andes vendor quirk. `kvm_arch_enable_virtualization_cpu` enables NACL shared memory, clears delegation CSRs, permits only time counter access, clears HVIP, and enables AIA. `kvm_arch_disable_virtualization_cpu` disables AIA, clears VSIE/HVIP/delegation CSRs in a safe order, and disables NACL. Module functions are `riscv_kvm_init`, `riscv_kvm_exit`, and helper `kvm_riscv_teardown`.

Control flow: Module init refuses hosts without H extension, SBI v0.2+, or RFENCE. It initializes NACL if available, probes G-stage mode, detects VMID bits, initializes AIA when available, prints discovered capabilities, enables vendor quirks, registers perf callbacks, and calls `kvm_init`. Failures unwind NACL/AIA/perf state through `kvm_riscv_teardown`. CPU enable/disable hooks program hypervisor CSRs each time KVM virtualization is activated on a CPU.

State and persistence: Persistent module state includes static keys for vendor TLB behavior, NACL feature keys, AIA availability, VMID mode information, and registered device/perf/KVM core callbacks. Per-CPU virtualization state lives in CSRs and is reset on disable.

Dependencies and integration points: It depends on SBI probing, cpufeature discovery, NACL, G-stage/VMID helpers, AIA init, perf callbacks, and generic KVM module registration. It bridges Linux KVM core with RISC-V hardware virtualization.

Risks and test signals: CSR disable ordering matters because stale HVIP plus VSIE can deliver spurious host interrupts after clearing delegation. Init unwind must not leak NACL pages or AIA IRQ/device registrations. Tests should cover unsupported-H/SBI/RFENCE paths, NACL feature combinations, AIA absent/present hosts, G-stage mode detection failures, module load/unload, CPU hotplug virtualization enable/disable, and Andes AX66 quirk behavior.
