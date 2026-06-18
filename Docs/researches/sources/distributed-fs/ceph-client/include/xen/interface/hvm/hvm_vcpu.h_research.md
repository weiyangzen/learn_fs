# sources/distributed-fs/ceph-client/include/xen/interface/hvm/hvm_vcpu.h

Purpose: defines the architecture-specific initial register context used to launch an HVM/PVH vCPU in 32-bit or 64-bit x86 mode.

Important APIs/types/functions: `struct vcpu_hvm_x86_32` contains 32-bit general registers, control registers, EFER, and cached segment base/limit/access-right fields. `struct vcpu_hvm_x86_64` contains 64-bit general registers plus `cr0`, `cr3`, `cr4`, and `efer`. `struct vcpu_hvm_context` selects `VCPU_HVM_MODE_32B` or `VCPU_HVM_MODE_64B` and embeds the corresponding union.

Control flow: a domain builder or control tool prepares this context before vCPU startup. The mode selects which union member Xen consumes. For 64-bit mode, Xen derives segment caches suitable for long mode; compatibility-mode launches use the 32-bit layout.

State and persistence: the structure is a one-time or explicit vCPU state payload. After launch, CPU state lives inside Xen/vCPU execution state.

Dependencies and integration points: includes `../xen.h` for integer and Xen ABI types. Integrates with HVM/PVH domain builders, boot loaders, and vCPU creation paths.

Risks: segment access-right bit layout must match Intel SDM encoding. Incorrect EFER/CR combinations can fail launch or start in the wrong mode. Padding and union layout are ABI and must remain stable across compilers.

Test signals: domain-builder tests launching 32-bit, 64-bit, paging-enabled, and compatibility-mode guests; structure size/offset assertions; and boot smoke tests that validate initial RIP/EIP and control-register state.
