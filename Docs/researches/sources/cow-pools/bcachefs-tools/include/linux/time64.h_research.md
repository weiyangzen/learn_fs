# File Research: sources/cow-pools/bcachefs-tools/include/linux/time64.h

Maps `timespec64` to libc `timespec`, defines nanosecond/microsecond/millisecond constants, and implements conversions/truncation/normalization helpers.

It provides `time64_t`, `ns_to_timespec64`, `timespec64_to_ns`, and `timespec64_trunc` compatibility aliases.
