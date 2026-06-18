<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm-asm-offsets.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm-asm-offsets.c

### Purpose
`kvm-asm-offsets.c` generates assembly-visible offsets for KVM x86 VMX and SVM structures. The build compiles this file as offset-generation input and post-processes the raw assembler output for inclusion by assembly code.

### Important APIs, Types, And Functions
The single `common()` function emits offsets using `OFFSET()` and separators using `BLANK()`. When `CONFIG_KVM_AMD` is enabled it emits `SVM_vcpu_arch_regs`, `SVM_current_vmcb`, `SVM_spec_ctrl`, `SVM_vmcb01`, `KVM_VMCB_pa`, and `SD_save_area_pa`. When `CONFIG_KVM_INTEL` is enabled it emits `VMX_spec_ctrl`. It includes `vmx/vmx.h` and `svm/svm.h` under `COMPILE_OFFSETS`.

### Control Flow
There is no runtime control flow. Compile-time `IS_ENABLED()` conditionals determine which offsets are emitted for the configured build.

### State, Persistence, And Dependencies
The file persists no state. It depends on exact definitions of `struct vcpu_svm`, `struct kvm_vmcb_info`, `struct svm_cpu_data`, and `struct vcpu_vmx`; any structure layout change is reflected in regenerated offsets.

### Integration Points
Generated offsets are consumed by low-level VM entry/exit and speculation-control assembly that cannot use C field access. The file participates in the kernel asm-offsets build pipeline.

### Risks
Missing or stale offsets can break assembly at build time or, worse, cause runtime corruption if assembly and C disagree. Conditional emission must match assembly use under Intel/AMD config combinations.

### Test Signals
Build KVM with AMD-only, Intel-only, and combined configurations. Verify generated asm offsets change when relevant struct fields move and that low-level VMX/SVM assembly still assembles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm-asm-offsets.c -->
