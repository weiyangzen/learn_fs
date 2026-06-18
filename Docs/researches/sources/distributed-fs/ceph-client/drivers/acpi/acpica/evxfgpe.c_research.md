# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfgpe.c

## Purpose
`evxfgpe.c` is the external GPE control API layer. It initializes GPE blocks, manages runtime and wake references, masks/unmasks or directly sets GPE hardware state, installs/removes user GPE blocks, and maps system GPE indices back to GPE devices.

## Important APIs, Types, And Functions
Exports include `acpi_update_all_gpes`, `acpi_enable_gpe`, `acpi_disable_gpe`, `acpi_set_gpe`, `acpi_mask_gpe`, `acpi_mark_gpe_for_wake`, `acpi_setup_gpe_for_wake`, `acpi_set_gpe_wake_mask`, `acpi_clear_gpe`, `acpi_get_gpe_status`, `acpi_dispatch_gpe`, `acpi_finish_gpe`, `acpi_disable_all_gpes`, `acpi_enable_all_runtime_gpes`, `acpi_enable_all_wakeup_gpes`, `acpi_any_gpe_status_set`, `acpi_install_gpe_block`, `acpi_remove_gpe_block`, and `acpi_get_gpe_device`. Key types are `struct acpi_gpe_event_info`, `struct acpi_gpe_register_info`, `struct acpi_gpe_block_info`, and `struct acpi_gpe_notify_info`.

## Control Flow
Initialization walks all GPE blocks once via `acpi_ev_walk_gpe_list`, initializes each block, sets `acpi_gbl_all_gpes_initialized`, and polls pre-triggered edge GPEs if needed. `acpi_enable_gpe` validates dispatchability and adds a runtime reference; first reference enables hardware and may trigger a poll. `acpi_disable_gpe` removes a reference and disables only at zero. Direct set bypasses reference counting and toggles `disable_for_dispatch`. Wake setup validates a wake device, optionally converts an unhandled GPE into implicit notify dispatch, removes auto-enable references for PRW wake GPEs, appends a notify target, and marks `ACPI_GPE_CAN_WAKE`. Wake mask updates `enable_for_wake` bits. GPE block install validates a device node, creates a block, creates/attaches a device object if needed, and stores `device.gpe_block`; removal deletes the block and clears the pointer.

## State And Persistence
Runtime state includes GPE flags, runtime reference counts, wake masks, notification lists, per-device GPE block pointers, and global count/list state. All per-GPE changes are in memory plus hardware enable/status registers.

## Dependencies And Integration Points
The file depends on the GPE core, hardware register helpers, namespace validation, FADT/user GPE block management, and PM sleep/wake code that calls PRW-related APIs.

## Risks
Bypassing reference counts with `acpi_set_gpe` can break shared GPE users. Wake setup allocation must happen before the spinlock to avoid sleeping while locked. `acpi_remove_gpe_block` returns directly on a null attached object without releasing the namespace mutex, which is a control-flow hazard in this version. Implicit notify assumes level-triggered behavior for compatibility.

## Test Signals
Coverage should include first/last reference enablement, no-handler rejection, direct set versus reference-counted enable state, wake mark/setup duplicate detection, wake mask bit changes, GPE block install/remove lifecycle, skipped-GPE status scans, and lock release on all error paths.
