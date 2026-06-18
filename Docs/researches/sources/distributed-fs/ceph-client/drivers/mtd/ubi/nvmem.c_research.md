# sources/distributed-fs/ceph-client/drivers/mtd/ubi/nvmem.c

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/nvmem.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/ubi/nvmem.c

Purpose: this file registers selected UBI volumes as read-only NVMEM providers when their device-tree node contains an `nvmem-layout` child. It lets platform data such as calibration cells be read from UBI-backed storage through the generic NVMEM framework.

Important APIs, types, and functions: `struct ubi_nvmem` tracks the registered `nvmem_device`, UBI number, volume id, usable LEB size, and list link. `ubi_nvmem_reg_read()` implements NVMEM reads by opening the volume read-only and translating linear offsets into `(lnum, offset)` UBI reads. `ubi_nvmem_add()` builds the `nvmem_config`; `ubi_nvmem_remove()` unregisters matching providers. `nvmem_notify()` handles UBI volume events. Module init/exit register and unregister a UBI volume notifier.

Control flow: on `UBI_VOLUME_ADDED`, the notifier checks for an OF node and `nvmem-layout`, validates size fields, allocates state, registers a root-only read-only NVMEM device whose size is `usable_leb_size * vi->size`, and records it in a global list. On `UBI_VOLUME_RESIZED`, it removes the old provider and falls through to add a replacement. On `UBI_VOLUME_SHUTDOWN`, it removes the provider. NVMEM reads open the volume, loop while bytes remain, read at most one usable LEB segment per iteration, and close the volume.

State and persistence behavior: this module adds no flash format. Persistent bytes are the underlying UBI volume contents. Runtime state is the global `nvmem_devices` list protected by `devices_mutex`; each read opens the volume fresh, so it observes current volume mapping and size as exposed by UBI notifications.

Dependencies and integration points: it depends on the UBI notifier API from `kapi.c`, UBI read-only volume access, OF device nodes attached to UBI volumes, and `<linux/nvmem-provider.h>`. It is careful to use UBI volume info devices (`vi->dev`) for naming, ownership, and OF linkage.

Risks: pointer arithmetic on `void *val` relies on the kernel's GNU C behavior. Notifier documentation says callbacks must not use UBI API, but the NVMEM read path uses UBI API outside the notifier, while add/remove use only metadata and NVMEM registration. Missing `nvmem-layout` silently skips registration. Resize removes and recreates providers, which can invalidate consumers during topology changes.

Test signals: boot with a UBI volume node containing `nvmem-layout` and verify an NVMEM provider appears; read cells crossing LEB boundaries; resize a volume and observe provider re-registration with the new size; remove/detach the volume and verify unregister; check read-only/root-only policy; and validate failure paths for missing OF nodes and invalid volume sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ubi/nvmem.c -->
