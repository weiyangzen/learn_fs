# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/Makefile

Purpose: Build orchestration for the Atheros/Qualcomm wireless subtree. It descends into selected driver directories and assembles the common `ath.o` support object.

Important APIs/types/functions: `obj-$(CONFIG_ATH5K)`, `obj-$(CONFIG_AR5523)`, `obj-$(CONFIG_ATH10K)`, and similar lines map configuration symbols to subdirectories. `obj-$(CONFIG_ATH_COMMON) += ath.o` builds the shared common module from `main.o`, `regd.o`, `hw.o`, `key.o`, `dfs_pattern_detector.o`, and `dfs_pri_detector.o`. Conditional fragments add `debug.o` and `trace.o`; `CFLAGS_trace.o := -I$(src)` supports local trace header inclusion.

Control flow: Kbuild evaluates selected config symbols and builds only enabled subtrees. Drivers selecting `ATH_COMMON` cause `ath.o` to be linked. Optional debug and trace code are compiled only when their Kconfig booleans are true.

State/persistence: Produces build artifacts under the kernel build tree. No runtime state is held here.

Dependencies/integration: Ties Kconfig selections to object layout. Common regulatory, key, DFS, debug, and tracing helpers are shared by multiple Atheros drivers through `ATH_COMMON`.

Risks: Mismatches between Kconfig symbols and Makefile object lists can silently omit a driver or common helper. Trace builds require include path correctness because trace headers often rely on local relative inclusion.

Test signals: Targeted `make M=drivers/net/wireless/ath` builds under different configs confirm object selection. `modpost` failures catch missing objects or unresolved references from selected drivers.
