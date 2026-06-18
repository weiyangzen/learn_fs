# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_config.c

Purpose: This file derives and loads the hypervisor configuration CSRs that shape guest-visible behavior for a vCPU. It initializes default exception/interrupt delegation, adjusts delegation for guest debugging, enables HENVCFG/HSTATEEN bits according to the configured guest ISA, and writes those CSRs through NACL or direct CSR paths.

Important APIs/types/functions: `KVM_HEDELEG_DEFAULT` delegates common guest exceptions such as illegal instruction, syscall, and page faults. `KVM_HIDELEG_DEFAULT` delegates VS software, timer, and external interrupts. Public functions are `kvm_riscv_vcpu_config_init`, `kvm_riscv_vcpu_config_guest_debug`, `kvm_riscv_vcpu_config_ran_once`, and `kvm_riscv_vcpu_config_load`.

Control flow: vCPU creation initializes default delegation. Guest debug toggles breakpoint delegation so breakpoints exit to userspace when debug is enabled and marks CSRs dirty. Just before the first run, `ran_once` adds HENVCFG bits for Svpbmt, Sstc, Zicbom, Zicboz, and Svadu-without-Svade, and HSTATEEN bits for HSENVCFG, AIA, IMSIC, ISELECT, and nested stateen exposure when the host supports Smstateen. Load writes HEDELEG/HIDELEG/HENVCFG and optional high halves/HSTATEEN through NACL shared memory when available or direct CSR writes otherwise.

State and persistence: The derived configuration persists in `vcpu->arch.cfg`. It is mostly immutable after first run except guest-debug toggling of breakpoint delegation. CSR writes are runtime CPU state and are refreshed by `kvm_arch_vcpu_load`.

Dependencies and integration points: It depends on ISA policy and vCPU ISA bitmaps, NACL CSR sync, RISC-V CSR/HENVCFG/HSTATEEN definitions, guest debug ioctls, and the vCPU load fast path in `vcpu.c`.

Risks and test signals: Missing HENVCFG/HSTATEEN bits can advertise an extension without granting access to its CSRs or behavior; overly broad bits expose unsupported state. Tests should cover first-run derivation for each gated extension, guest debug enable/disable before and after load, 32-bit high CSR writes, NACL/direct load equivalence, and `csr_dirty` forcing reload after debug changes.
