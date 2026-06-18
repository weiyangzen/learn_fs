# sources/distributed-fs/ceph-client/drivers/bus/stm32_firewall.c

## Purpose
This file implements the common STM32 firewall framework used by ETZPC, RIFSC, and debug-bus providers. It parses device-tree access-controller phandles, tracks registered firewall controllers, provides exported grant/release helpers for consumers, and filters bus children before platform population.

## Important APIs, Types, and Functions
Exported consumer APIs are `stm32_firewall_get_firewall()`, `stm32_firewall_grant_access()`, `stm32_firewall_grant_access_by_id()`, `stm32_firewall_release_access()`, `stm32_firewall_release_access_by_id()`, and `stm32_firewall_get_grant_all_access()`. Controller APIs are `stm32_firewall_controller_register()`, `stm32_firewall_controller_unregister()`, and `stm32_firewall_populate_bus()`. Global state is `firewall_controller_list` protected by `firewall_controller_list_lock`.

## Control Flow
Consumers parse `access-controllers` with `of_for_each_phandle()`, match each provider phandle to an already registered controller, copy firewall ID and extra args into caller storage, and optionally grant all accesses with unwind on failure. Controllers register into the global list. During `stm32_firewall_populate_bus()`, each available child must have at least one access controller; denied access causes `of_detach_node(child)` so the platform core will not probe it.

## State and Persistence
Controller registration persists in a global list until unregister. Per-device firewall data can be devm allocated by `stm32_firewall_get_grant_all_access()`, while populate-bus uses temporary allocations. Access state itself is owned by provider callbacks and may map to hardware semaphores or firmware sessions.

## Dependencies and Integration Points
The framework depends on OF phandle iteration, mutex/list infrastructure, exported STM32 firewall types, and provider callbacks. It is a central integration point between bus controllers and child drivers that need explicit access grants.

## Risks and Test Signals
Risks include probe-order dependency because providers must be registered before consumers parse phandles, possible permanent DT node detachment during denied access, mandatory `access-controllers` for firewall bus children, and no internal type filtering before calling provider grant callbacks. Test signals include successful multi-controller phandle parsing, correct unwind of granted accesses, denied children not probing, and list registration/unregistration under repeated probe/remove.
