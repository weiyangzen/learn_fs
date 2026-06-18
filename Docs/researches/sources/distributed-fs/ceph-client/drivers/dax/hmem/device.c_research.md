# sources/distributed-fs/ceph-client/drivers/dax/hmem/device.c

Purpose: discovers soft-reserved heterogeneous-memory resources and records them under a global HMEM resource tree, registering the `hmem_platform` device when needed.

Important APIs/types/functions: module parameter `disable`, `walk_hmem_resources()`, `hmem_register_resource()`, `hmem_register_one()`, `hmem_init()`, global `hmem_active`, and `hmem_platform`.

Control flow and state: boot-time `hmem_init()` walks soft-reserve resources and calls `hmem_register_resource()`. Registration is serialized by `hmem_resource_lock`, stores ranges in `hmem_active` with target NUMA node in `res->desc`, and registers one `hmem_platform` device once. `walk_hmem_resources()` lets the HMEM platform driver later consume the recorded child resources.

Dependencies and integration: depends on memregion soft-reserve walking, platform devices, DAX HMEM bus header, NUMA target-node helpers, and module parameter handling.

Risks and test signals: duplicate resource registration, disabled module parameter, target-node propagation via `desc`, and platform device one-shot registration are risks. Test soft-reserve discovery, duplicate overlaps, `hmem.disable=1`, missing platform registration, and handoff to `hmem.c`.
