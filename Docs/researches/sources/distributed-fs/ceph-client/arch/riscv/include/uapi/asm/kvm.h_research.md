<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/kvm.h

Purpose: Defines the RISC-V KVM userspace ABI for vCPU registers, ISA/SBI extension IDs, timers, AIA CSRs, firmware features, and one-reg encodings.

Important APIs/types/functions: Important types include `kvm_riscv_config`, `kvm_riscv_core`, `kvm_riscv_csr`, `kvm_riscv_aia_csr`, `kvm_riscv_timer`, extension enums `KVM_RISCV_ISA_EXT_ID` and `KVM_RISCV_SBI_EXT_ID`, SBI STA/FWFT structs, and `KVM_REG_RISCV_*` macros.

Control flow: Userspace VMMs use KVM ioctls and one-reg IDs to configure ISA exposure, inspect/save/restore vCPU state, timers, CSRs, and SBI feature policy.

State and persistence: ABI state persists in VM/vCPU register files, timer values, enabled extension bitmaps, and migration streams.

Dependencies and integration points: Consumed by QEMU/kvmtool, KVM RISC-V kernel code, selftests, and migration tooling.

Risks: Enum ordering and register IDs are ABI. Reordering or wrong struct sizing breaks userspace VMMs and migration compatibility.

Test signals: KVM selftests, QEMU boot/migration, one-reg round trips, timer/AIA tests, and headers_install ABI checks.

Source read size: 401 lines, 12559 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/kvm.h -->
