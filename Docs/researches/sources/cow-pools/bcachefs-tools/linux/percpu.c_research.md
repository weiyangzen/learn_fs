# File Research: sources/cow-pools/bcachefs-tools/linux/percpu.c

Implements userspace percpu storage as per-thread TLS chunks containing a linker-defined static section plus a fixed dynamic arena. It supports thread initialization, callback registration for per-thread init/exit, dynamic percpu allocation/free, dynamic init registration, and constructor/destructor lifecycle.

The allocator is bump plus freelist, grain-aligned, and zeroes dynamic allocations across all live chunks. It aborts on too many threads or callback overflow.
