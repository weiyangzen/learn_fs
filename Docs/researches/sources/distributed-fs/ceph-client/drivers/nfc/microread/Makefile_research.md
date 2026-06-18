# sources/distributed-fs/ceph-client/drivers/nfc/microread/Makefile

Purpose: Maps Microread Kconfig symbols to core and transport module objects.

Important APIs, types, and functions: `microread_i2c-objs = i2c.o`, `microread_mei-objs = mei.o`, and `obj-$(CONFIG_NFC_MICROREAD) += microread.o` plus transport `obj-*` lines define module composition.

Control flow: Build-time only. Kbuild emits the core and optional transport modules according to `.config`.

State and persistence behavior: No runtime state; module names are persistent build/user-visible outputs.

Dependencies and integration points: Aligns with `microread.c`, `i2c.c`, `mei.c`, and symbols in `microread/Kconfig`.

Risks: Object/module naming must match documentation and autoloading expectations. Transports depend on exported `microread_probe()`/`microread_remove()` from the core.

Test signals: Build core with each transport, run modpost for exported symbol resolution, and inspect generated `microread_i2c.ko` and `microread_mei.ko`.
