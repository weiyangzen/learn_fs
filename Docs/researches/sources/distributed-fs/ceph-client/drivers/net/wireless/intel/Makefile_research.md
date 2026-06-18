# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/Makefile

Purpose: Routes Intel wireless build objects to the appropriate driver subdirectories.

Important APIs/build targets: Adds `ipw2x00/` for `CONFIG_IPW2100` or `CONFIG_IPW2200`, `iwlegacy/` for `CONFIG_IWLEGACY`, and `iwlwifi/` for `CONFIG_IWLWIFI` or `CONFIG_IWLMEI`.

Control flow and state: Kbuild object selection only. Multiple IPW configs can point to the same subdirectory, allowing that subdirectory Makefile to build selected objects.

Dependencies and integration: Depends on Kbuild config symbols from Intel wireless Kconfigs. Risks include subdirectory duplication if both IPW configs are enabled, missing object traversal for new config symbols, and link failures if Kconfig/Makefile diverge. Test signals include allyesconfig/allmodconfig builds, single-driver builds, and dependency-tree changes in Intel wireless configs.
