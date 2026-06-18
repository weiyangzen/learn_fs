<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/Makefile -->
# sources/distributed-fs/ceph-client/tools/hv/Makefile

Purpose: Builds and installs Hyper-V guest userspace daemons and helper scripts.

Important APIs/types/functions: Targets build `hv_kvp_daemon` and `hv_vss_daemon`, plus `hv_fcopy_uio_daemon` on x86/x86_64. `ALL_SCRIPTS` includes DHCP, DNS, and ifconfig helper scripts. The Makefile uses `tools/build/Makefile.include`, sets `-D_GNU_SOURCE`, includes `$(OUTPUT)include`, and suppresses packed-member address warnings.

Control flow: It computes `srctree` when unset, disables built-in rules, exports build variables, invokes per-daemon build recipes, links final binaries, and installs binaries to `sbindir`, scripts to `libexecdir)/hypervkvpd` without `.sh`, and creates `sharedstatedir`.

State and persistence: Build artifacts are under `$(OUTPUT)`. Install persists system binaries/scripts under `/usr/sbin`, `/usr/libexec/hypervkvpd`, and `/var/lib` by default.

Dependencies/integration: Depends on kernel tools build infrastructure, Hyper-V UAPI headers, compiler/linker, and `lsvmbus`. It integrates with Hyper-V guest services and distro packaging.

Risks/tests: Risks include architecture gating for fcopy, install paths not matching distro policy, and script renaming expectations from daemons. Test signals are x86 and non-x86 builds, `make clean`, staged install with `DESTDIR`, and service packaging checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/Makefile -->
