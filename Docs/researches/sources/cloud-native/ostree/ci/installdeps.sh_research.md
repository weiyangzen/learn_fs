# sources/cloud-native/ostree/ci/installdeps.sh

Purpose: installs RPM-family CI dependencies for libostree, especially OpenShift/Prow jobs using the coreos-assembler buildroot container.

Important APIs/functions: environment guards `SKIP_INSTALLDEPS`, `CI_PKGS`; sourced helpers from `ci/libbuild.sh`: `pkg_upgrade`, `pkg_install_buildroot`, `pkg_install`, `pkg_builddep`, and `pkg_install_if_os`.

Control flow: exits without action if dependency installation is disabled or the process is not root. Otherwise it synchronizes packages, installs buildroot tooling, installs build dependencies for the `ostree` RPM, adds composefs and runtime/test packages, optionally installs caller-requested `CI_PKGS`, and adds Fedora-only developer/test tools.

State and persistence: mutates the system package set and rpm/dnf metadata. No repo-local state is created.

Dependencies and integration: integrates with `libbuild.sh`, Fedora/CentOS dnf tooling, RPM spec build-dependency metadata, sanitizer runtimes, fsverity, jq, GJS tests, coccinelle, clang, and PyYAML.

Risks and test signals: risks include package drift, root-only behavior hiding missing deps on non-root runs, and `dnf builddep ostree` depending on repo metadata. The signal is whether later `ci/build.sh` or direct autotools builds configure with desired optional features.
