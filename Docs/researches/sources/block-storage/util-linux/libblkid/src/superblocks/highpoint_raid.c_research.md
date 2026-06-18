# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/highpoint_raid.c

HighPoint RAID detector for hpt45x and hpt37x formats. The hpt45x probe is computed-location based: it checks regular files or whole disks only, reads metadata 11 sectors from the end, and accepts the OK or BAD little-endian magic.

The hpt37x detector uses static magic entries at the documented offset and a probe that only enforces whole-disk/regular-file scope. Both idinfos report RAID usage. hpt45x records magic for wiping/reporting; hpt37x relies on the generic magic table.
