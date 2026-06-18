# sources/distributed-fs/openafs/src/dviced/Makefile.in

This Makefile builds the demand-attach fileserver `dafileserver` and `state_analyzer`. It reuses sources from `viced`, `vlserver`, `dir`, `vol`, and `fsint`, compiling with `-DRXDEBUG`, `-DFSSYNC_BUILD_SERVER`, `-DSALVSYNC_BUILD_CLIENT`, and `-DAFS_DEMAND_ATTACH_FS`.

Control flow is make target driven: explicit rules compile each borrowed object from its source directory; `dafileserver` statically links viced, directory, volume, fsint, and support libraries; `state_analyzer` links state analyzer and utility/opr libs; install/dest stage binaries into server libexec/sbin or destination tree. State is generated objects and binaries.

Dependencies include many OpenAFS libraries, hcrypto, roken, pthread/thread libs, and AIX import flags when needed. Integration is the demand-attach file server build variant and shares the directory package from this work item. Risks include object duplication across source directories, compile flags needing to match the source modules' expectations, and static link ordering. Test signals are successful `dafileserver` link, state analyzer link, demand-attach fileserver startup, volume attach/detach, fssync/salvsync interactions, and directory operations through fileserver RPCs.
