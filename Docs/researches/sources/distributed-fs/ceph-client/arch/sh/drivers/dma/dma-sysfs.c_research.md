# sources/distributed-fs/ceph-client/arch/sh/drivers/dma/dma-sysfs.c



Source read size: 170 lines, 4296 bytes.



Purpose: sysfs exposure for the legacy SH DMA API.

Important APIs/types/functions: `dma_subsys_init()`, root `devices` attribute, per-channel `dev_id`, `config`, `mode`, `count`, `flags` attributes, `dma_create_sysfs_files()`, and `dma_remove_sysfs_files()`.

Control flow: postcore init registers a `dma` bus and root summary attribute. Each DMAC registration creates a device per channel, attaches attributes, and symlinks the channel from the provider platform device; unregister removes files, link, and device.

State and persistence: runtime sysfs devices mirror `struct dma_channel` fields. Writes to `config`, `mode`, and `dev_id` immediately mutate channel state only for the running kernel.

Dependencies and integration points: depends on platform devices from `register_dmac()`, `to_dma_channel()`, and legacy DMA API configuration callbacks.

Risks and test signals: `dev_id` writes use unbounded `strcpy`; root `devices` loops only first 16 virtual channels; partial attribute creation failures leave registered devices. Test sysfs reads/writes, invalid config values, channel removal, and large `dev_id` input.
