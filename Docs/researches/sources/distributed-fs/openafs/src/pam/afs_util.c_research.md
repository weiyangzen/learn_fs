<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_util.c -->
# sources/distributed-fs/openafs/src/pam/afs_util.c

## Purpose
Provides shared utility state and helper functions for the OpenAFS PAM module: secure cleanup callbacks, integer-to-string conversion, external `klog` execution, and current PAG lookup.

## Important APIs, Types, And Functions
Globals are `pam_afs_ident` and `pam_afs_lh`. Functions are `lc_cleanup`, `nil_cleanup`, `cv2string`, `do_klog`, and `getPAG`. `do_klog` chooses `KLOG` or `KLOGKRB`, builds `klog` arguments including optional cell and lifetime, pipes the password to the child process, and returns the child exit status. `getPAG` uses `ktc_curpag` and masks the low 24 bits.

## Control Flow
Cleanup callbacks zero/free or ignore PAM data. `do_klog` validates executable access, creates a pipe, forks, wires child stdin/stdout to the pipe, execs klog, writes password plus newline from the parent, closes descriptors, waits, and reports the exit code. `getPAG` maps invalid/current-none PAG values to `-1`.

## State And Persistence
The file defines process-global strings used as syslog identity and PAM data key. `do_klog` can create AFS/Kerberos tokens through the external command as a side effect. `lc_cleanup` erases password data when PAM ends.

## Dependencies And Integration Points
Auth and setcred call these helpers. The file depends on OpenAFS auth/ktc APIs, PAM types, syslog, process control, and hard-coded legacy paths `/usr/afsws/bin/klog`, `klog.krb`, and `unlog`.

## Risks And Test Signals
Risks include hard-coded executable paths, pipe descriptor handling that connects stdout to the same pipe, password exposure through external process I/O, wait behavior returning success on unexpected pid mismatch, and no close-on-exec discipline. Test signals include cleanup wiping, `do_klog` success/failure with fake helpers, alternate cell/lifetime arguments, and `getPAG` values before/after `setpag`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/afs_util.c -->
