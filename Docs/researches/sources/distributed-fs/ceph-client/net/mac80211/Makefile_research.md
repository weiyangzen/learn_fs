# sources/distributed-fs/ceph-client/net/mac80211/Makefile

Purpose: this kbuild file defines the `mac80211.o` composite object for `CONFIG_MAC80211` and selects the translation units that make up the Linux mac80211 subsystem copy in this source tree. It is the integration point that pulls together core interface management, station state, key handling, WPA helpers, scan/offchannel logic, HT/VHT/HE/EHT/UHR handling, aggregation, airtime accounting, cfg80211 hooks, mesh, debugfs, minstrel rate control, tests, and WBRF support.

Important build APIs and targets: `obj-$(CONFIG_MAC80211) += mac80211.o` registers the module/object. `mac80211-y := ...` lists mandatory objects including `aead_api.o`, `agg-tx.o`, `agg-rx.o`, `aes_cmac.o`, `aes_gmac.o`, `cfg.o`, and `airtime.o`, which are the implementation files in this work item. Conditional fragments add `led.o`, debugfs files, mesh files, `pm.o`, and minstrel rate-control objects. `obj-y += tests/` always descends into the tests directory when this makefile is included. `CFLAGS_trace.o := -I$(src)` gives trace compilation local include visibility. `ccflags-y += -DDEBUG` globally compiles this subtree with `DEBUG` defined.

Control flow and dependencies: there is no runtime control flow, but the object ordering and conditional inclusion affect available symbols. `cfg.o` contributes `mac80211_config_ops`, later used by `main.c` when creating the wiphy. `aead_api.o`, `aes_cmac.o`, and `aes_gmac.o` satisfy crypto calls from `key.c`, `wpa.c`, `rx.c`, and `tx.c`. `agg-tx.o` and `agg-rx.o` expose exported BA session helpers for drivers and internal action-frame processing. `airtime.o` exposes airtime calculators used by TX scheduling and status accounting.

State and persistence behavior: build state is derived from Kconfig symbols such as `CONFIG_MAC80211_MESH`, `CONFIG_MAC80211_DEBUGFS`, `CONFIG_MAC80211_RC_MINSTREL`, and `CONFIG_PM`; no persistent runtime state is managed here. The most notable cross-cutting build-time state is `-DDEBUG`, which can change logging, warnings, and debug-only paths throughout mac80211.

Integration points: this file integrates with the kernel kbuild system, Kconfig feature switches, and subtree tests. It also establishes that the crypto helpers and aggregation files are part of the same object, enabling internal non-exported symbol references across mac80211.

Risks: omitting a file here causes unresolved symbols or silent feature loss. Adding `ccflags-y += -DDEBUG` across the whole subsystem can increase logging volume and change code guarded by debug macros. Conditional feature objects must match Kconfig declarations and any external symbol users.

Test signals: kbuild compilation for all relevant Kconfig combinations is the main signal. Useful coverage includes `CONFIG_MAC80211`, mesh on/off, debugfs on/off, PM on/off, and minstrel on/off. Link-time unresolved-symbol failures would quickly expose object list regressions.
