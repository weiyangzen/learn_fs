# sources/distributed-fs/glusterfs/xlators/performance/nl-cache/src/Makefile.am

Purpose: builds the `nl-cache.la` GlusterFS performance xlator module.

Important APIs, types, and functions: `xlator_LTLIBRARIES = nl-cache.la`; installs under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/performance`; compiles `nl-cache.c` and `nl-cache-helper.c`; ships private headers `nl-cache.h`, `nl-cache-mem-types.h`, and `nl-cache-messages.h`.

Control flow: Automake compiles the two C files with Gluster CPP/C flags, links against `libglusterfs.la`, and produces a loadable module using `$(GF_XLATOR_DEFAULT_LDFLAGS)`.

State and persistence: build metadata only. It contributes no runtime cache state.

Dependencies and integration: includes `libglusterfs/src`, generated and source XDR include paths, and `$(CONTRIBDIR)/timer-wheel`, which is required by `nl-cache-helper.c` for cache expiry timers.

Risks and test signals: the timer-wheel include path is a specific integration requirement; removing it would break helper compilation. Build tests should verify module link, installed path, and distribution packaging of the noinst headers.
