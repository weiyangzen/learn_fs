# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pseries/pmem.c

Purpose: Handles DLPAR hot-add/hot-remove of pSeries persistent memory device-tree nodes and initial population of persistent-memory platform devices.

Important APIs/types/functions: Uses global `pmem_node`, helpers `pmem_drc_add_node()`, `pmem_drc_remove_node()`, exported `dlpar_hp_pmem()`, OF match table `drc_pmem_match`, and init `pseries_pmem_init()`.

Control flow: Init finds the `ibm,persistent-memory` parent on POWER8+ and probes child `ibm,pmemory` devices through OF platform code. Hotplug events validate DRC-index event format, take the device hotplug lock, acquire or release the DRC, configure connectors, attach/detach OF nodes, and rely on OF reconfig notifiers to create or tear down platform devices consumed by `papr_scm.c`.

State and persistence: Keeps a referenced global pointer to the persistent-memory parent node. Device state is represented in the dynamic OF tree and DRC ownership in firmware.

Dependencies and integration points: Integrates with pseries DLPAR RTAS helpers, OF dynamic attach/detach, platform bus probing, memory hotplug build config, and the PAPR SCM platform driver.

Risks: Failed attach after configure must release the DRC and free connector nodes carefully. Failed release after detach attempts to reattach the node. Hotplug during early boot is handled by rediscovering `pmem_node`, but lifetime/reference handling remains important.

Test signals: Initial discovery, pmem hot-add/hot-remove, unsupported event id/action, missing parent node, configure-connector failure, attach/detach rollback, and interaction with `papr_scm_probe/remove`.

Source read size: 167 lines, 4357 bytes.
