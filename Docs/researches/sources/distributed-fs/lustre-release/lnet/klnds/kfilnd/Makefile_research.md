<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/Makefile

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/Makefile_research.md`.

Purpose: declares the kfabric LND kernel module and its compilation units.

Important APIs/types/functions: kbuild emits `kkfilnd.o` from `kfilnd.o`, `kfilnd_modparams.o`, `kfilnd_tn.o`, `kfilnd_ep.o`, `kfilnd_dev.o`, `kfilnd_dom.o`, `kfilnd_peer.o`, `kfilnd_cq.o`, and `kfilnd_debugfs.o`. It adds `$(KFICPPFLAGS)` to `ccflags-y` and enables `GCOV_PROFILE` when requested.

Control flow: kbuild compiles each listed source and links them into the module. The object order places the LNet entry point and module parameters before transaction, endpoint, device, domain, peer, completion, and debugfs helpers.

State and persistence behavior: build-only file; no runtime state.

Dependencies and integration: integrates with Lustre/LNet kbuild and kfabric provider headers supplied through `KFICPPFLAGS`.

Risks: any new source file must be added here or it will be omitted. Missing `KFICPPFLAGS` causes kfabric include failures. GCOV flag affects instrumentation across the whole module.

Test signals: build `kkfilnd.o` with and without kfabric provider flags, check module symbols resolve, enable `CONFIG_GCOV_PROFILE_LNET`, and verify each object appears in the final module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/kfilnd/Makefile -->
