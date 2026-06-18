# sources/distributed-fs/openafs/src/butm/Makefile.in

Purpose: builds and installs the backup tape module library and its local test programs. The primary artifact is `libbutm.a`, built from `file_tm.o` and `AFS_component_version_number.o`, then copied to `${TOP_LIBDIR}`.

Important targets: `all` builds `libbutm.a`, installs `butm_prototypes.h` into the top include tree, and builds `test_ftm` and `butm_test`. `test_ftm` and `butm_test` link against `libbutm.a`, `libbubasics.a`, LWP, USD, com_err, util, opr, roken, and platform libraries. `install` and `dest` place the static library in AFS lib directories.

Control flow and dependencies: includes common config and LWP make fragments. Object dependencies ensure `file_tm.c` and tests rebuild when public butm/com_err headers or component version source change.

Risks and tests: `test` only prints a usage hint for manual execution instead of running assertions. The library is static-only here, and tests require device configuration or tape hardware/file simulation. Duplicate `libafscom_err.a` in `LIBS` is harmless but noisy.
