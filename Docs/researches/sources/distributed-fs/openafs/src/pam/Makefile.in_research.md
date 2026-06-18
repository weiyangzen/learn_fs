<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/Makefile.in -->
# sources/distributed-fs/openafs/src/pam/Makefile.in

## Purpose
Builds the OpenAFS PAM modules and a small PAM test program. It creates both `pam_afs.so` and `pam_afs.krb.so`, links them with OpenAFS authentication/token libraries, and installs them only when kauth installation is enabled.

## Important APIs, Types, And Functions
The makefile uses OpenAFS config, pthread, and libtool make fragments. Key objects are account, session, password, prompt/message helpers, OpenAFS RPC/auth/protection/kauth libraries, and `ktc.c`. Kerberos-flavored objects define `AFS_KERBEROS_ENV`. Targets are `all`, `pam_afs.la`, `pam_afs.krb.la`, `test_pam`, `install`, `dest`, and `clean`.

## Control Flow
The default target builds `test_pam`, `pam_afs.la`, and `pam_afs.krb.la`. The two module targets compile shared libtool modules with different auth/credential/util/ktc objects. `test_pam` uses platform-specific link lines. `install` and `dest` copy the resulting `.so` files into the configured lib directory or dest tree only when `INSTALL_KAUTH=yes`.

## State And Persistence
Build artifacts are libtool objects/modules and `test_pam`. Install state consists of PAM module shared objects in `${libdir}` or `${DEST}/lib`; RPM packaging later relocates them to the PAM security module directory.

## Dependencies And Integration Points
This is the build glue for the PAM hook implementations in the same directory and for the RPM kauth-client package. It depends on PAM headers/libs and many OpenAFS internal libraries.

## Risks And Test Signals
Risks include symbol/export mismatches, platform-specific PAM link flags, building deprecated kauth functionality, and install path differences between build and distro package expectations. Test signals include successful libtool module builds, exported `pam_sm_*` symbols, `test_pam` linking, and PAM stack smoke tests for auth/setcred/session/password flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/pam/Makefile.in -->
