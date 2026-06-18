# sources/distributed-fs/ceph-client/drivers/net/dsa/b53/b53_mmap.c

Purpose: B53 MMIO/platform transport for memory-mapped integrated Broadcom switches and BCM63xx PHY power control.

Important APIs/types/functions: `struct b53_mmap_priv` stores MMIO base, optional syscon regmap, PHY metadata, and enabled PHY mask. `b53_mmap_read*()`/`write*()` perform direct little/big-endian MMIO. `b53_mmap_probe_of()` builds platform data from DT; PHY enable/disable callbacks toggle EPHY/GPHY low-power bits.

Control flow: probe obtains platform or OF data, maps resources, reads enabled ports from `ports`, selects SoC PHY info when `brcm,gpio-ctrl` exists, allocates B53 with MMIO ops, attaches platform data, and registers the switch. Port enable/disable can power PHY blocks.

State and persistence behavior: runtime-only MMIO/regmap pointers and `phys_enabled` mask; hardware registers and PHY power bits are reprogrammed as ports change.

Dependencies and integration points: platform devices, OF, MMIO, syscon/regmap, B53 platform data, common B53 core.

Risks: OF requires `ports`; endian binding mistakes corrupt access; unaligned access returns `-EINVAL`; missing gpio-ctrl silently disables PHY power management; PHY callback errors are not returned to common code.

Test signals: platform-data and OF probe, endian and width tests including 48-bit paths, BCM6318/6368/63268 PHY power sequencing, and port enable/disable cycles.
