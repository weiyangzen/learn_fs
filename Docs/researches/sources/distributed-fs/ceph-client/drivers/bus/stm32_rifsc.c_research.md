# sources/distributed-fs/ceph-client/drivers/bus/stm32_rifsc.c

## Purpose
This driver registers the STM32 RIFSC firewall controller, grants access to RIF-protected peripherals/memory based on security/CID/semaphore configuration, filters bus children, and optionally exposes a debugfs dump of RIFSC resource configuration.

## Important APIs, Types, and Functions
Core access functions are `stm32_rifsc_grant_access()` and `stm32_rifsc_release_access()`. Semaphore helpers `stm32_rif_acquire_semaphore()` and `stm32_rif_release_semaphore()` coordinate CID1 ownership when semaphore mode is enabled. `stm32_rifsc_probe()` maps registers, computes RISUP/RIMU/RISAL counts from `RIFSC_RISC_HWCFGR2`, registers the firewall controller, filters children, creates debugfs when enabled, and populates allowed children. Debugfs helpers read RISUP, RIMU, and RISAL register groups into printable tables.

## Control Flow
Grant access first bounds-checks the firewall ID, reads the security bit for the peripheral, denies secure-only resources, then checks CID filtering. If CID filtering is disabled, access is allowed. If semaphore mode is enabled, CID1 must be in the semaphore whitelist and the driver attempts to acquire the semaphore. Otherwise the static CID must be CID1. Release writes the semaphore register only when held.

## State and Persistence
Runtime state is the firewall controller and optional debugfs private data. Hardware state includes acquired RIF semaphores, which persist until release or reset. Debugfs reads live registers. For STM32MP21, the driver overrides an incorrect hardware RISAL count to zero.

## Dependencies and Integration Points
It depends on the STM32 firewall framework, OF matching, platform MMIO, debugfs, bitfield helpers, and SoC-specific resource-name tables. It integrates with child platform devices by detaching unauthorized nodes before population.

## Risks and Test Signals
Risks include semaphore races, failure to unregister the controller on some later probe failures, debugfs name-table bounds if hardware counts exceed compiled arrays, and CID assumptions fixed to CID1. Test signals include correct allowed/denied child probing, semaphore acquisition/release around client use, debugfs `stm32_firewall/rifsc` matching hardware, and STM32MP21 RISAL workaround behavior.
