<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-otcore.am -->
## sources/cloud-native/ostree/Makefile-otcore.am

### Purpose
This fragment builds the private `libotcore.la` helper library for core boot/signature functionality shared by OSTree components.

### APIs, Types, and Control Flow
It adds `libotcore.la` to `noinst_LTLIBRARIES` and compiles `otcore.h`, ed25519 verification, prepare-root support, and SPKI verification sources. It notes a partial circular dependency because the library uses includes from libostree.

### State, Dependencies, and Integration
It links GLib/GIO, GPGME when configured, systemd, crypto libraries, and optionally composefs. It is linked by switchroot helpers, tests, and libostree paths that need these core helpers.

### Risks and Test Signals
The CFLAGS line includes `$(OT_DEP_CRYPTO_LIBS)` where CFLAGS might be expected, which may be intentional or a latent build hygiene issue depending on configure output. Conditional composefs linkage must match source usage. Test signals are prepare-root, signature verification, and otcore unit tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-otcore.am -->
