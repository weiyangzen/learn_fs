# sources/distributed-fs/ceph-client/drivers/soc/fsl/qbman/Makefile

Purpose: Kbuild file for DPAA1 BMan/QMan framework objects and tests.

Important build behavior: `CONFIG_FSL_DPAA` builds `bman_ccsr.o`, `qman_ccsr.o`, `bman_portal.o`, `qman_portal.o`, `bman.o`, `qman.o`, and `dpaa_sys.o`. `CONFIG_FSL_BMAN_TEST` and `CONFIG_FSL_QMAN_TEST` build composite test modules with optional API/stash test objects.

Control flow and integration: the object list ensures low-level hardware setup, portal probing, API layers, and shared helpers are all linked together for DPAA1.

State and persistence: no runtime state.

Risks and test signals: risks are missing cross-object symbols if object lists drift. Test signals are build/link success for DPAA, BMan test module containing `bman_test_api.o` when configured, and QMan test variants matching Kconfig.
