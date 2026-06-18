
# sources/distributed-fs/ceph-client/include/linux/nsc_gpio.h

Purpose: declares the common file-operation helper interface for National Semiconductor GPIO controllers used by Geode and PC-8736x style chips.

Important APIs/types/functions: `struct nsc_gpio_ops` supplies controller-specific methods for configuration, dumping state, get/set/change/current pin state, module ownership, and a device pointer for debug output. `nsc_gpio_read()`, `nsc_gpio_write()`, and `nsc_gpio_dump()` are shared helpers used by chip drivers.

Control flow: a chip driver fills `nsc_gpio_ops` with low-level accessors and exposes GPIOs through common file operations. User reads/writes go through `nsc_gpio_read()` / `nsc_gpio_write()`, which call the ops for the selected minor/pin. Dump support routes diagnostic output through the controller implementation.

State and persistence: this header owns no state. Runtime state is hardware register state plus driver private data behind the callback table. GPIO pin configuration persists only as hardware/platform state.

Dependencies and integration points: relies on `struct file`, user pointers, `struct module`, `struct device`, and U32 integer types from includers. It integrates legacy character-device style GPIO access with NSC/AMD/Winbond platform drivers.

Risks and test signals: risks include missing module ownership, invalid minor-to-pin mapping, user buffer handling bugs in shared file operations, and divergent semantics between Geode and PC-8736x callbacks. Test signals include read/write/change paths for each chip family, invalid minor tests, module unload while fds are open, and register dump validation on known hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/nsc_gpio.h -->
