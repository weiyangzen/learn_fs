<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/glib-tap.mk -->
## sources/cloud-native/ostree/buildutil/glib-tap.mk

### Purpose
This make fragment adapts GLib-style TAP tests to automake, supporting both in-tree and installed tests.

### APIs, Types, and Control Flow
It sets `AM_TESTS_ENVIRONMENT`, `LOG_DRIVER` to `tap-driver.sh`, and `LOG_COMPILER` to `tap-test`. It initializes test variables for installed, uninstalled, dist, data, scripts, programs, and libtool libraries. It builds `TESTS` from runnable uninstalled test programs/scripts, computes aggregate lists for all test artifacts, adds distributed scripts/data to `EXTRA_DIST`, chooses `check_*` or `noinst_*` based on `ENABLE_ALWAYS_BUILD_TESTS`, and under `ENABLE_INSTALLED_TESTS` installs test programs/scripts/data and generates `.test` metadata files.

### State, Dependencies, and Integration
Generated `.test` metadata is added to `CLEANFILES`. It integrates with `Makefile-tests.am`, automake parallel test harness, GLib test environment variables, and installed-test runners.

### Risks and Test Signals
The variable taxonomy is broad; placing a file in the wrong variable changes whether it is run, installed, or distributed. Test signal is automake recognizing the expected tests and installed-test metadata generation.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/glib-tap.mk -->
