# sources/distributed-fs/ceph-client/drivers/acpi/wakeup.c

### Purpose
`wakeup.c` manages ACPI wakeup devices around system sleep and provides a small callback registry for drivers whose wake IRQ is shared with the ACPI SCI.

### Important APIs, Types, And Functions
The main APIs are `acpi_enable_wakeup_devices()`, `acpi_disable_wakeup_devices()`, `acpi_wakeup_device_init()`, `acpi_register_wakeup_handler()`, `acpi_unregister_wakeup_handler()`, and `acpi_check_wakeup_handlers()`. `struct acpi_wakeup_handler` stores a callback and opaque context on a protected list.

### Control Flow
Enable/disable paths iterate `acpi_wakeup_device_list`, skip invalid or unsupported sleep states, require either `device_may_wakeup()` or ACPI prepare count, then set GPE wake masks and optionally power wake devices. Init enables button GPEs and turns on wakeup for devices capable of wake. SCI-shared handlers are only registered when the given IRQ equals `acpi_sci_irq`; wake checking calls handlers until one reports true.

### State, Persistence, And Dependencies
State lives in ACPI device wake flags, GPE masks, wake power state, and the static handler list guarded by `acpi_wakeup_handler_mutex`. Sleep entry/exit code calls this while hotplug is effectively quiesced, so the device list is not locked in the suspend paths.

### Integration Points
This code integrates ACPI core wake device discovery, device power-management wake flags, GPE programming, ACPI sleep transitions, and drivers that need to distinguish SCI wake from a shared device interrupt.

### Risks
Incorrect wake mask handling can either miss wake events or leave spurious wake sources armed. Handler unregister walks with `list_for_each_entry()` and deletes a matching entry then breaks; callers must avoid duplicate registrations with the same callback/context. `acpi_check_wakeup_handlers()` intentionally runs without locking, so it relies on sleep serialization.

### Test Signals
Signals include wake from buttons and device GPEs in supported S-states, wake power enable/disable pairing, SCI-shared IRQ devices reporting wake correctly, no wake handler leaks after driver unload, and no spurious wake storms after resume.
