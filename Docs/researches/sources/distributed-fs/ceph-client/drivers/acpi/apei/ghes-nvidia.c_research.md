# sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes-nvidia.c

## Purpose
Registers an NVIDIA-specific GHES vendor CPER section handler and prints NVIDIA error payload fields when firmware reports the matching section GUID.

## Important APIs, Types, And Functions
Defines `struct cper_sec_nvidia` for the vendor payload and `struct nvidia_ghes_private` for the notifier. Main functions are `nvidia_ghes_notify()`, `nvidia_ghes_print_error()`, and `nvidia_ghes_probe()`.

## Control Flow
The platform driver matches ACPI HID `NVDA2012`. Probe allocates private state and registers a device-managed GHES vendor notifier. On notification, the handler imports the CPER section GUID, ignores non-NVIDIA sections, validates minimum payload size, prints metadata at severity-dependent log level, validates variable register array length, then prints register address/value pairs.

## State And Persistence
State is device-managed notifier/private memory. There is no persistent state beyond kernel logs.

## Dependencies And Integration Points
Depends on GHES vendor notifier APIs, ACPI platform matching, CPER generic data helpers, GUID helpers, and little-endian conversion.

## Risks
Malformed firmware may advertise too-small sections or a register count exceeding section length. The handler avoids out-of-bounds register access by checking `struct_size()` before iterating.

## Test Signals
Use synthetic CPER vendor records for GUID filtering, minimum-size rejection, severity log level selection, zero-register sections, truncated register arrays, and device-managed notifier unregister on device removal.
