# sources/distributed-fs/ceph-client/tools/testing/selftests/Makefile

Purpose: top-level kselftest makefile enumerating selftest target directories and orchestrating build, run, install, hotplug, packaging, and clean operations.

Important APIs/types/functions: `TARGETS` list, `TARGETS_HOTPLUG`, `SKIP_TARGETS`, `FORCE_TARGETS`, `KBUILD_OUTPUT`/`O` handling, `BUILD`, `KHDR_INCLUDES`, default `all`, `run_tests`, `hotplug`, `run_hotplug`, `install`, `gen_tar`, and `clean` targets.

Control flow: default `all` iterates over targets and optional install dependencies, invoking sub-makes with per-target `OUTPUT`. `run_tests` builds then invokes each target's `run_tests`. `install` copies kselftest runner files, installs each target under `KSFT_INSTALL_PATH`, emits `kselftest-list.txt`, and writes a git-described `VERSION` if available. `gen_tar` packages the install tree.

State and persistence: creates build output trees, install directories, test lists, archives, and optional VERSION. Honors out-of-tree build locations.

Dependencies/integration: central integration point for all `tools/testing/selftests` subdirectories, `scripts/subarch.include`, and `lib.mk` conventions.

Risks and test signals: because `FORCE_TARGETS` defaults empty, the aggregate build can succeed if at least one target builds. `SKIP_TARGETS` excludes BPF and sched_ext by default. Target list ordering and missing target directories affect emitted test inventory.
