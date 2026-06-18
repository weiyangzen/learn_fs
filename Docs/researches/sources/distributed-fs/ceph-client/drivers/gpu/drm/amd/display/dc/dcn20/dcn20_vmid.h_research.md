# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dcn20/dcn20_vmid.h

## Purpose
Defines DCN2 VMID register lists, field lists, concrete VMID descriptor, and the setup API.

## Important APIs, Types, And Functions
`DCN20_VMID_REG_LIST(id)` enumerates `CNTL`, page-table base high/low, start high/low, and end high/low registers. `DCN20_VMID_MASK_SH_LIST` and `DCN20_VMID_REG_FIELD_LIST` define depth, block size, page-directory entry, and logical page-number fields. `struct dcn20_vmid` stores context, register map, shifts, and masks. `dcn20_vmid_setup()` is declared.

## Control Flow
No runtime flow in the header. It supplies the register contract consumed by the `.c` setup implementation and resource code.

## State And Persistence
The descriptor holds pointers to register metadata. VM page-table state lives in hardware registers.

## Dependencies And Integration Points
Includes `vmid.h` for common VMID register and config types. Resource builders use these macros to instantiate VMID register tables.

## Risks
Field names all use VM_CONTEXT0 naming even when macro parameter selects other instances; this follows generated register naming but is easy to misuse. Any mismatch in high/low address field width corrupts GPUVM address ranges.

## Test Signals
Compile-time macro expansion, VMID setup readback, GPUVM memory access tests, and absence of VM faults after context programming.
