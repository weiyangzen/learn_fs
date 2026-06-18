# File Research: sources/cow-pools/bcachefs-tools/include/linux/seqlock.h

Provides a compact `seqcount_t` implementation. Readers spin while the sequence is odd, use read barriers around sampling, and retry when the sequence changes. Writers increment before and after updates with write barriers.

This gives seqlock-style consistency without embedding writer locking; callers must serialize writers separately.
