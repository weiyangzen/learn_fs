# sources/distributed-fs/ceph-client/drivers/soc/fsl/dpio/dpio-driver.c

Purpose: fsl-mc bus driver for DPAA2 DPIO objects. It opens MC control sessions, configures the DPIO, maps software portal regions, creates a `dpaa2_io` service object, and wires interrupts to the service ISR.

Important APIs and functions: `dpaa2_dpio_probe()` performs object setup; `dpaa2_dpio_remove()` tears it down. `dpaa2_dpio_get_cluster_sdest()` derives stashing destination from SoC family. `register_dpio_irq_handlers()` requests the IRQ and sets affinity hint; `dpio_driver_init()` allocates `cpus_unused_mask` and registers the fsl-mc driver.

Control flow: probe allocates a private struct, allocates an MC portal, opens and resets the DPIO, reads attributes, enables it, assigns the next unused CPU, optionally sets stashing destination, maps CENA/CINH regions with classic or DDR-backed portal behavior, allocates MC IRQs, creates `dpaa2_io`, registers IRQ, logs success, and closes the MC session. Error paths unwind in reverse order. Remove stops the service, frees IRQs, returns CPU to the unused mask, opens/disables/closes the DPIO, and frees the MC portal.

State and persistence: `cpus_unused_mask` tracks CPU assignment. Per-device `dpio_priv` stores the `dpaa2_io` service. The DPIO object state persists in MC firmware/hardware across command calls.

Dependencies and integration: depends on fsl-mc bus, DPIO MC command wrappers, SoC bus matching for stashing, DPIO portal regions, IRQ allocation, and `dpaa2_io_create()` from the service layer.

Risks and test signals: risks include CPU/DPIO count mismatch, region_count assumptions, stashing destination unknown SoC handling, and possible unwind ordering around `dpaa2_io_create()` versus IRQ free. Test signals are DPIO probe logs, CPU affinity hints, MC command success, functional DPAA2 network drivers using service APIs, and clean hot-unbind.
