# sources/distributed-fs/ceph-client/drivers/amba/bus.c

### Purpose
`bus.c` implements the Linux AMBA bus for ARM PrimeCell/CoreSight-style devices: matching, probing, PM, DMA setup, device allocation/registration, driver registration, sysfs attributes, and memory-region helpers.

### Important APIs, Types, And Functions
Exported APIs include `amba_bustype`, `dev_is_amba()`, `__amba_driver_register()`, `amba_driver_unregister()`, `amba_device_add()`, `amba_device_alloc()`, `amba_device_register()`, `amba_device_put()`, `amba_device_unregister()`, `amba_request_regions()`, and `amba_release_regions()`. Internal flow uses `amba_lookup()`, `amba_read_periphid()`, `amba_match()`, `amba_probe()`, `amba_remove()`, and runtime PM callbacks.

### Control Flow
Device registration claims the parent memory resource and tries to read peripheral/component IDs; if resources are not ready, uevents are suppressed until match can power the device, enable `apb_pclk`, deassert reset, ioremap, read PID/CID registers, and resubmit an add uevent. Matching honors `driver_override` before ID table lookup. Probe decodes OF IRQs, applies OF clock defaults, attaches PM domain, enables pclk, enables runtime PM, and calls the AMBA driver's probe. Remove reverses runtime PM and clock setup.

### State, Persistence, And Dependencies
Each `amba_device` carries peripheral ID, component ID, CoreSight UCI data, pclk, resource, IRQs, DMA masks/params, override string, and `periphid_lock`. The bus depends on clocks, resets, OF, ACPI DMA configuration, IOMMU default domains, PM domains, runtime PM, and Linux device core.

### Integration Points
It is the binding layer for AMBA drivers and supports both OF and ACPI firmware paths. It emits `AMBA_ID` and modalias uevents for module loading and registers a late stub driver when modules are enabled so ID reads can occur even before real AMBA drivers load.

### Risks
ID reads require powered and clocked hardware; failures are mapped to `-EPROBE_DEFER` in match to avoid driver registration failure. Clock/PM-domain cleanup is subtle on probe failure paths. DMA cleanup assumes a valid driver object and respects `driver_managed_dma`. Runtime PM clock toggling must honor IRQ-safe devices.

### Test Signals
Signals include correct sysfs `id`, `resource`, and `driver_override`; module autoload modaliases; deferred ID read recovery; CoreSight UCI matching; probe/remove clock balance; OF IRQ decoding; ACPI/OF DMA setup; IOMMU default-domain use; and region request/release behavior.
