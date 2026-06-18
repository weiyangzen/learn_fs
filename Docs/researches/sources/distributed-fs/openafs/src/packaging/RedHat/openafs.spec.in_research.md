<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs.spec.in -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs.spec.in

## Purpose
The primary RPM spec template for OpenAFS on Fedora, RHEL, CentOS, and Amazon Linux. It builds userspace packages, optional authentication libraries, Kerberos tools, legacy kauth packages, documentation, kernel-source and DKMS packages, and kernel-module RPMs across distro/kernel variants.

## Important APIs, Types, And Functions
Important macros include `afsvers`, `pkgvers`, `pkgrel`, `source_date_epoch`, `build_userspace`, `build_modules`, `build_dkmspkg`, `kauth_support`, `build_authlibs`, `krb5support`, `depmod`, `kmodtool`, `kverrel`, `kvariants`, `dkms_version`, `initdir`, and `pamdir`. Source entries include OpenAFS source, release notes, ChangeLog, CellServDB, build helpers, and `openafs-kmodtool`. It invokes `./configure`, `make only_libafs_tree`, `make all_nolibafs`, `make libafs`, `make install_nolibafs`, DKMS config generation, systemd/SysV script installation, and kmodtool-generated spec sections.

## Control Flow
The spec sets defaults unless overridden by rpmbuild definitions, declares subpackages, expands kmod package templates when module builds are enabled, unpacks the source, computes the OpenAFS sysname from target architecture, chooses kernel source paths, configures OpenAFS with transarc paths and optional krb5/swig/kauth features, builds the libafs tree, configures additional variant module trees, builds userspace and modules, installs userspace into `RPM_BUILD_ROOT`, prunes obsolete/duplicated files, relocates `afsd` and admin utilities, installs PAM modules when kauth is enabled, adds init/systemd files, creates client/server configuration directories, installs CellServDB.dist/cacheinfo/ThisCell, emits DKMS and kernel-source trees, installs docs, creates compatibility symlinks, installs kmods into `/lib/modules/.../extra/openafs`, then defines package scriptlets and file lists.

## State And Persistence
Build-time state includes `libafs_tree`, `_kmod_build_<variant>` directories, `RPM_BUILD_ROOT`, generated `dkms.conf`, generated `Distribution`-like package manifests, and installed module paths. Runtime package state includes `/etc/sysconfig/openafs`, `/usr/vice`, `/usr/afs`, `/afs`, CellServDB.local/dist/combined files, systemd or SysV service registrations, DKMS registrations, and depmod metadata.

## Dependencies And Integration Points
The spec is consumed by `makesrpm.pl`, `mockbuild.pl`, direct rpmbuild helpers, and distro packagers. It integrates with `openafs-kmodtool`, `openafs-client-systemd-helper.sh`, client/server unit files, legacy init scripts, OpenAFS configure/build targets, PAM, Kerberos, SWIG Perl bindings, DKMS, kernel-devel packages, systemd scriptlets, and central.org CellServDB distribution.

## Risks And Test Signals
Risks include macro drift across RPM versions/distros, kernel-source path naming changes, broad file-list fragility, package split conflicts, DKMS build failures, service scriptlet behavior on upgrade/removal, security implications of legacy kauth/PAM packaging, and hard-coded Source20 freshness. Test signals include SRPM creation, mock rebuilds with userspace-only and modules-only modes, install/upgrade/remove of every subpackage, DKMS add/build/install/remove, generated kmod dependency correctness, systemd/SysV service operation, `rpmlint` or distro policy review, and file-list completeness on all supported architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs.spec.in -->
