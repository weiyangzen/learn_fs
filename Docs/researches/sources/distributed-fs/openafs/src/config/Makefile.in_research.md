# sources/distributed-fs/openafs/src/config/Makefile.in

Purpose: Makefile template for the `src/config` directory, building configuration helper tools and installing core public configuration headers.

Important APIs/types/functions: builds `config` from `config.o mc.o`, builds `mkvers`, generates `Makefile.version`, generates `AFS_component_version_number.c`, creates `param.h.new` by concatenating `AFS_PARAM_COMMON` and `AFS_PARAM`, and installs headers such as `afs/param.h`, `afs_sysnames.h`, `stds.h`, `icl.h`, `afs_args.h`, `venus.h`, and `vioc.h`.

Control flow: `all` builds helper tools and top-level include headers. `buildtools` builds the subset needed during early build. `Makefile.version` selects the CML or non-CML version fragment based on `CML/state`. Install and dest targets copy generated and static headers into configured include trees. `clean` removes local objects, tools, generated version files, and `param.h.new`.

State and persistence: produces build tools, generated `AFS_component_version_number.c`, `Makefile.version`, and installed/cached headers under `${TOP_INCDIR}`, `${DEST}`, and `${DESTDIR}${includedir}`.

Dependencies and integration: includes `Makefile.config` and `Makefile.lwp`, relies on Autoconf variables `AFS_PARAM` and `AFS_PARAM_COMMON`, and is required before kernel/libafs builds that need `param.h` and `afs_sysnames.h`.

Risks and test signals: risks include stale `param.h.new`, wrong CML selection, object-directory vs source-directory path mistakes, and non-atomic generated header updates. Signals are clean config-directory builds, header installation into all three include targets, and downstream libafs compilation using the generated platform header.
