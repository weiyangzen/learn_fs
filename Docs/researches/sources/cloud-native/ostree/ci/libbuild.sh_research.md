# sources/cloud-native/ostree/ci/libbuild.sh

Purpose: shared bash helper library for RPM-based CI builds. It centralizes OS detection, build directory defaults, package operations, and autotools build invocation.

Important APIs/functions: exported-style variables `dn`, `OS_ID`, `OS_ID_LIKE`, `OS_VERSION_ID`, `BUILDDIR=target/c`; functions `pkg_upgrade`, `make`, `build`, `pkg_install`, `pkg_install_if_os`, `pkg_install_buildroot`, `pkg_builddep`, and `pkg_builddep_runtimedep`.

Control flow: sourced scripts call helpers rather than running a main path. `build` runs `NOCONFIGURE=1 ./autogen.sh`, configures in `target/c` with Fedora-style install paths, then builds with a parallel `make`. `pkg_install_buildroot` branches on Fedora vs CentOS, enabling CRB/EPEL on CentOS.

State and persistence: creates `target/c` during builds and mutates host packages through dnf helpers. `pkg_builddep_runtimedep` temporarily installs then erases a runtime package to get dependencies.

Dependencies and integration: used by `installdeps.sh`, `rpmostree.sh`, and likely `ci/build.sh`. It assumes `/etc/os-release`, dnf, rpm builddep support, autotools, and `/usr/bin/make`.

Risks and test signals: `fatal` is referenced but not defined in this file, so unsupported OS paths rely on a caller-provided function or fail poorly. Other risks are hard-coded `/usr/lib64`, CentOS 9 EPEL URLs, and parallel make flakiness. Signals are successful configure/build and package resolution.
