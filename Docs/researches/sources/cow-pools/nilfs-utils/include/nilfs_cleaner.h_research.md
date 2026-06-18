# File Research: sources/cow-pools/nilfs-utils/include/nilfs_cleaner.h

Public cleaner controller API. It declares cleaner launch/open/close, ping, PID/device accessors, and command functions for status, run, suspend, resume, tune, reload, wait, stop, and shutdown.

It defines `nilfs_cleaner_args`, valid argument bits, units for numeric arguments, cleaner status values, and helper macros for setting, clearing, and testing each cleaner argument validity bit.
