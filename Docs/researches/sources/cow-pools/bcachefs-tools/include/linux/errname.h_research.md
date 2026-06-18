# File Research: sources/cow-pools/bcachefs-tools/include/linux/errname.h

This small header maps an errno value to a libc error string. `errname(int err)` returns `strerror(abs(err))`, so both positive and negative errno-style values are accepted.
