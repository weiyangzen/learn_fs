# File Research: sources/cow-pools/bcachefs-tools/include/linux/export.h

This header stubs module symbol export macros: `EXPORT_SYMBOL`, `EXPORT_SYMBOL_GPL`, `EXPORT_SYMBOL_GPL_FUTURE`, and unused variants all expand to nothing. `THIS_MODULE` is a null `struct module *`, and `KBUILD_MODNAME` is empty.

It is purely build compatibility.
