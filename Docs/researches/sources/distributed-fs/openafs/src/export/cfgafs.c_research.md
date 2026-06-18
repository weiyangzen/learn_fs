# sources/distributed-fs/openafs/src/export/cfgafs.c

This AIX userspace helper loads, initializes, terminates, and unloads the AFS kernel extension. It accepts `-a mod_file` to add and `-d mod_file` to delete, uses `sysconfig(SYS_KLOAD)`, `sysconfig(SYS_CFGKMOD)`, `SYS_KULOAD`, and persists the loaded module id in `<mod_file>.kmid`.

Important control flow: add loads the module, initializes it with `CFG_INIT`, writes the kmid file, and on init failure unloads. Delete reads and unlinks the kmid file, sends `CFG_TERM`, then unloads. On load failure it queries loader messages and execs AIX `execerror`. AIX32 installs a full-dump SIGSEGV handler for better core dumps.

Dependencies are AIX sysconfig/ldr/device APIs, `AFS_component_version_number.c`, and platform path selection for `execerror`. Integration is installation scripts and kernel extension lifecycle. Risks include fixed 256-byte path buffer, stale or missing kmid files, add and delete not being mutually exclusive if both options are supplied, and partial cleanup on failures. Test signals are add/delete cycles on AIX and kmid file lifecycle checks.
