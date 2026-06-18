<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildall.sh -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildall.sh

## Purpose
Legacy helper to build OpenAFS RPMs and kernel modules for all installed kernel source trees on the current RedHat/SuSE-like host. It detects the OS flavor and running kernel series, builds the base package, then builds module packages for each local kernel source directory.

## Important APIs, Types, And Functions
The shell script uses `/etc/redhat-release` or `/etc/SuSE-release`, `uname`, `sed`, `grep`, `awk`, `ls`, and `rpmbuild`. Important variables are `specdir`, `buildopts`, `ostype`, `osrel`, `osvers`, `kbase`, `kv`, `archlist`, `kvers`, and `ksrcdir`.

## Control Flow
It maps release text to `fc`, `rhel`, `rh`, or `suse` tags and computes `osvers`. It classifies running kernels as 2.4 or 2.6, selects source-tree base paths, runs `rpmbuild -ba` for userspace/base packages, enumerates kernel source directories, ignores symlinks, derives variant names and target architectures, removes excluded architectures such as i586 on RHEL/CentOS, and runs `rpmbuild -bb` with `build_modules 1` for each kernel/arch pair.

## State And Persistence
Outputs are normal rpmbuild products in the system RPM build tree. The script reads system release files and kernel source directories but does not maintain internal state.

## Dependencies And Integration Points
It integrates directly with `/usr/src/redhat/SPECS/openafs.spec` or SuSE's `/usr/src/packages/SPECS` and predates the mock-based builder. It depends on local kernel source layout and the spec's `osvers`, `kernvers`, `ksrcdir`, and `build_modules` definitions.

## Risks And Test Signals
Risks include unquoted shell variables, very old OS/kernel assumptions, brittle release parsing, and building against every matching local kernel source tree. Test signals are correct `osvers` derivation, successful base rpmbuild, correct module variant naming for 2.4/2.6 kernels, and RPM outputs installable against the target kernel trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildall.sh -->
