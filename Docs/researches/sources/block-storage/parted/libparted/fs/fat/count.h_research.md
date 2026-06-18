# File Research: sources/block-storage/parted/libparted/fs/fat/count.h

FAT cluster-usage interface header. It defines `FatClusterFlag` values for free, file, directory, and bad clusters, plus a packed `FatClusterInfo` bitfield storing 6 bits of usage units and a 2-bit flag.

It declares functions to collect cluster info for a filesystem, query cluster flags and usage, map fragment flags, and test whether a fragment is active. These functions are implemented outside the listed files but are referenced by FAT resize/analysis code through `fat.h`.

The bitfield makes per-cluster metadata compact, with one usage unit representing `cluster_size / 64`.
