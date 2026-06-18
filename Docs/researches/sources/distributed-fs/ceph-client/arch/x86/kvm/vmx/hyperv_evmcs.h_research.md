# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv_evmcs.h

## Purpose
`vmx/hyperv_evmcs.h` defines the shared contract for Hyper-V Enlightened VMCS v1 support. It declares eVMCS versioning, enumerates which VMX controls are representable by eVMCS v1, exposes the VMCS-field-to-eVMCS translation table, and provides inline helpers for offset lookup and typed field reading.

## Important APIs, Types, And Functions
`KVM_EVMCS_VERSION` is currently `1`. The `EVMCS1_SUPPORTED_*` masks define the VMX pin, primary execution, secondary execution, tertiary execution, VM-exit, VM-entry, and VMFUNC controls usable with eVMCS v1. Comments list VMCS fields not supported by eVMCS v1, such as posted-interrupt descriptor fields, APIC access address, EOI bitmaps, PML fields, VMFUNC/EPTP list fields, VMREAD/VMWRITE bitmaps, preemption timer, PLE fields, and some tracing fields.

`struct evmcs_field` stores an eVMCS byte offset and a Hyper-V clean-field mask. `vmcs_field_to_evmcs_1[]` and `nr_evmcs_1_fields` are defined in `hyperv_evmcs.c`. `evmcs_field_offset()` converts an encoded VMCS field to an array index with `ENC_TO_VMCS12_IDX()`, rejects out-of-range or hole entries, optionally returns the clean-field mask, and returns the eVMCS offset. `evmcs_read_any()` reuses `vmcs12_read_any()` against an eVMCS pointer because it accepts an explicit offset and field encoding.

## Control Flow
Feature filtering code uses the supported-control masks to hide VMX features that Hyper-V eVMCS cannot carry. VMCS access code calls `evmcs_field_offset()` before every redirected field access. If lookup fails, the caller treats the field as unsupported for eVMCS. Successful writes use the returned clean-field mask to invalidate Hyper-V clean groups; reads use the offset directly. `evmcs_read_any()` is used by nested VMX when an arbitrary field encoding needs to be read from the mapped eVMCS page.

## State And Persistence
The header itself stores no mutable state. It defines the static ABI between KVM and `struct hv_enlightened_vmcs`. Runtime state lives in the eVMCS page, especially `hv_clean_fields`, which tracks which groups Hyper-V may treat as unchanged. The control masks also define persistent guest-visible nested VMX capability behavior once exposed through CPUID/MSRs.

## Dependencies And Integration Points
The file depends on Hyper-V HVDK definitions (`<hyperv/hvhdk.h>`), `capabilities.h`, and `vmcs12.h`. It is consumed by `hyperv.c`, `hyperv_evmcs.c`, `vmx_onhyperv.h`, nested VMX copy/validation code, and VMX-on-Hyper-V setup that sanitizes VMCS controls to the eVMCS-supported subset.

## Risks And Edge Cases
The supported-control masks must agree with the field map and Hyper-V behavior. Exposing a control without a corresponding eVMCS field can break nested Hyper-V guests. Some fields are present in the structure but not used by KVM; future feature work must add both table entries and control validation deliberately. `evmcs_field_offset()` relies on offset zero as a hole marker because `revision_id` is not VMCS-encoded. Callers must handle `-ENOENT` and must not access eVMCS memory after failed lookup.

## Test Signals
Signals include VMX control MSR filtering tests, eVMCS field lookup tests for supported and unsupported encodings, KVM-on-Hyper-V boot and nested virtualization tests, clean-field update tests, CPUID eVMCS version tests, and nested Hyper-V L1 tests that attempt unsupported controls such as posted interrupts, PML, VMFUNC controls, and preemption timer.
