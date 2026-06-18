# sources/distributed-fs/ceph-client/drivers/dibs/Makefile

Purpose: builds the DIBS class object and conditionally includes the loopback implementation.

Important APIs/types/functions: declares `dibs-y += dibs_main.o`, `obj-$(CONFIG_DIBS) += dibs.o`, and `dibs-$(CONFIG_DIBS_LO) += dibs_loopback.o`.

Control flow: no runtime flow. Kbuild links `dibs_main.o` into `dibs.o` whenever `CONFIG_DIBS` is enabled, and links `dibs_loopback.o` into the same module/built-in object only when `CONFIG_DIBS_LO` is enabled.

State and persistence behavior: none beyond build artifacts.

Dependencies and integration points: follows the Kconfig dependency from `drivers/dibs/Kconfig`; the resulting object exports DIBS device/client APIs for other kernel users.

Risks and test signals: a mismatch between Kconfig and Makefile would either omit loopback symbols or build unused code. Test signal is successful allmodconfig/module builds in both loopback-enabled and disabled combinations.
