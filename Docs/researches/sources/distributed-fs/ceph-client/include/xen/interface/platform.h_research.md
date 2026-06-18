# sources/distributed-fs/ceph-client/include/xen/interface/platform.h

## Purpose
`platform.h` defines dom0-oriented Xen platform operations for host time, memory type ranges, microcode, EFI runtime services, firmware information, ACPI sleep, CPU frequency and idle data, processor PM tables, CPU/memory hotplug, core parking, symbol lookup, and dom0 console discovery.

## Important APIs, Types, and Functions
The central ABI is `struct xen_platform_op` with `cmd`, `interface_version`, and a union of command payloads. Major payloads include `xenpf_settime32/64`, `xenpf_add_memtype`, `xenpf_del_memtype`, `xenpf_read_memtype`, `xenpf_microcode_update`, `xenpf_efi_runtime_call`, `xenpf_firmware_info`, `xenpf_enter_acpi_sleep`, `xenpf_change_freq`, `xenpf_getidletime`, `xenpf_set_processor_pminfo`, `xenpf_pcpuinfo`, hotplug structs, `xenpf_core_parking`, and `xenpf_symdata`.

## Control Flow
The hardware domain fills a platform op and calls `HYPERVISOR_platform_op`. Xen dispatches by command, reading or updating host-wide platform state such as wallclock, MTRR/memtype setup, firmware tables, EFI variables, ACPI sleep state, CPU PM capabilities, and hotplug state.

## State and Persistence Behavior
Most operations change host or hypervisor platform state rather than guest-local state: time, microcode, memory type handles, EFI variables, CPU online state, PM tables, and hotplug topology. Query operations return snapshots.

## Dependencies and Integration Points
It depends on `xen/interface/xen.h` and `dom0_vga_console_info`. Linux dom0 ACPI, EFI, CPUfreq/cpuidle, microcode, hotplug, firmware, and console code integrate through this ABI.

## Risks and Test Signals
Risks include interface-version mismatch, union padding/size assumptions, unsafe EFI variable buffers, incorrect PM dependency arrays, privilege-sensitive host changes, and 32-bit time limitations. Test signals include EFI get/set variable paths, ACPI sleep entry, CPU online/offline/hotadd, PM table registration, microcode update failure modes, and symbol/console queries.
