<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-switchroot.am -->
## sources/cloud-native/ostree/Makefile-switchroot.am

### Purpose
This fragment builds and installs early-boot switchroot helpers: `ostree-prepare-root`, `ostree-remount`, and optionally `ostree-system-generator`.

### APIs, Types, and Control Flow
It initializes prepare-root sources and flags, installs `ostree-remount` under boot programs when systemd is enabled or as a check program otherwise, and supports a static prepare-root path using `STATIC_COMPILER` and `ostree-prepare-root-static.c`. The normal path builds `ostree-prepare-root.c` with GLib/GIO, crypto, libotcore, libotutil, and libglnx. SELinux, composefs, systemd, and systemd+libmount conditionals add CPPFLAGS/LIBADD and the systemd generator target.

### State, Dependencies, and Integration
Installed programs land under `$(prefix)/lib/ostree` and systemd generator directories when enabled. These binaries are boot-critical and integrate with boot unit files from `Makefile-boot.am` and bootc/container tests.

### Risks and Test Signals
Static prepare-root exists for systems without populated `/lib`; wrong linkage can break boot. Feature macros must reflect runtime mount behavior. Test signals include switchroot tests, bootc integration, ASAN/unit builds, and installed boot asset checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-switchroot.am -->
