# File Research: sources/cow-pools/nilfs-utils/include/cleaner_exec.h

Declares legacy cleaner process control routines: launch, ping, and shutdown of `nilfs_cleanerd`. It defines the daemon name and mount option name `gcpid`.

It also exposes logger/printf/flush function pointers, allowing callers to redirect cleaner process control output.
