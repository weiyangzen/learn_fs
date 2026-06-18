## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/acpi.c

### Purpose
`acpi.c` registers a small ACPI notifier for NVKM devices so AC adapter changes can refresh Nouveau clock power-source state.

### Important APIs, types, and functions
The public functions are `nvkm_acpi_init()` and `nvkm_acpi_fini()`. Under `CONFIG_ACPI`, static `nvkm_acpi_ntfy()` handles ACPI bus events.

### Control flow
Init assigns `device->acpi.nb.notifier_call` and registers the ACPI notifier. The notifier checks for `device_class == "ac_adapter"` and calls `nvkm_clk_pwrsrc(device)`. Fini unregisters the notifier. When `CONFIG_ACPI` is disabled, init/fini compile to no-ops.

### State and persistence behavior
The notifier block is stored in `device->acpi.nb` for the device lifetime while registered. No additional state is persisted in this file.

### Dependencies
It depends on `acpi.h`, `core/device.h`, `subdev/clk.h`, and ACPI notifier APIs when configured.

### Integration points
`device/base.c` calls `nvkm_acpi_init()` after subdevices initialize and `nvkm_acpi_fini()` during device fini. The clock subdevice consumes AC/DC source changes.

### Risks
Notifier registration must be balanced with unregister during teardown. The string match is narrow to AC adapter events. Calling into clock code during ACPI notification requires the device and clock subdevice to remain valid.

### Test signals
Builds with and without `CONFIG_ACPI`, AC adapter plug/unplug while Nouveau is loaded, clock power-source updates, and device unload after notifier registration are useful checks.
