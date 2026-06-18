# sources/distributed-fs/openafs/src/afs/HPUX/osi_debug.c

## sources/distributed-fs/openafs/src/afs/HPUX/osi_debug.c

Purpose: this HP-UX file is effectively an include aggregation unit for AFS debug-related kernel symbols. It pulls in platform and AFS headers but defines no functions or persistent state.

Important APIs/types/functions: there are no local APIs. The included headers expose callback queue, DNLC, stats, sysname, trace, exporter, rx/fcrypt, NFS client, private data, and Vice structures to whatever object context this file was intended to satisfy.

Control flow: none. Loading or compiling the file only validates that the selected HP-UX build environment can include these headers together.

State/persistence: none locally. Any state is in included modules such as tracing, stats, or callback queues.

Dependencies/integration: depends on `afsconfig.h`, `param.h`, HP-UX system includes, OpenAFS internal headers, and RX crypto headers. It likely exists for legacy build/link compatibility rather than runtime logic.

Risks/test signals: risk is header drift: incompatible typedefs, macros, or include ordering can break HP-UX builds. Build-only tests are the meaningful signal; runtime tests are not applicable.
