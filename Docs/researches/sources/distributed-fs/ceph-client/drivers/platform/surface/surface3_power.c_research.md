# sources/distributed-fs/ceph-client/drivers/platform/surface/surface3_power.c

## Purpose
Implements support for the Surface 3 `MSHW0011` power IC arrangement. It creates a secondary battery I2C client, services ACPI GSBus OperationRegion requests for battery/adapter data, polls for changes, and triggers ACPI DSM notifications for adapter, battery status, and battery info updates.

## Important APIs, Types, And Functions
Core state is `struct mshw0011_data`, holding adapter and battery I2C clients, notify mask, polling task, cached charging/full-capacity state, and trip point. ACPI buffer layouts include `struct bix`, `struct bst`, `struct gsb_command`, and `struct gsb_buffer`. Important functions are `mshw0011_notify()`, `mshw0011_bix()`, `mshw0011_bst()`, `mshw0011_adp_psr()`, `mshw0011_isr()`, `mshw0011_poll_task()`, `mshw0011_space_handler()`, and space-handler install/remove helpers.

## Control Flow
I2C probe allocates state for ACPI HID `MSHW0011`, treats the probed client as adapter `ADP1`, creates a battery client at ACPI index 1, queries DSM version/mask, starts a polling kthread, installs an ACPI GSBus address-space handler, and clears ACPI dependencies. The space handler decodes raw-process GSB buffers: adapter `PSR` queries read adapter status, battery commands serve `_STA`, `_BIX`, `_BST`, `_BTP`, or reject unsupported commands. The poll task wakes every two seconds, reads adapter status, battery status, and battery info, compares cached values, and notifies ACPI via DSM when changes are detected.

## State And Persistence Behavior
Cached state tracks last adapter charging state, battery charging state, trip point, and full-charge capacity for change detection. No persistent storage is written. The polling kthread is freezable and stopped on remove/error if running. The ACPI private handler data is allocated at install and freed on remove.

## Dependencies And Integration Points
Depends on ACPI DSM and GSBus OperationRegion APIs, I2C/SMBus reads, `i2c_acpi_new_device()`, kthreads/freezer, unaligned access, and packed ACPI battery structures. It integrates with ACPI battery devices indirectly by satisfying their OperationRegion accesses and by firing DSM notifications.

## Risks
Polling exits permanently on the first `mshw0011_isr()` error, which may make transient SMBus failures stop future notifications. `notify_mask` is assigned the boolean result of `mask == MSHW0011_EV_2_5_MASK`, so it becomes 0/1 rather than the returned mask value; this matches the code as written but is worth checking against firmware expectations. The space handler uses `value64` as a packed GSB buffer pointer and depends on exact ACPI layout. Unsupported battery commands return `AE_BAD_PARAMETER`, which may surface as firmware-visible errors.

## Test Signals
Test adapter plug/unplug, charge/discharge transitions, BIX full-capacity changes, serial-number read `-EREMOTEIO`, ACPI battery methods backed by GSBus, remove while poll task runs, suspend/freezer behavior, and transient SMBus error recovery expectations.
