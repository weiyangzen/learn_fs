# sources/distributed-fs/ceph-client/drivers/reset/spacemit/Makefile

Purpose: Kbuild mapping for SpacemiT reset modules.

Important APIs/types/functions: builds `reset-spacemit-common.o` for `CONFIG_RESET_SPACEMIT_COMMON`, `reset-spacemit-k1.o` for `CONFIG_RESET_SPACEMIT_K1`, and `reset-spacemit-k3.o` for `CONFIG_RESET_SPACEMIT_K3`.

Control flow: Kbuild selects object files according to Kconfig; runtime behavior lives in the C files.

State and persistence: no runtime state. Build artifacts and module composition are determined by `.config`.

Dependencies and integration: common object exports `spacemit_reset_probe` in namespace `RESET_SPACEMIT`, which K1/K3 import.

Risks and test signals: missing common object or namespace import causes link/module-load failures. Test K1-only, K3-only, both, module, and built-in builds.
