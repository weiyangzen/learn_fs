<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/version.c -->
## sources/distributed-fs/ceph-client/fs/proc/version.c

Purpose: implements `/proc/version`, exposing the kernel banner built from UTS sysname, release, and version.

Important APIs and functions: `version_proc_show` formats `linux_proc_banner` with `utsname()->sysname`, `release`, and `version`; `proc_version_init` registers a permanent single proc file.

Control flow: each read emits one banner line through seq_file. Init creates `version` under proc root and marks it permanent.

State and persistence behavior: no local state persists. It reads current UTS namespace/system naming data and static kernel banner format.

Dependencies and integration points: depends on UTS name accessors, procfs single-file creation, and seq_file. It is a longstanding userspace ABI for kernel version reporting.

Risks: output format is legacy ABI; changing banner content or newline behavior can break parsers. UTS namespace interactions should match other version/name proc outputs.

Test signals: read `/proc/version`; compare with `uname` fields and kernel build version; check behavior in UTS namespaces; verify permanent entry creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/version.c -->
