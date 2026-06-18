# sources/distributed-fs/coda/coda-src/vol/vutil.cc

Purpose: volume utility helper implementations for creating and copying volume metadata.

Important APIs: `VCreateVolume` creates a new RVM volume record, optionally allocates a recoverable resolution log, writes a header and disk info through recovery APIs, and attaches it secretly. `AssignVolumeName` normalizes names and optional suffixes. `CopyVolumeHeader` copies administrative disk data from one volume to another while preserving immutable ids/group/copy date and resetting destroy/log/resolution fields. `ClearVolumeStats` zeros daily/weekly usage counters.

Control flow/state: new volumes are created with `destroyMe = DESTROY_ME`, meaning the file server should not attach them until utility code finishes and clears the flag. `VCreateVolume` locks the partition, allocates `VolumeDiskData`, calls `NewVolHeader`, then `NewVolDiskInfo`, and returns an attached `Volume *` in `V_SECRETLY` mode.

Dependencies/integration: depends on partitions, vice inode support, `volume.h`, `recov.h`, recoverable volume logs, and `AllowResolution`. Risks include `sprintf(vol.partition, partition, strlen(partition)+1)` misuse where `strncpy`/`snprintf` would be expected, leaving destroy flag uncleared by caller, partial creation cleanup after `NewVolDiskInfo` failure, and transaction ownership by caller. Test signals: create RW/RO/backup/replicated volumes, long partition names, optional RVM logs, interrupted restore cleanup, header copy preserving immutable ids, and name suffix stripping.
