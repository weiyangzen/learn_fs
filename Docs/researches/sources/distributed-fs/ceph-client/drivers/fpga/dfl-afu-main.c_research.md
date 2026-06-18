## sources/distributed-fs/ceph-client/drivers/fpga/dfl-afu-main.c

Purpose: this is the main Intel DFL Accelerated Function Unit port driver. It provides the DFL port char-device ABI, port reset/enable control, sysfs attributes, MMIO region setup, DMA map/unmap ioctls, mmap support, and subfeature ioctl dispatch.

Important APIs and functions: `__afu_port_enable()` and `__afu_port_disable()` manage the port soft-reset bit with a nested `disable_count` and poll `PORT_CTRL_SFTRST_ACK`. `port_reset()` disables then enables the port. Header sysfs attributes expose port ID, latency tolerance reporting, AP1/AP2 events, power state, and revision-zero user clock command/status registers. AFU sysfs exposes `afu_id`. File operations implement exclusive/shared open tracking, release cleanup, ioctls for API version, region info, DMA map/unmap, port reset, AFU/error/user interrupt subfeatures, and `mmap()`.

Control flow: probe allocates `struct dfl_afu`, initializes MMIO/DMA region containers, initializes all enumerated port features, and registers file operations. The header feature resets the port during init. AFU and STP features add mmap-capable MMIO regions based on platform resources. Open increments DFL use count and can honor `O_EXCL`; release decrements it and, on last close, clears IRQ triggers, resets the port, and destroys DMA regions.

State and persistence: AFU private state stores MMIO region list, current file offset allocation, DMA RB tree, region count, and user-message count. `disable_count` lives in shared `dfl_feature_dev_data`. MMIO region metadata persists for device lifetime; DMA mappings persist per device until unmapped or last close. Hardware reset and status registers are mutated through sysfs/ioctl/release paths.

Dependencies and integration: it relies on DFL feature-device infrastructure, AFU helper files, DFL IRQ helpers, Linux char-device/mmap APIs, and parent resource layout. It registers `dfl_fpga_port_ops` so FME bridges can enable/disable a port during PR.

Risks: any final close resets the port and destroys all DMA regions, so multi-process users must coordinate carefully. `mmap()` allows noncached physical mappings for regions marked by feature init; incorrect resource indexes can expose wrong MMIO. User clock sysfs is hidden for feature revisions greater than zero, so ABI depends on hardware revision. DMA map/unmap is delegated to a physically contiguous implementation.

Test signals: test shared versus exclusive opens, reset ioctl argument validation, sysfs attribute visibility by feature/revision, AFU/STP region info and mmap permissions, DMA map/unmap ioctl copy failure unwinds, IRQ trigger cleanup on last release, and FME bridge enable/disable calls through registered port ops.
