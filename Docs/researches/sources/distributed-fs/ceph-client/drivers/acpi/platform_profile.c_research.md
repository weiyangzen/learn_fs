<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/platform_profile.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/platform_profile.c

## Purpose
`platform_profile.c` provides the ACPI platform profile sysfs interface. It lets platform drivers register profile handlers, exposes per-handler class devices under `platform-profile`, maintains the legacy aggregate `/sys/firmware/acpi/platform_profile*` attributes, and exports helpers to notify or cycle profiles.

## Important APIs, Types, and Functions
The main private type is `struct platform_profile_handler`, containing handler name, class device, IDA minor, visible/hidden choices bitmaps, and `platform_profile_ops`. Exported APIs are `platform_profile_register()`, `platform_profile_remove()`, `devm_platform_profile_register()`, `platform_profile_notify()`, and `platform_profile_cycle()`. Sysfs helpers include `choices_show`, `profile_show`, `profile_store`, aggregate choice/profile functions, and visibility logic for legacy attributes.

## Control Flow and State
Module init exits if ACPI is disabled, registers the class, and creates the aggregate ACPI sysfs group. Registration validates ops, calls driver `probe()` to fill choices, optionally obtains hidden choices, allocates a minor under `profile_lock`, registers a class device named `platform-profile-N`, notifies the legacy attribute, and updates group visibility. Per-device stores set only that handler after checking visible or hidden support. Legacy stores compute intersection of all registered choices, reject `custom`, set every handler, emit per-handler notifications, and notify the ACPI kobject. `platform_profile_cycle()` aggregates current profile and choices, skips custom/max-power, wraps to the next common profile, and sets all handlers.

## State and Persistence
Persistent runtime state is the class device set, IDA minors, profile choices/hidden choices, and driver-owned current profile state accessed through callbacks. Aggregate sysfs results are computed on demand and disappear when no handlers are registered.

## Dependencies and Integration Points
The file depends on ACPI kobject sysfs, Linux class/device APIs, IDA, mutex/cleanup guard helpers, bitmap operations, `find_next_bit_wrap()`, and `include/linux/platform_profile.h` callback contracts. It integrates with vendor platform drivers that implement `profile_get`, `profile_set`, `probe`, and optional `hidden_choices`.

## Risks and Test Signals
Risks include aggregate legacy semantics requiring all handlers to support a requested profile, hidden choices being allowed for per-device writes but hidden from legacy choices when only one handler exists, callback errors aborting multi-device stores mid-operation, and reliance on drivers returning valid enum values. Test signals are class device attributes `name/choices/profile`, aggregate attributes appearing only with registered handlers, uevents and sysfs notifications on changes, cycle behavior across supported choices, devm cleanup, and concurrent register/remove/store under `profile_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/platform_profile.c -->
