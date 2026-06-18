## sources/distributed-fs/ceph-client/include/linux/bus/stm32_firewall_device.h

**Purpose:** This header defines the consumer-side STM32 firewall interface for devices that need access grants from one or more firewall controllers.

**Important APIs/types/functions:** `STM32_FIREWALL_MAX_EXTRA_ARGS` limits per-entry arguments. `struct stm32_firewall` stores an opaque controller pointer, up to five extra arguments, entry name, argument count, and firewall ID. With `CONFIG_STM32_FIREWALL`, APIs include `stm32_firewall_get_firewall()`, `stm32_firewall_grant_access()`, `stm32_firewall_release_access()`, by-ID grant/release helpers, and `stm32_firewall_get_grant_all_access()`. Without the config, functions return `-ENODEV` or no-op.

**Control flow, state, persistence:** Consumers parse DT access-controller references, request grants before touching protected resources, then release. By-ID helpers allow subsystem resources but bypass DT ID validation and must be used carefully.

**Dependencies/integration:** Depends on device tree, platform device types, and controller registration from `stm32_firewall.h`. Integrates with STM32 peripheral/memory drivers.

**Risks and test signals:** Risks are leaked grants, using `U32_MAX`, trusting by-ID grants from unvalidated sources, and failing to handle `-ENODEV` on non-firewall builds. Test signals include config-on/off compile coverage, protected-device probe ordering, grant-all cleanup on partial failure, and negative DT entries.
