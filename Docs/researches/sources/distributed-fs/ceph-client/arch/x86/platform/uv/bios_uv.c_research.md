<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/bios_uv.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/uv/bios_uv.c

## Purpose
Wraps UV firmware runtime services exposed through the EFI UV system table.

## Important APIs, Types, And Functions
Exports UV BIOS calls for partition/coherency info, message-queue watchlists, memory protection, reserved pages, frequency base, legacy VGA target, master NASID, heap operations, object/port/geoinfo/PCI topology enumeration, and `uv_bios_init()`. `uv_systab_phys`, `uv_systab`, and SN info globals hold firmware state.

## Control Flow
`uv_bios_init()` validates and maps the EFI UV systab, remapping variable-size UV4+ tables. Calls acquire `__efi_uv_runtime_lock`, optionally disable IRQs, invoke the table function through `efi_call_virt_pointer()`, and return BIOS status codes.

## State And Persistence
The mapped `uv_systab` and exported partition globals persist after init. Firmware calls can alter UV BIOS-managed state such as heaps, memory protection, and watchlists.

## Dependencies And Integration Points
Depends on EFI runtime support, UV hub headers, x86 EFI locking, ioremap, and platform drivers needing UV firmware services.

## Risks And Edge Cases
Missing or disabled EFI runtime makes the systab unavailable. Firmware status codes must be preserved. Calls under IRQ-save are required for some low-level contexts but can still depend on EFI runtime correctness.

## Test Signals
UV systab revision logs, successful SN info retrieval, UV feature drivers using exported calls, and clean behavior with missing systab validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/uv/bios_uv.c -->
