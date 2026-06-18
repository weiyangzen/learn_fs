# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/vmfs.c

## Scope

Implements VMware VMFS filesystem and VMFS volume-member probing.

## Behavior

- VMFS filesystem probe exports byte-reordered UUID, label, and version.
- VMFS volume member probe exports `UUID_SUB`, version, and optionally reads an LVM UUID from a fixed offset inside the volume-info area.
- Registers separate idinfos for `VMFS` filesystem usage and `VMFS_volume_member` RAID usage.

## Dependencies And Risks

- UUID formatting uses VMFS-specific byte ordering.
- Optional LVM UUID extraction silently skips if the secondary buffer cannot be read.
