# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/hyperv_evmcs.c

## Purpose
`vmx/hyperv_evmcs.c` defines the translation table from architectural VMCS field encodings to offsets in Hyper-V's `struct hv_enlightened_vmcs` v1 layout. The table is shared by KVM running on Hyper-V, where VMCS reads/writes are redirected into an enlightened VMCS, and by nested VMX code translating an L1 Hyper-V guest's eVMCS into KVM's `vmcs12`.

## Important APIs, Types, And Functions
The file defines two macros: `EVMCS1_OFFSET(x)` wraps `offsetof(struct hv_enlightened_vmcs, x)`, and `EVMCS1_FIELD(number, name, clean_field)` installs an `evmcs_field` entry indexed by `ENC_TO_VMCS12_IDX(number)`. The exported `vmcs_field_to_evmcs_1[]` array maps many 64-bit, 32-bit, and 16-bit VMCS fields to eVMCS offsets and Hyper-V clean-field masks. `nr_evmcs_1_fields` exports the array size for bounds checking in `evmcs_field_offset()`.

Mapped fields include guest/host RIP/RSP/RFLAGS, host and guest PAT/EFER/perf global controls, CR0/CR3/CR4/DR7, SYSENTER fields, IO/MSR bitmaps, segment bases/limits/access rights/selectors, descriptor table bases/limits, TSC offset/multiplier, APIC page, VMCS link pointer, PDPTRs, guest pending debug exceptions, EPT pointer, XSS and ENCLS bitmaps, exit qualification and physical/linear addresses, VM-exit and VM-entry event fields, VM instruction error, exit reason, instruction length, pin/primary/secondary controls, TPR threshold, page-fault masks, CR3 target/MSR load-store counts, host selectors, guest selectors, and VPID. Several newer CET/LBR fields are listed as not used by KVM.

## Control Flow
There is no dynamic control flow beyond static initialization. At runtime, readers call `evmcs_field_offset()` from `hyperv_evmcs.h`, which indexes this table by encoded VMCS field. KVM-on-Hyper-V accessors use the returned offset to load/store the current eVMCS and clear the appropriate clean-field bit. Nested VMX code uses the same mapping to read arbitrary eVMCS fields or copy clean groups.

## State And Persistence
The table is immutable kernel data. The clean-field mask associated with each entry determines how writes invalidate Hyper-V's clean-state cache in the live eVMCS page. Entries using `HV_VMX_ENLIGHTENED_CLEAN_FIELD_ALL` represent fields without a spec-defined specific clean mask and force broad invalidation. Offset zero is reserved by lookup code to mean "hole" because `revision_id` has no VMCS encoding and lives at offset zero.

## Dependencies And Integration Points
The implementation depends on `hyperv_evmcs.h`, which brings in Hyper-V HVDK eVMCS definitions, VMCS field encodings, and `struct evmcs_field`. It integrates with `vmx_onhyperv.h` eVMCS read/write paths, `nested.c` eVMCS copy paths, and any code that needs to translate standard VMCS encodings to enlightened layout.

## Risks And Edge Cases
The translation table is a correctness-critical ABI map. A wrong offset can corrupt eVMCS state; a wrong clean mask can make Hyper-V or KVM reuse stale fields. Unsupported VMCS fields must remain holes so lookup returns `-ENOENT`; accidentally mapping a field absent from eVMCS v1 would falsely expose support. The table includes `TSC_MULTIPLIER` even though nested eVMCS control filtering clears TSC scaling for guest controls, so consumers must distinguish field layout from feature exposure. The offset-zero hole convention means no encoded VMCS field can validly map to offset zero.

## Test Signals
Useful signals are compile-time layout checks against `struct hv_enlightened_vmcs`, VMCS read/write tests while KVM runs on Hyper-V, nested Hyper-V eVMCS launch tests, clean-field invalidation tests for each major group, unsupported-field lookup tests, migration tests preserving eVMCS data, and comparison tests between VMCS12 copy behavior and expected eVMCS field values.
