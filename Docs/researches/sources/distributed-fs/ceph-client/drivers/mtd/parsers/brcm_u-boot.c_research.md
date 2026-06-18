# sources/distributed-fs/ceph-client/drivers/mtd/parsers/brcm_u-boot.c

Purpose: parser for Broadcom U-Boot environment partitions. It discovers up to two environment blobs by scanning for a small `uEnv` header.

Important APIs/types/functions: `brcm_u_boot_parse()` is the parser entry for compatible `brcm,u-boot`. `struct brcm_u_boot_header` stores little-endian magic and length. `names[]` assigns `u-boot-env` and `u-boot-env-backup`.

Control flow: the parser allocates a two-entry partition array, scans from offset 0 to the smaller of flash size and 2 MiB in 0x1000-byte steps, reads the header at each step, tolerates corrected bitflips, and compares the magic to `BRCM_U_BOOT_MAGIC`. For each hit it sets name, offset, and size as `sizeof(header) + length`, then stops after two hits.

State and persistence: all persistent data is the on-flash environment header and payload. Runtime state is the partition array; there is no cleanup callback because names are static. The parser does not mutate flash.

Dependencies and integration: integrates with MTD parser core and OF matching. Risks include trusting unbounded length, fixed scan window/step, and returning an allocated empty partition array when no headers are found. Test signals include primary and backup env images, malformed lengths, flash smaller than 2 MiB, read failures versus bitflips, and max-two behavior.
