# File Research: sources/cow-pools/bcachefs-tools/include/linux/kmemleak.h

This header mirrors the kernel kmemleak API. Under `CONFIG_DEBUG_KMEMLEAK`, it declares the kmemleak tracking functions and small recursive wrappers that respect `SLAB_NOLEAKTRACE`.

Without that config, all kmemleak functions become empty inline stubs. This lets allocation code retain instrumentation calls without affecting normal bcachefs-tools builds.
