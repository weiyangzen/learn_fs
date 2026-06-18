# sources/distributed-fs/openafs/src/config/linux-version

Purpose: shell validation script for legacy Linux kernel header trees listed in `LINUX_VERS`.

Important APIs/types/functions: reads `LINUX_VERS` and `LINUX_SRCDIR`, checks each `$LINUX_SRCDIR$VERS` or fallback source directory, reads `include/linux/version.h`, extracts `UTS_RELEASE` with `fgrep` and `awk`, and accumulates buildable versions.

Control flow: missing environment variables are treated as non-fatal skips. For each requested version, missing directories or headers report errors. A matching `UTS_RELEASE` marks the version buildable; mismatches are tolerated only if the release string contains the requested subversion. At the end, if any errors occurred, it reports whether some or no kernels can be built and exits nonzero only when none are valid.

State and persistence: no persistent state; it only reports validation status.

Dependencies and integration: used from config/kernel build contexts to verify Linux header availability before building libafs for specified kernels.

Risks and test signals: risks include unquoted paths, obsolete `version.h`/`UTS_RELEASE` assumptions for modern kernels, typoed comments, and `exit -1` shell portability. Signals are header-tree checks with exact matches, Red Hat multi-version strings, missing headers, and unset environment variables.
