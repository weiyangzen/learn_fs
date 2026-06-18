## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utosi.c

Purpose: `utosi.c` implements ACPICA support for the predefined `_OSI` method and manages the global list of interface strings reported as supported or unsupported to firmware.

Important APIs and functions: the static `acpi_default_supported_interfaces[]` lists Windows vendor strings through `"Windows 2022"` plus feature-group strings, marking optional features invalid by default. `acpi_ut_initialize_interfaces` links this static array and publishes it as `acpi_gbl_supported_interfaces`. `acpi_ut_interface_terminate` frees dynamic entries and resets static flags. `acpi_ut_install_interface`, `acpi_ut_remove_interface`, `acpi_ut_update_interfaces`, and `acpi_ut_get_interface` manipulate the list while the caller holds `acpi_gbl_osi_mutex`. `acpi_ut_osi_implementation` is the AML-visible `_OSI` implementation.

Control flow: `_OSI` validates its single string argument, creates an integer return object, searches the interface list under the `_OSI` mutex, returns all-ones for supported non-invalid strings, updates `acpi_gbl_osi_data` to the newest requested Windows value, releases the mutex, then invokes an optional host interface handler that can override support.

State and dependencies: persistent state includes the linked interface list, dynamic allocation for runtime interfaces, invalid/default-invalid flags, `acpi_gbl_osi_data`, `acpi_gbl_interface_handler`, and `acpi_gbl_osi_mutex`.

Integration points: public APIs in `utxface.c` wrap these functions. AML method execution routes `_OSI` calls here, and OS policy code can install handlers or modify interface strings before namespace initialization paths execute firmware methods.

Risks: firmware behavior depends heavily on exact string support policy. Dynamic list operations require external locking. Updating the default Windows strings is compatibility-sensitive because it can select different firmware code paths.

Test signals: lookup of valid, invalid, removed, and dynamically re-added strings; optional feature toggling; interface handler override behavior; `_OSI` non-string argument rejection; and Windows version tracking should be verified.
