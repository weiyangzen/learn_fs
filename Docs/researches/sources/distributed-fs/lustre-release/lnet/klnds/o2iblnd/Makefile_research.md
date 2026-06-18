<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/Makefile -->
# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/Makefile

Final split target: `Docs/researches/sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/Makefile_research.md`.

Purpose: builds the external OFED o2iblnd Lustre LND module and sets compiler include/feature flags so external OFED headers override in-kernel ones.

Important APIs/types/functions: conditional `obj-m += ko2iblnd.o` under `BUILD_EXT_O2IB`; object list `o2iblnd.o o2iblnd_cb.o o2iblnd_modparams.o`; `ccflags-y += $(EXTRA_KCFLAGS)`; `NOSTDINC_FLAGS` adds `EXTRA_OFED_CONFIG`, `EXTRA_OFED_INCLUDE`, `-DEXTERNAL_OFED_BUILD`, and `-DEXTERNAL_OFED_VERSION`.

Control flow: when external build is enabled, kbuild links the three objects into `ko2iblnd`. Include flags are arranged to prefer external OFED. Optional `CONFIG_GCOV_PROFILE_LNET` enables coverage.

State and persistence behavior: build-only file; runtime module state is in the C sources.

Dependencies and integration: depends on external OFED config/include variables, Lustre kbuild, and version variable `EXT_O2IB_VER`.

Risks: missing or misordered OFED include flags can silently build against in-kernel headers. `BUILD_EXT_O2IB` controls module emission but object variables are still declared. Version define quoting must survive make/shell expansion.

Test signals: build with and without `BUILD_EXT_O2IB`, verify include precedence, inspect compiler command for external defines, build with GCOV enabled, and load module against the expected OFED stack.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/Makefile -->
