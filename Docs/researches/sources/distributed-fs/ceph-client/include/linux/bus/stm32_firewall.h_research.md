## sources/distributed-fs/ceph-client/include/linux/bus/stm32_firewall.h

**Purpose:** This header defines the controller-side STM32 firewall framework interface. It lets STM32 firewall providers register controllers and participate in boot-time device-tree population decisions.

**Important APIs/types/functions:** Firewall type bits are `STM32_PERIPHERAL_FIREWALL`, `STM32_MEMORY_FIREWALL`, and `STM32_NOTYPE_FIREWALL`. `struct stm32_firewall_controller` stores name, device, MMIO base, list entry, type, maximum entries, and callbacks `grant_access`, `release_access`, and `grant_memory_range_access`. Functions are `stm32_firewall_controller_register()`, `stm32_firewall_controller_unregister()`, and `stm32_firewall_populate_bus()`.

**Control flow, state, persistence:** Registered controllers become part of a framework-maintained list. Boot population calls into controllers to decide whether protected DT nodes are accessible. Access grants may change firewall hardware state and must be paired with release where applicable.

**Dependencies/integration:** Depends on device tree, platform devices, list infrastructure, and MMIO. Integrates with `stm32_firewall_device.h` consumers and STM32 access-controller bindings.

**Risks and test signals:** Risks include registering controllers before MMIO is ready, incorrect `max_entries`, missing release paths, and populating inaccessible devices that later fault. Test signals are DT boot with protected peripherals/memory, denied-access probes returning errors rather than crashing, controller unregister tests, and memory-range grant coverage.
