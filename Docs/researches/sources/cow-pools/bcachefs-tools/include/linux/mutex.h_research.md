# File Research: sources/cow-pools/bcachefs-tools/include/linux/mutex.h

This header implements kernel mutex API calls using `pthread_mutex_t`. `struct mutex` wraps a pthread mutex, `DEFINE_MUTEX()` uses `PTHREAD_MUTEX_INITIALIZER`, and lock/unlock/trylock/init map to pthread calls.

It defines a cleanup guard named `mutex`, enabling `guard(mutex)` and scoped guard patterns from `cleanup.h`.
