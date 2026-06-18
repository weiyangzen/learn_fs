<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/lmdb/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/lmdb/module.mk.in

Purpose: build-system fragment for OrangeFS's vendored/internal LMDB sources. It is conditional on `WANT_INTERNAL_LMDB=yes`, so the LMDB backend is only built when configured to use the bundled implementation rather than an external library or no LMDB path.

Important variables: `DIR := src/common/lmdb`; `SRC` includes `mdb.c` and `midl.c`; both `SERVERSRC` and `LIBSRC` receive those files so the internal LMDB code is available to server and library targets. `MODCFLAGS_$(DIR)/mdb.c := -std=c99` sets C99 mode for `mdb.c`.

Control flow is make-time only. The `ifeq` block controls whether source lists and flags are emitted. There is no runtime state or persistence behavior, but this fragment gates whether LMDB's persistent database implementation is compiled into OrangeFS artifacts.

Dependencies are the surrounding OrangeFS make infrastructure, especially variables such as `WANT_INTERNAL_LMDB`, `SERVERSRC`, `LIBSRC`, and `MODCFLAGS_*`. Integration points are the top-level module include system and the LMDB files in the same directory.

Risks: the line `MODCFLAGS_$(DIR)/midl.c.c := -std=c99` appears to have an extra `.c`, so the intended per-file C99 flag may not apply to `midl.c`. If the compiler defaults are stricter or older, this could produce configuration-specific build issues. Test signals are configure/build matrix runs with `WANT_INTERNAL_LMDB=yes` and `no`, plus inspection that both `mdb.c` and `midl.c` receive expected compiler flags and are linked into all intended artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/lmdb/module.mk.in -->
