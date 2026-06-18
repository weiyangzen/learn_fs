# sources/distributed-fs/ceph-client/drivers/nvmem/u-boot-env.c

Purpose: MTD-backed NVMEM provider for U-Boot environment storage, coupled with the U-Boot environment layout parser.

Important APIs/types/functions: `struct u_boot_env` stores device, registered NVMEM device, format, and `struct mtd_info`. `u_boot_env_read()` wraps `mtd_read()` and tolerates bitflip return codes. Probe gets the MTD device for the OF node, registers an NVMEM provider sized to the MTD, then calls `u_boot_env_parse()`.

Control flow: probe allocates state, stores format from OF match data, resolves the MTD partition/device node, registers a read-only NVMEM provider with custom read callback, and immediately parses environment variables into NVMEM cells. Runtime reads are direct MTD reads with short-read detection.

State/persistence: environment data persists in MTD flash. Driver state references the MTD and NVMEM device; variable cells are registered by the layout parser.

Dependencies/integration: OF compatibles mirror layout formats; depends on MTD, NVMEM provider, and `layouts/u-boot-env.h`.

Risks: the MTD device acquired by `of_get_mtd_device_by_node()` is not explicitly released in this file, so lifetime management should be checked against devm/platform expectations. Registering NVMEM before parsing means parse failure returns probe failure after provider registration is devm-managed. Bitflips are accepted but still may indicate marginal flash.

Test signals: MTD lookup deferral/failure, bitflip-tolerant reads, short reads, parser CRC failures propagating from probe, and per-format compatible selection.
