# sources/distributed-fs/ceph-client/drivers/leds/leds-ip30.c

Purpose: SGI Octane IP30 LED driver exposing system and fault LEDs mapped as platform MMIO resources.

Important APIs/types/functions: `struct ip30_led` holds classdev and `__iomem` register pointer. `ip30led_set()` writes the brightness value directly to the mapped register. `ip30led_create()` allocates one LED, maps resource index 0 or 1, assigns fixed name, initializes brightness from `readl()`, and registers the classdev.

Control flow: probe creates the system LED then fault LED. Resource index 0 is named `white:power`; index 1 is `red:fault`. Brightness max is 1 and writes are direct `writel(value, reg)` operations.

State and persistence: per-LED state is the mapped register. Initial LED core brightness reflects hardware at probe. Register values persist in platform hardware until overwritten.

Dependencies/integration: platform resources, `devm_platform_ioremap_resource()`, MMIO accessors, platform device `"ip30-leds"`, LED class.

Risks: resource order is ABI-critical. Direct MMIO writes have no masking, so each resource must be a dedicated LED register. Static names are not firmware-configurable. There is no shutdown callback.

Test signals: validate both resources map, initial brightness mirrors `readl()`, writes 0/1 drive expected LEDs, invalid resource index path is unreachable except direct helper misuse, and devm cleanup.
