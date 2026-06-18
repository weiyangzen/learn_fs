# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned/generic.h

Provides generic typed `__get_unaligned_le/be` and `__put_unaligned_le/be` macros. They dispatch by object size for 1, 2, 4, or 8 bytes and call `__bad_unaligned_access_size()` for unsupported sizes.
