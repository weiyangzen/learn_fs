## sources/distributed-fs/ceph-client/drivers/s390/crypto/Makefile

Purpose: describes how s390 crypto driver objects are grouped into kernel modules based on Kconfig symbols. It wires AP bus, zcrypt, protected-key handlers, and VFIO AP support into the build.

Important APIs/types/functions: build groups include `ap-objs`, `zcrypt-objs`, `pkey-objs`, `pkey-cca-objs`, `pkey-ep11-objs`, `pkey-pckmo-objs`, `pkey-uv-objs`, and `vfio_ap-objs`. The controlling symbols are `CONFIG_AP`, `CONFIG_ZCRYPT`, `CONFIG_PKEY`, `CONFIG_PKEY_CCA`, `CONFIG_PKEY_EP11`, `CONFIG_PKEY_PCKMO`, `CONFIG_PKEY_UV`, and `CONFIG_VFIO_AP`.

Control flow: there is no runtime flow, but build dependency order is encoded: zcrypt and adapter drivers depend on `ap.o`; pkey base/API/sysfs build into `pkey.o`; hardware-specific pkey handlers are separate modules/objects that register with the pkey base.

State and persistence: build-time only. Its decisions determine which runtime modules and symbol exports exist.

Dependencies and integration: integrates AP core (`ap_bus.o`, `ap_card.o`, `ap_queue.o`), zcrypt card/queue/message drivers, pkey handlers, and VFIO AP matrix support.

Risks and test signals: risks are missing object membership when adding a handler, broken module autoload names used by `pkey_handler_request_modules()`, and unresolved symbols if AP/zcrypt ordering changes. Test with built-in and modular configurations for AP, ZCRYPT, PKEY, individual pkey handlers, and VFIO_AP.
