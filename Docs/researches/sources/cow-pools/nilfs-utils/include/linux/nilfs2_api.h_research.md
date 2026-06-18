# File Research: sources/cow-pools/nilfs-utils/include/linux/nilfs2_api.h

Bundled NILFS2 user-space API header. It defines ioctl-visible structures for checkpoint info, segment usage info and updates, checkpoint modes, vector arguments, checkpoint ranges, checkpoint and segment stats, virtual block info, virtual descriptors, and block descriptors.

It also defines flag helper inline functions for checkpoint, segment usage, and segment usage updates. Ioctl numbers cover changing checkpoint mode, deleting checkpoints, reading checkpoint and segment usage data, obtaining vinfo/bdesc data, cleaning segments, syncing, resizing, setting allocation range, and updating segment usage info.
