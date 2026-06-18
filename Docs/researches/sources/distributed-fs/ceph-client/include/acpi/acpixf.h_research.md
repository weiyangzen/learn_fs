<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpixf.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpixf.h

## Purpose
`acpixf.h` defines ACPICA's public external interface, runtime configuration globals, feature-dependent stub macros, and the exported function prototypes for initialization, table management, namespace traversal, object evaluation, handlers, events, resources, hardware registers, sleep, timers, diagnostics, and debugger support.

## Important APIs, types, and functions
It declares `ACPI_CA_VERSION` and global configuration variables such as `acpi_gbl_enable_interpreter_slack`, `acpi_gbl_auto_serialize_methods`, `acpi_gbl_create_osi_method`, `acpi_gbl_enable_table_validation`, `acpi_gbl_copy_dsdt_locally`, `acpi_gbl_do_not_use_xsdt`, FADT address policy flags, `acpi_gbl_reduced_hardware`, `acpi_gbl_use_global_lock`, `acpi_gbl_max_loop_iterations`, trace globals, debug masks, `acpi_gbl_FADT`, and `acpi_current_gpe_count`. Public APIs include subsystem initialization, ACPI enable/disable, system info/statistics, interface management, table install/load/unload/get/put, namespace walking, handle/name/data APIs, object evaluation, method installation, notify/address-space/exception/interface handlers, global lock and AML mutexes, fixed events, GPEs, resource conversion/walking, reset and GAS read/write, sleep/wake, PM timer, diagnostic print functions, debug trace functions, and Linux-specific divergence `acpi_get_data_full()`.

## Control flow
A typical boot flow calls table initialization, subsystem initialization, ACPI enablement, table loading, and object initialization. Drivers then query tables, walk namespace nodes, evaluate methods, install notify or address-space handlers, and manage GPE/fixed events. Hardware-dependent APIs are compiled into stubs returning `AE_NOT_CONFIGURED`, `AE_OK`, or zero when `ACPI_REDUCED_HARDWARE` is true; diagnostic/debug/application/debugger APIs are similarly stubbed based on build flags.

## State and persistence behavior
This header declares the global runtime policy knobs and core table state but does not implement storage unless `DEFINE_ACPI_GLOBALS` is set. Runtime state includes table descriptors, FADT copy, GPE counts, debug settings, OSI/interface state, and interpreter behavior flags. Firmware tables remain persistent inputs; ACPICA state is rebuilt each boot and destroyed by `acpi_terminate()`.

## Dependencies and integration points
It includes `acconfig.h`, `actypes.h`, `actbl.h`, and `acbuffer.h`, and is included by `acpi.h`. Linux ACPI bus, drivers, OSL, resource, PM, and hardware code all depend on these declarations. It is the main ABI surface between ACPICA core and its consumers.

## Risks and test signals
Risks include global policy flags being changed after initialization, reduced-hardware stubs hiding missing behavior, table reference leaks due to unmatched `acpi_get_table()`/`acpi_put_table()`, GPE handler ordering mistakes, address-space handler `_REG` sequencing, sleep-state register misuse, debug macros compiled inconsistently, and public ABI drift. Test signals include full ACPICA boot/shutdown, table load/unload and reference counting, namespace walk/evaluate paths, handler install/remove races, GPE enable/disable/wake masks, resource conversion, GAS read/write, sleep/resume, and builds with reduced hardware, no error messages, debug output, debugger, and application flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpixf.h -->
