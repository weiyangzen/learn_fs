# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/extensions/sample/main.c

## Purpose
Sample NetIDMgr module entry point for an AFS extension DLL.

## Important APIs, Types, And Functions
Declares module/resource handles, facility string, supported locales, `init_module()`, `exit_module()`, and `DllMain()`. `init_module()` sets locale info, obtains the selected resource module, fills a `kmm_plugin_reg`, and calls `kmm_provide_plugin()`.

## Control Flow
On module initialization, it registers US English resources, loads plugin description/icon, declares dependency on `AfsCred`, and provides one miscellaneous plugin whose message processor is `plugin_msg_proc`. `exit_module()` is a placeholder. `DllMain()` records the DLL instance on process attach.

## State And Persistence
Runtime globals hold module and resource handles. No persistent settings are written.

## Dependencies And Integration Points
Depends on KMM module lifecycle, sample resource DLL naming from the Makefile, `credprov.h`, and plugin message handling in `plugin.c`.

## Risks
Failure to load resources aborts module initialization. The sample relies on the core AFS plugin dependency being named `AfsCred`. Icons loaded for registration need ownership behavior consistent with KMM expectations.

## Test Signals
Load sample module in NetIDMgr with core AFS plugin present, verify locale selection, plugin registration, dependency handling, icon/description loading, and unload.
