# sources/distributed-fs/ceph-client/drivers/bus/stm32_etzpc.c

## Purpose
This driver registers the STM32 ETZPC firewall controller and filters bus children based on ETZPC decode-protection settings. It covers peripheral and memory firewall entries.

## Important APIs, Types, and Functions
`stm32_etzpc_grant_access()` validates a firewall ID, reads the relevant `ETZPC_DECPROT` field, and permits access only when the peripheral is non-secure and attributed to Cortex-A7 (`ETZPC_PROT_A7NS`). `stm32_etzpc_probe()` maps ETZPC registers, fills `struct stm32_firewall_controller`, derives `max_entries` from `ETZPC_HWCFGR`, registers the controller, runs `stm32_firewall_populate_bus()`, and populates allowed children.

## Control Flow
Probe reads hardware configuration counts for secure peripherals and AHB masters, sets the max entry range, and registers with the shared STM32 firewall list. During bus population, each child’s `access-controllers` property is resolved and `stm32_etzpc_grant_access()` determines whether the node remains available for later platform population.

## State and Persistence
Private state is the devm-allocated firewall controller plus mapped MMIO. Hardware security configuration is read-only from this driver’s perspective. Release access is intentionally a no-op.

## Dependencies and Integration Points
It depends on the STM32 firewall framework, OF phandle parsing, platform MMIO resources, and ETZPC hardware configuration registers. It integrates with child platform devices by removing unauthorized nodes before `of_platform_populate()`.

## Risks and Test Signals
Risks include no unregister if `stm32_firewall_populate_bus()` fails after registration, access decisions depending entirely on bootloader/secure firmware configuration, and ID/count mismatches from DT. Test signals include correct `max_entries` from HWCFGR, denied nodes being detached, allowed child probes, and graceful `-EACCES` for secure-only peripherals.
