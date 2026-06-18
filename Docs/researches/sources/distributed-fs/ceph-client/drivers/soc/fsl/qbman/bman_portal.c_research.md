# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/bman_portal.c

Purpose: DPAA1 BMan portal platform driver. It maps CE/CI portal regions, assigns portals to CPUs, initializes affine BMan portals, handles CPU hotplug IRQ affinity changes, and performs kexec cleanup when needed.

Important APIs and functions: `bman_portal_probe()` performs platform probing; `init_pcfg()` calls `bman_create_affine_portal()` and enables RCR interrupt source; `bman_online_cpu()` and `bman_offline_cpu()` move IRQ affinity; `bman_portals_probed()` exports portal probe status; `bman_portal_driver_register()` registers platform driver and CPU hotplug callbacks.

Control flow: probe defers until BMan CCSR is probed, allocates portal config, obtains CE/CI resources and IRQ, maps CE with `memremap()` and CI with `ioremap()`, assigns the first unused CPU under `bman_lock`, initializes the portal when assigned, adjusts affinity if CPU is offline, and, once all portals are considered probed, drains all pools if BMan required cleanup.

State and persistence: `affine_bportals[NR_CPUS]`, `portal_cpus`, `__bman_portals_probed`, and per-config mappings persist. Hardware portal rings persist in mapped CE/CI regions.

Dependencies and integration: depends on `bman_is_probed()` from CCSR, `bman_create_affine_portal()` from API layer, DPAA portal resource ordering, CPU hotplug, and IRQ affinity support.

Risks and test signals: risks include `__bman_portals_probed` set when CPU slots are exhausted rather than when all device-tree portals are seen, cleanup depending on a usable affine portal, and no full remove path. Test signals are portal probe logs per CPU, IRQ affinity changes across CPU online/offline, successful pool shutdown after kexec, and DPAA buffer operations on every assigned CPU.
