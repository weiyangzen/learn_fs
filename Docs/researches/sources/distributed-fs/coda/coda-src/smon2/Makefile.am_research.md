# sources/distributed-fs/coda/coda-src/smon2/Makefile.am

Purpose: Automake build rules for server monitoring and sizing utilities.

Important declarations: under `BUILD_SERVER`, builds `getvolinfo`, `rpc2ping`, `rvmsizer`, and `smon2` as `bin_PROGRAMS`. `AM_CPPFLAGS` adds RPC2 and Coda base/vicedep include paths. Default `LDADD` links vicedep, base, and RPC2 libraries; `rvmsizer_LDADD` overrides to only link base because it scans local filesystems and does not use RPC2.

Control flow/state: build-time only; no runtime state. Integrates with top-level server conditional and generated build directories.

Dependencies, risks, tests: depends on generated `libvenusdep`, `libbase`, and RPC2 libraries. Risks include installing admin/monitoring tools in `bin` rather than `sbin` if packaging expects privileged utilities elsewhere, and missing Python scripts from build/install declarations. Test with `BUILD_SERVER` enabled/disabled, link of each target, and `make distcheck` inclusion of adjacent scripts if expected.
