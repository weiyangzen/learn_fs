# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/bcm-pmb.c

Purpose: Broadcom PMB (Power Management Bus) genpd provider for selected BCMBCA devices such as BCM4908 PCIe/USB and BCM63138 SATA.

Important APIs/types/functions: `struct bcm_pmb` stores MMIO base, endianness, spinlock, and onecell data; `bcm_pmb_pd_data` maps names/IDs to PMB bus/device addresses; `bcm_pmb_pm_domain` wraps genpd. Low-level accessors `bcm_pmb_bpcm_read/write()` call `bpcm_rd/wr()` with locking and endian conversion. Power helpers control BPCM zones/devices and SATA-specific registers; genpd callbacks are `bcm_pmb_power_on/off()`.

Control flow: probe maps PMB registers, initializes locking/endian mode, obtains the SoC table, sizes onecell slots by max binding ID, creates a genpd for each table entry initialized as off, and registers the provider. PCIe domains power zone 0 on/off. USB powers on all zones based on `BPCM_CAP_NUM_ZONES` and powers off device via zone 0. SATA powers zone 0 and toggles miscellaneous/SR control, but has no power-off implementation in the switch.

State and persistence: software state is static domain mapping and a spinlock protecting PMB transactions. Hardware state persists in BPCM zone control, power request, reset, memory, and SATA registers. No filesystem persistence.

Dependencies/integration: depends on `reset/bcm63xx_pmb.h` BPCM accessors, DT binding IDs from `bcm-pmb.h`, OF match data, generic PM domains, MMIO, endianness from DT, and built-in platform driver registration.

Risks: BPCM transactions are serialized only within this driver; external PMB users need compatible locking. Endianness mistakes corrupt control words. SATA power-off is unsupported and returns `-EINVAL` through the default path. USB all-zone power-on trusts capability bits. Incorrect bus/device IDs can affect unrelated SoC blocks.

Test signals: DT consumers resolve PCIe/USB/SATA indices, BPCM reads/writes succeed in both endian modes, PCIe zone state changes, USB powers all zones, SATA initializes correctly, unsupported power-off is handled by consumers, and time-sensitive devices enumerate after genpd on.
