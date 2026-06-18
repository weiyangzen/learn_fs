# File Research: sources/cow-pools/bcachefs-tools/include/linux/console.h

This is a minimal console-lock shim. `console_lock()` and `console_unlock()` are no-ops, while `console_trylock()` always returns `true`.

It exists only to satisfy kernel-code call sites in user space; it provides no serialization.
