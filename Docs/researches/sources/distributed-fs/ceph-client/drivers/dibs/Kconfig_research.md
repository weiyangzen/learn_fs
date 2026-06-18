# sources/distributed-fs/ceph-client/drivers/dibs/Kconfig

Purpose: defines the build-time feature switches for Direct Internal Buffer Sharing. `DIBS` enables the core abstraction layer used by DIBS devices and clients such as SMC, while `DIBS_LO` adds a software loopback device for same-OS testing without hardware fabric support.

Important APIs/types/functions: this is Kconfig-only. `config DIBS` is a tristate with module name `dibs`; `config DIBS_LO` is a bool depending on `DIBS`, so loopback code is compiled into the DIBS object only when the core is enabled.

Control flow: no runtime control flow. The selections drive `drivers/dibs/Makefile`, where `dibs_main.o` is always part of the DIBS object and `dibs_loopback.o` is added when `CONFIG_DIBS_LO` is enabled.

State and persistence behavior: no runtime state. Configuration state persists in the kernel `.config` and determines whether the DIBS class and optional loopback provider are present.

Dependencies and integration points: integrates with Linux Kconfig and the DIBS client-facing headers in `include/linux/dibs.h`. `DIBS_LO` is a test/convenience provider, not a hardware transport.

Risks and test signals: enabling `DIBS_LO` creates an in-kernel emulated sharing device, so test kernels may expose behavior not representative of hardware. Build signals are `CONFIG_DIBS=m/y` producing the DIBS class, and `CONFIG_DIBS_LO=y` adding the `lo` DIBS device during DIBS init.
