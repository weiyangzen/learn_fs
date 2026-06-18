# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned/be_struct.h

Defines big-endian unaligned helpers using packed CPU-endian struct loads/stores from `packed_struct.h`. This only makes sense when CPU byte order matches the desired big-endian interpretation through selected include configuration.
