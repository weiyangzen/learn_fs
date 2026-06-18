# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/drbdproxy_datalog.c

DRBD Proxy datalog detector. It matches `DRBDdlh*` at the start of the device, reads a small log header, emits the embedded UUID, and formats the little-endian version as `v<version>`.

The idinfo reports `drbdproxy_datalog` with filesystem usage and a 16 KiB minimum size. The probe is intentionally lightweight and does not validate flags or log layout beyond the magic and readable header.
