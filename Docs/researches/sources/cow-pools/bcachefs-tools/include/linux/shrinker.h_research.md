# File Research: sources/cow-pools/bcachefs-tools/include/linux/shrinker.h

Declares userspace shrinker support: `shrink_control`, `struct shrinker`, allocation/free/register functions, `run_shrinkers()`, and initialization. Shrinkers are used by allocation wrappers to retry after reclaim attempts.

Implementation is in `linux/shrinker.c`, and the API preserves kernel count/scan callback shape.
