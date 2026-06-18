# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs12.c

## Purpose
Builds the runtime lookup table that maps VMCS field encodings to offsets in KVM's packed `struct vmcs12`, filtered by the actual VMX capabilities available on the host.

## Important APIs, Types, And Functions
`kvm_supported_vmcs12_field_offsets[]` is the static offset table populated with `FIELD()` and `FIELD64()` macros. `vmcs12_field_offsets[]` and `nr_vmcs12_fields` are runtime, read-mostly outputs. `cpu_has_vmcs12_field()` checks whether a field should be exposed based on VMX features. `nested_vmx_setup_vmcs12_fields()` copies supported entries into the runtime table at init.

## Control Flow
At initialization, `nested_vmx_setup_vmcs12_fields()` iterates the static array. Empty entries and capability-disabled fields are skipped. Supported fields get their `struct vmcs12` offset copied into `vmcs12_field_offsets`, and `nr_vmcs12_fields` advances to the highest present index plus one. Nested VMX VMREAD/VMWRITE later use `get_vmcs12_field_offset()` from the header against this table.

## State And Persistence
`vmcs12_field_offsets[]` and `nr_vmcs12_fields` are initialized once and marked `__ro_after_init`. They define the persistent nested-VMX field surface for the running module. The static table is `__initconst`.

## Dependencies And Integration Points
Depends on `vmcs12.h`, VMCS encodings, and capability helpers such as VPID, posted interrupts, TSC scaling, TPR shadow, APIC access virtualization, VMFUNC, EPT, XSAVES, ENCLS VM-exit, perf global ctrl load, secondary controls, and CET controls. It is central to nested VMX emulation and live migration compatibility.

## Risks
Forgetting to gate a field by its CPU capability could expose unusable nested VMX features. Omitting a supported field breaks L1 hypervisors. Incorrect offsets corrupt VMCS12 state. Because the struct layout is migration ABI, offset changes are especially dangerous.

## Test Signals
Nested VMX selftests for VMREAD/VMWRITE of optional fields, feature-masked CPU models, migration of nested state, and host capability combinations cover this file. Build-time offset checks in `vmcs12.h` also protect the table.
