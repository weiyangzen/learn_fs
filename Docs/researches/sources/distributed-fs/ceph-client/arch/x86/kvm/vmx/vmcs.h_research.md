# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs.h

## Purpose
Defines VMCS support types and helpers shared across VMX code, including VMCS12 field index compression, loaded-VMCS tracking, host-state caching, control-shadow caching, interrupt-info predicates, and VMCS field metadata helpers.

## Important APIs, Types, And Functions
Macros `ROL16()`, `VMCS12_IDX_TO_ENC()`, and `ENC_TO_VMCS12_IDX()` map VMCS encodings to compact array indices. `struct vmcs_host_state` caches host fields loaded on VM-exit. `struct vmcs_controls_shadow` caches execution/entry/exit controls. `struct loaded_vmcs` tracks current VMCS, shadow VMCS, CPU, launch state, virtual NMI state, hv timer state, MSR bitmap, loaded-list linkage, host state, and control shadows. Helper predicates identify interrupt types and exception vectors. `vmcs_field_width()`, `vmcs_field_readonly()`, and `vmcs_field_index()` decode VMCS field encodings.

## Control Flow
Nested VMX uses the encoding/index helpers to map arbitrary VMREAD/VMWRITE field encodings to `struct vmcs12` offsets. VMX entry/load paths use `loaded_vmcs` to track whether a VMCS is loaded on a CPU and whether it has launched. Exit handling uses interrupt predicates to classify VM-exit interruption information.

## State And Persistence
`DECLARE_PER_CPU(struct vmcs *, current_vmcs)` tracks the loaded VMCS pointer per CPU. `loaded_vmcs` instances persist for vCPU or nested-VMX lifetime and link into per-CPU loaded VMCS lists so CPU-down paths can clear them. Host-state and control-shadow fields are write-through caches of VMCS fields.

## Dependencies And Integration Points
Depends on Linux time/list/nospec, x86 KVM/VMX architectural constants, and VMX capability definitions. Used by VMX core, nested VMX, VMCS operation wrappers, TDX VMCS access checks, and VM-entry code.

## Risks
VMCS field encoding helpers must match Intel VMCS encoding layout. `loaded_vmcs` CPU tracking is sensitive to migration and CPU hotplug. Interrupt-info helpers rely on valid VMCS interruption information masks; misuse can misclassify NMIs, exceptions, or external interrupts.

## Test Signals
Nested VMX VMREAD/VMWRITE tests, CPU hotplug with loaded VMCSs, virtual NMI tests, VMCS shadow tests, and exception-injection/exit-classification tests exercise this header.
