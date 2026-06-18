# sources/distributed-fs/ceph-client/drivers/bus/fsl-mc/fsl-mc-bus.c

Purpose: implements the Freescale/NXP Management Complex platform and `fsl-mc` bus core. It registers the `fsl-mc` bus type, binds MC object drivers by vendor/type, creates Linux devices for DPRC and child objects, configures DMA/IOMMU identity through ICIDs, exposes `rescan` and `autorescan` bus attributes, and probes the root `fsl,qoriq-mc`/`NXP0008` platform device.

Important APIs and types: `struct fsl_mc` stores the root DPRC, address translation ranges, and MC control registers. `struct fsl_mc_addr_translation_range` maps MC offsets to CPU physical addresses. Exported entry points include `fsl_mc_bus_type`, device types for object classes, `__fsl_mc_driver_register()`, `fsl_mc_driver_unregister()`, `fsl_mc_get_version()`, `fsl_mc_device_add()`, `fsl_mc_device_remove()`, and `fsl_mc_get_endpoint()`.

Control flow: `postcore_initcall()` registers the bus, platform driver, DPRC driver, allocator driver, and a platform-bus notifier. Probe maps optional MC registers, resumes firmware after IOMMU setup, creates root MC I/O, queries firmware version/container ID/API version, parses DT ranges, and adds the root DPRC device. Device addition allocates either `struct fsl_mc_bus` for DPRCs or `struct fsl_mc_device`, fills object descriptors, ICIDs, DMA masks, MSI domains, MMIO regions, and calls `device_add()`.

State and persistence: state is runtime-only: global firmware version, global portal base workaround, per-platform root bus data, bus scan mutexes, and device-model objects. Remove destroys root MC I/O, unregisters notifier, and pauses MC firmware to make kexec safer.

Dependencies and integration: depends on DPRC firmware commands, `mc_send_command()`, FSL MC allocator/IRQ helpers, OF/ACPI DMA configuration, IOMMU default-domain APIs, MSI domains, and Linux device model matching/modalias. Integration points are sysfs bus controls, platform probe/remove, DPRC object scanning, and exported registration helpers for MC client drivers.

Risks: address translation and the DPMCP base-address workaround are firmware-version sensitive; DMA configuration depends on the correct root ancestor and ICID; `autorescan_show()` assumes a root DPRC writes the buffer; notifier/probe ordering matters because MC firmware may fault if not paused before SMMU setup. Test signals include OF and ACPI probe, root DPRC enumeration, `rescan`, `autorescan`, child DPRC endpoint lookup, IOMMU domain attach/detach, MSI inheritance, and kexec/remove behavior.
