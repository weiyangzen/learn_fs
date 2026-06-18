# File Research: sources/cow-pools/bcachefs-tools/include/linux/percpu-rwsem.h

This header maps `struct percpu_rw_semaphore` to a single `pthread_mutex_t`. Read and write lock paths both lock the same mutex; try-read uses `pthread_mutex_trylock()`.

Initialization and free are simple pthread/no-op operations, and assertion is a no-op. It defines cleanup guards for `percpu_read`, conditional `percpu_read_try`, and `percpu_write`.
