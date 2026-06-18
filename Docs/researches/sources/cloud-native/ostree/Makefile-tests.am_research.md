<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-tests.am -->
## sources/cloud-native/ostree/Makefile-tests.am

### Purpose
This fragment declares OSTree's test environment, shell and C test suites, installed-test support, helper binaries, test data, and test-specific build/link rules.

### APIs, Types, and Control Flow
It adds TAP driver assets to distribution, configures `AM_TESTS_ENVIRONMENT` with uninstalled source/build paths, fatal GLib warnings, typelib/library paths, local PATH, feature flags, and proxy/VFS overrides. It lists large sets of installed-or-uninstalled shell tests for pull, deploy, admin, static delta, signing, xattrs, composefs, concurrency, and more. Conditional sections add ed25519, SPKI, GPGME, FUSE, libsoup, GJS, Avahi, libarchive, and installed-test data. It builds helper/test programs such as bloom, repo-finder, varint, checksum, lzma, PEM, bsdiff, otcore, and trivial HTTPD. Symlink-stamp rules expose built binaries under `tests/`.

### State, Dependencies, and Integration
It integrates with `buildutil/glib-tap.mk`, `Makefile-ostree.am`, libostree/libotutil/libotcore, installed-test packaging, and GNOME desktop testing. Install hooks create installed-test symlinks and ASAN-adjusted `libtest.sh`.

### Risks and Test Signals
The file is a central CI surface: missing a test in the right variable can exclude it from `make check` or installed tests. Environment variables intentionally constrain GLib behavior; changing them can cause nondeterminism. Test signal is the suite itself, plus installed-test runners and distro matrix jobs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/Makefile-tests.am -->
