# sources/distributed-fs/ceph-client/drivers/dca/Kconfig

Purpose: minimal Kconfig symbol for the Intel Direct Cache Access service module.

Important APIs/types/functions: `config DCA` as a tristate.

Control flow and state: this symbol controls whether the DCA core and sysfs service are built. It does not expose prompt text or dependencies in this snippet, so selection is expected from provider drivers or architecture/platform config.

Dependencies and integration: integrates with kbuild through `drivers/dca/Makefile` and with clients/providers through `<linux/dca.h>` exported symbols.

Risks and test signals: because it is dependency-light, invalid selections can surface at provider build/runtime rather than config time. Test provider configs that select DCA, modular vs built-in builds, and absence of DCA when clients use stubs.
