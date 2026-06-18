# sources/distributed-fs/openafs/src/config/ranlib

This shell wrapper replaces `ranlib` on platforms where the operation is intentionally ignored. It prints a diagnostic of the form `ranlib <arg> ignored` and exits with the shell's default success status unless `echo` fails.

There are no APIs beyond the executable script interface. It has no state or persistence. Integration is through Makefiles that set `RANLIB` to this script when archive indexing is unnecessary or unsupported.

Risks are limited but real: build logs can show success even if a platform actually needs archive symbol indexing. Test signals are successful static library linkage on the affected platform and no unresolved symbols caused by missing archive indexes.
