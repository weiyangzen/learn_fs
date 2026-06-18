# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/vmcs_shadow_fields.h

## Purpose
Defines the VMCS fields eligible for VMCS shadowing by invoking caller-provided `SHADOW_FIELD_RO` and `SHADOW_FIELD_RW` macros. It is an include-time table rather than a standalone header API.

## Important APIs, Types, And Functions
The file requires at least one of `SHADOW_FIELD_RO` or `SHADOW_FIELD_RW` to be defined and provides empty defaults for the other. It lists shadowed fields grouped by width: selected 16-bit fields, read-only VM-exit info, read/write execution and entry controls, natural-width guest/control fields, host FS/GS fields, and read-only guest physical address fields.

## Control Flow
Callers include this file with macros that generate enums, arrays, or handling code. Fields modified when L0 emulates VMX instructions are intentionally not shadowed because such changes would require extra shadow synchronization. The comments require shadowed fields to be synced by `prepare_vmcs02`, not only rare preparation paths.

## State And Persistence
The file itself has no storage. It defines the shadowed subset of VMCS12/VMCS fields that can be cached in hardware shadow VMCS state for nested VMX performance.

## Dependencies And Integration Points
Depends on VMCS field encoding symbols and `struct vmcs12` field names. Integrated by nested VMX shadow-VMCS code and VMCS12 generic read/write helpers.

## Risks
Adding a field that changes during L0 VMX instruction emulation can create stale shadow state. Removing a field can hurt nested VMX performance or alter VMREAD/VMWRITE interception. Field ordering by size is used for branch prediction expectations in generic accessors.

## Test Signals
Nested VMCS shadow tests, L1 VMREAD/VMWRITE behavior, VMX instruction failure paths, and L2 run preparation tests validate this table.
