# sources/distributed-fs/ceph-client/drivers/ipack/devices/Makefile

Purpose: Selects the IP-OCTAL object in the IPACK devices directory.

Important APIs/types/functions: `obj-$(CONFIG_SERIAL_IPOCTAL) += ipoctal.o`.

Control flow: Kbuild emits the IP-OCTAL driver only when `SERIAL_IPOCTAL` is enabled.

State and persistence: No runtime state; build selection only.

Dependencies/integration: Hooks `ipoctal.c` into the kernel/module build under the TTY/IPACK config gate.

Risks and test signals: Verify modular and built-in builds, especially with carrier drivers modular, so the IPACK driver registration symbols are available.
