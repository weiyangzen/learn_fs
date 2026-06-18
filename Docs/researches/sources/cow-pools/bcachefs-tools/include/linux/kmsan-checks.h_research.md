# File Research: sources/cow-pools/bcachefs-tools/include/linux/kmsan-checks.h

This header mirrors Kernel Memory Sanitizer annotation hooks. With `CONFIG_KMSAN`, it declares poison, unpoison, check, copy-to-user, and memmove metadata functions.

Without KMSAN, all functions are empty inline stubs. It preserves kernel call sites while making sanitizer support optional.
