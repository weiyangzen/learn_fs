# File Research: sources/cow-pools/bcachefs-tools/include/linux/prefetch.h

This header stubs `prefetch()` and `prefetchw()`. Each macro evaluates its pointer argument into an unused local to preserve side-effect behavior, but performs no CPU prefetch instruction.
