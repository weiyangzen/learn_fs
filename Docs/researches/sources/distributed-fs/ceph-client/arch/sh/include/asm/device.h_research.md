# sources/distributed-fs/ceph-client/arch/sh/include/asm/device.h



Source read size: 17 lines, 442 bytes.



Purpose: SH device extension declarations.

Important APIs/types/functions: `platform_resource_setup_memory()` and `plat_early_device_setup()`.

Control flow: platform code calls helpers to allocate contiguous memory resources and register early devices.

State and persistence: resources and platform devices persist elsewhere.

Dependencies and integration points: platform bus, early platform code, board setup.

Risks and test signals: wrong resource setup can overlap memory. Test through SH defconfig/allmodconfig builds plus focused runtime paths that include this header.
