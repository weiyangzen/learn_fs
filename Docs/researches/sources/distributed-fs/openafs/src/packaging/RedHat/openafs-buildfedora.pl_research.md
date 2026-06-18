<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildfedora.pl -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildfedora.pl

## Purpose
Builds OpenAFS RPMs on Fedora systems using Fedora-style kmod variants discovered from installed `kernel*-devel` packages. It builds the base package once and then module packages for every discovered architecture/kernel/variant tuple.

## Important APIs, Types, And Functions
The Perl script uses `rpm -q fedora-release`, `rpm -q --queryformat` for `kernel`, `kernel-PAE`, `kernel-kdump`, and `kernel-xen` devel packages, `ls -d /usr/src/kernels/...`, and `rpmbuild`. It stores variants in a nested `%list` keyed by arch and version.

## Control Flow
It determines the Fedora version, iterates known variants, skips variants whose RPM query fails, parses package names into kernel version and architecture, discovers arch-specific kernel source directories, and records variant lists. It then runs `rpmbuild -ba` with `fedorakmod 1` and `osvers fc<version>`, followed by `rpmbuild -bb` for each arch/version with `build_modules 1`, `kernvers`, and `kvariants`.

## State And Persistence
The script writes only standard rpmbuild artifacts. Its state is the in-memory `%list` derived from installed kernel-devel packages and `/usr/src/kernels`.

## Dependencies And Integration Points
It integrates with the RedHat spec's Fedora kmod branch and expects `openafs.spec` in `/usr/src/redhat/SPECS`. It overlaps with but is simpler than `mockbuild.pl`.

## Risks And Test Signals
Risks include old Fedora variant assumptions, fragile regex parsing of kernel package names, reliance on local installed kernel-devel packages, and shell-string invocation of rpmbuild. Test signals include correct variant discovery for installed kernels and successful base plus kmod RPM builds for each recorded tuple.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-buildfedora.pl -->
