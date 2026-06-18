<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_util.h -->
# sources/distributed-fs/openafs/src/pam/afs_util.h

## Purpose
Declares shared utility globals, cleanup callbacks, klog/PAG helpers, and compatibility macros for the OpenAFS PAM module.

## Important APIs, Types, And Functions
Declarations include `pam_afs_ident`, `pam_afs_lh`, `lc_cleanup`, `nil_cleanup`, `cv2string`, `do_klog`, and `getPAG`. Constants define `KLOG`, `KLOGKRB`, `UNLOG`, and `IGNORE_MAX`. HPUX compatibility maps some PAM/syslog APIs.

## Control Flow
The header contains no runtime flow. It provides compile-time contracts and platform shims used by the PAM implementation files.

## State And Persistence
No state is stored here beyond externally defined global names and path constants.

## Dependencies And Integration Points
It is included by all major PAM files and ties option parsing (`IGNORE_MAX`) and external helper execution paths together.

## Risks And Test Signals
Risks include obsolete `/usr/afsws` paths, platform macro drift, and globals declared as mutable `char *`. Test signals are clean builds across supported PAM platforms and correct helper path usage in installed packages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_util.h -->
