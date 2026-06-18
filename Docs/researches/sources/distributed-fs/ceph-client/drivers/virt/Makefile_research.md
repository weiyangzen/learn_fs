# sources/distributed-fs/ceph-client/drivers/virt/Makefile

Purpose: top-level Makefile for virtualization support drivers. It maps virtualization Kconfig symbols to object files and subdirectories.

Important APIs, types, and functions: object assignments include `fsl_hypervisor.o`, `vmgenid.o`, `vboxguest/`, `nitro_enclaves/`, `acrn/`, and `coco/`.

Control flow: Kbuild includes objects conditionally by config. `vboxguest/` and `coco/` are entered unconditionally from this Makefile, while internal Kconfig/Makefiles decide built objects. `acrn/` is included when `CONFIG_ACRN_HSM` is set.

State and persistence: build-system state only.

Dependencies and integration points: tied to `drivers/virt/Kconfig` and child directory Makefiles such as `drivers/virt/acrn/Makefile`.

Risks: unconditional directory traversal can expose child Makefile issues even when no objects are selected. Config-symbol mismatches would silently omit drivers.

Test signals: build matrix for each virtualization driver config and `make drivers/virt/` traversal with features disabled.
