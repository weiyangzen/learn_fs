# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs12.h

## Purpose
Defines KVM's emulated VMCS layout for nested VMX (`struct vmcs12`), migration-compatible offsets, revision/size constants, offset validation, and generic typed read/write helpers for VMCS12 fields.

## Important APIs, Types, And Functions
`struct vmcs12` is packed and contains the VMCS header, abort state, launch state, 64-bit controls/pointers, natural-width fields, 32-bit fields, and 16-bit selectors/status fields. `VMCS12_REVISION` and `VMCS12_SIZE` define nested VMX ABI. `vmx_check_vmcs12_offsets()` asserts fixed offsets. `get_vmcs12_field_offset()` validates and translates VMCS field encodings. `vmcs12_read_any()` and `vmcs12_write_any()` access fields according to VMCS width.

## Control Flow
L1 accesses VMCS12 through VMX instructions emulated by KVM. The nested VMX emulator decodes the VMCS field, calls `get_vmcs12_field_offset()`, and then reads or writes via the generic helpers. During nested run, VMCS12 is used to synthesize VMCS02 hardware state for L2. Offset checks protect build-time layout stability.

## State And Persistence
VMCS12 contents are guest-owned nested virtualization state stored in guest memory selected by VMPTRLD. The packed layout is explicitly migration ABI; existing field locations must not change. `launch_state` persists VMLAUNCH/VMCLEAR state. Padding areas are reserved for compatible expansion.

## Dependencies And Integration Points
Depends on `vmcs.h` for field width decoding and encoding-index mapping. Externs `vmcs12_field_offsets` and `nr_vmcs12_fields` are populated by `vmcs12.c`. Used broadly by nested VMX instruction emulation, state save/restore, and VMCS shadow support.

## Risks
Layout changes break save/restore and migration. Generic read/write helpers cast directly into packed storage, so offsets and widths must be correct. `get_vmcs12_field_offset()` uses nospec indexing to reduce speculative out-of-bounds risk; callers must still handle `-ENOENT`.

## Test Signals
Nested VMX state migration tests, VMCS12 offset build assertions, VMREAD/VMWRITE width tests, VMLAUNCH/VMCLEAR state tests, and L1/L2 nested boot tests validate this header.
