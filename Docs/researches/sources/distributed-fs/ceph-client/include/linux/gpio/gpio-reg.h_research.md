<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/gpio-reg.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/gpio-reg.h

Purpose: This compatibility header exists only to include the generic MMIO GPIO definitions from `linux/gpio/generic.h`.

Important APIs/types/functions: It declares no independent types or functions. Any user including this file receives the `gpio_generic_chip_config`, `gpio_generic_chip`, flags, initialization function, access wrappers, and lock helper macros from `gpio/generic.h`.

Control flow, state, and persistence: There is no runtime control flow in this file. State behavior is inherited entirely from the generic GPIO implementation.

Dependencies/integration: It provides an include path for older or transitional users that still include `gpio-reg.h` rather than `gpio/generic.h`.

Risks and test signals: The main risk is accidental divergence if future code expects this header to contain definitions of its own. Build tests should ensure legacy include users compile and that include guards do not conflict with `gpio/generic.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/gpio-reg.h -->
