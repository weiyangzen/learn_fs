# sources/compression/zstd/contrib/linux-kernel/test/include/linux/module.h

Purpose: user-space shim for Linux module export/license macros used by generated zstd module wrappers.

Important behavior: `EXPORT_SYMBOL(symbol)` and `EXPORT_SYMBOL_GPL(symbol)` create a pointer variable `__symbol` referencing the exported symbol, forcing the symbol to be type-checked/retained. `MODULE_LICENSE` and `MODULE_DESCRIPTION` are no-ops.

State, dependencies, and integration: export macros create global pointer variables in test builds. This helps validate wrapper symbols without requiring kernel module infrastructure.

Risks and test signals: it does not model real kernel export visibility or license enforcement. Compile/link success in the linux-kernel tests is the main signal.
