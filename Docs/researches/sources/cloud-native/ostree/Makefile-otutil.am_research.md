<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-otutil.am -->
## sources/cloud-native/ostree/Makefile-otutil.am

### Purpose
This fragment builds the private `libotutil.la` utility library used by libostree, CLI tools, and tests.

### APIs, Types, and Control Flow
It adds checksum, filesystem, keyfile, option parsing, Unix, variant, GIO, tool, and JSON writer utility sources. Under `USE_GPGME`, it adds GPG utility and zbase32 sources. CFLAGS include libglnx/libotutil include paths, locale directory, GLib/GIO/GPGME/crypto/systemd flags, and LIBADD mirrors those dependencies.

### State, Dependencies, and Integration
The library is non-installed and linked into libostree and command/test binaries. It centralizes common helpers so higher-level fragments do not duplicate utility source lists.

### Risks and Test Signals
Utility behavior has broad blast radius: changes can affect CLI parsing, repository IO, checksums, and tests. Conditional GPG sources must match GPGME availability. Test signals include utility-specific C tests and any libostree/CLI build using these helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-otutil.am -->
