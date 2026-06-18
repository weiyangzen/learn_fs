# sources/distributed-fs/ceph-client/drivers/bcma/bcma_private.h

Purpose: this private header defines BCMA-internal logging helpers, cross-file function prototypes, and conditional inline fallbacks for optional BCMA components.

Important APIs, types, and functions: logging macros `bcma_err`, `bcma_warn`, `bcma_info`, and `bcma_debug` prefix messages with bus number. It declares main bus lifecycle, scanning, SPROM, ChipCommon, ChipCommon B, PMU, flash, host PCI/SoC, PCI/PCIe2, watchdog, PCI host mode, MIPS, GMAC common, and GPIO functions. Conditional sections provide no-op or warning fallbacks when features such as `CONFIG_BCMA_PFLASH`, `CONFIG_BCMA_SFLASH`, `CONFIG_BCMA_NFLASH`, `CONFIG_BCMA_DRIVER_PCI`, `CONFIG_BCMA_DRIVER_PCI_HOSTMODE`, `CONFIG_BCMA_DRIVER_MIPS`, `CONFIG_BCMA_DRIVER_GMAC_CMN`, or `CONFIG_BCMA_DRIVER_GPIO` are disabled.

Control flow: compile-time configuration selects either external prototypes or inline fallback implementations. Runtime call sites can invoke common helpers without duplicating preprocessor conditionals.

State and persistence: no state is stored in the header. It exposes stateful structures defined in public BCMA headers, such as `struct bcma_bus`, `struct bcma_device`, and driver-specific structs.

Dependencies and integration points: it includes `linux/bcma/bcma.h` and `linux/delay.h`, and is included by the BCMA driver implementation files. It is the key boundary between optional object composition and unconditional call sites in the BCMA core.

Risks: fallback behavior must match call-site expectations. Some disabled-feature fallbacks log errors but return success for unsupported flash init, while GPIO init returns `-ENOTSUPP`; inconsistent conventions can surprise callers. Prototypes must stay synchronized with source definitions and Kconfig/Makefile conditions.

Test signals: all relevant Kconfig combinations should compile. Runtime signals include clear error logs when unsupported optional flash paths are detected and no unresolved symbols when features are disabled.
