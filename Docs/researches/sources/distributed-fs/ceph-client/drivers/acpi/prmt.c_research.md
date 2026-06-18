<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/prmt.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/prmt.c

## Purpose
`prmt.c` initializes ACPI Platform Runtime Mechanism support. It parses the PRMT table, maps firmware PRM handler physical addresses to EFI runtime virtual addresses, records module/handler metadata, exposes handler availability/call helpers, and installs the `PlatformRtMechanism` operation-region handler used by AML to invoke PRM services.

## Important APIs, Types, and Functions
Private packed wire/context types include `prm_mmio_info`, `prm_buffer`, and `prm_context_buffer`. Runtime metadata is `struct prm_module_info` with flexible handler array and `struct prm_handler_info`. Public exports are `acpi_prm_handler_available()` and `acpi_call_prm_handler()`. Key internals are `efi_pa_va_lookup()`, `acpi_parse_prmt()`, GUID lookup helpers, `acpi_platformrt_space_handler()`, and `init_prmt()`.

## Control Flow and State
`init_prmt()` checks for a PRMT table, parses module subtables, logs module count, verifies EFI runtime services, and installs an ACPI root address-space handler for `ACPI_ADR_SPACE_PLATFORM_RT`. Each parsed module allocates metadata, copies module GUID/revisions/count, maps and copies optional MMIO range lists, appends to `prm_module_list`, and converts each handler/static/parameter buffer physical address through EFI runtime descriptors. AML writes a PRM buffer to the opregion handler; `RUN_SERVICE` locates handler/module, builds a PRM context, calls `efi_call_acpi_prm_handler()`, and writes status/EFI status back. Transaction commands toggle the module `updatable` flag. The exported direct call path invokes a handler with a caller-supplied parameter buffer.

## State and Persistence
Persistent state is `prm_module_list`, allocated module/handler metadata, copied MMIO range lists, handler virtual addresses, static/ACPI parameter buffer addresses, and per-module `updatable` flags. PRM services execute in EFI runtime context and may mutate platform firmware/hardware state.

## Dependencies and Integration Points
The file depends on ACPI PRMT structures, EFI runtime memory descriptors, architecture EFI call wrappers, GUID helpers, ACPI operation regions, and exported PRM APIs used by other kernel code. It integrates AML bytecode with EFI PRM service handlers.

## Risks and Test Signals
Risks include physical-to-virtual lookup requiring EFI runtime descriptors that cover handler addresses, memory leaks because PRMT metadata persists permanently, transaction locking not protected by a mutex, continuing after NULL handler addresses inside the parse loop without advancing handler pointers in that iteration, and firmware handler failures reported through buffer fields rather than ACPI status. Test signals are PRMT module count logs, successful opregion handler installation, `acpi_prm_handler_available()` for known GUIDs, AML PRM run-service status values, EFI status propagation, and graceful behavior when EFI runtime services are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/prmt.c -->
