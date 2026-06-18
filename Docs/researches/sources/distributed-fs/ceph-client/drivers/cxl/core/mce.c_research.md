# sources/distributed-fs/ceph-client/drivers/cxl/core/mce.c

Purpose: registers a CXL-specific machine-check decode notifier that handles cacheline aliasing for CXL memory. When an MCE reports a usable system physical address, the notifier finds the CXL cache alias and offlines that aliased page in addition to the standard MCE handler's action on the original page.

Important APIs, types, and functions: `devm_cxl_register_mce_notifier()` is the exported setup API. It fills a caller-provided `struct notifier_block` with `cxl_handle_mce()` and priority `MCE_PRIO_UC`, registers it with `mce_register_decode_chain()`, and adds a devm unregister action. `cxl_handle_mce()` uses `struct cxl_memdev_state`, `struct cxl_memdev`, endpoint `struct cxl_port`, and `struct mce`.

Control flow: on notification, the handler rejects null or unusable MCE records, missing endpoints, invalid PFNs, and addresses without a CXL SPA cache alias. For a valid alias, it computes the alias PFN, logs an emergency message, calls `memory_failure(pfn, 0)`, and if offlining succeeds marks the PFN no-speculative with `set_mce_nospec()`. It returns `NOTIFY_OK` only when it handled an alias.

State and persistence behavior: the notifier is devm-lifetime state embedded in `struct cxl_memdev_state`. Runtime effects are persistent at memory-management level: `memory_failure()` can offline the aliased page, and `set_mce_nospec()` updates CPU/kernel state to prevent future speculative access. The file does not maintain its own storage.

Dependencies and integration points: depends on x86 MCE decode chains, memory-failure handling, `pfn_valid()`, CXL endpoint alias lookup via `cxl_port_get_spa_cache_alias()`, and memdev state creation in `mbox.c`. The companion header provides a stub when `CONFIG_CXL_MCE` is disabled.

Risks: incorrect alias lookup would offline the wrong page or miss a poisoned alias. The handler assumes `cxlmd->endpoint` remains usable during notification; teardown ordering depends on notifier devm lifetime. This is architecture/config dependent and silently absent when `CONFIG_CXL_MCE` is disabled.

Test signals: build with and without `CONFIG_CXL_MCE`, inject or simulate MCE records with unusable addresses, non-CXL addresses, invalid PFNs, and valid aliased SPAs, verify `memory_failure()` and `set_mce_nospec()` calls, and exercise notifier unregister during memdev teardown.
