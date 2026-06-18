# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/netware.c

NetWare NSS detector. It matches `SPB5` at 4 KiB, reads the NSS superblock, emits the pool UUID from `SBH_PoolID`, and formats the media version as major.two-digit-minor.

The idinfo reports filesystem usage under name `nss`. The probe does not validate the many other NSS structure fields or checksum; identity is based on magic and readable superblock fields.
