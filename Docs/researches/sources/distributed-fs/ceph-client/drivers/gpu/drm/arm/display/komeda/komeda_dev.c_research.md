# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/komeda/komeda_dev.c

Purpose: creates, initializes, exposes, resumes/suspends, and destroys the core `komeda_dev` hardware object.

Important APIs/types/functions: exported `komeda_dev_create()`, `komeda_dev_destroy()`, `komeda_dev_resume()`, and `komeda_dev_suspend()`. Internal helpers provide debugfs register dump, sysfs `core_id`, `config_id`, `aclk_hz`, and device-tree parsing for IRQ, reserved memory, pipeline nodes, pixel clocks, output ports, and output links.

Control flow: create allocates `komeda_dev`, maps registers, enables `aclk`, identifies chip, initializes format table, enumerates resources, parses DT, assembles pipelines, configures DMA segment size, detects IOMMU, disables clock, creates sysfs/debugfs, and returns the device. Destroy removes sysfs/debugfs, re-enables clock for teardown, destroys pipelines, releases reserved memory and chip data, unmaps registers, releases clock, and frees memory. Resume enables clock/IRQs and optionally connects IOMMU/TBU; suspend disconnects, disables IRQs, and disables clock.

State and persistence: holds MMIO base, clocks, IRQ, chip info, format table, pipelines, IOMMU domain, debugfs root, display mode, and error verbosity. Sysfs/debugfs expose runtime hardware state.

Dependencies/integration: platform resources, OF graph, reserved memory, DMA/IOMMU, debugfs/sysfs, D71 identify funcs, and Komeda pipeline assembly.

Risks: error paths call destroy on partially initialized objects. Manual devm cleanup plus devm ownership needs care. DT pipeline nodes and pxclk names are mandatory. Test signals: probe failure injection, DT variants, sysfs/debugfs reads under runtime PM, IOMMU and no-IOMMU devices, and repeated bind/unbind.
