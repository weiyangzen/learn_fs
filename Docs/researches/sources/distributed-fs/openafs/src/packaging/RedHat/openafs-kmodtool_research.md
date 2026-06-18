<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-kmodtool -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-kmodtool

## Purpose
Generates RPM spec fragments and kernel-version metadata for OpenAFS kmod packages. It is a Fedora/RHEL-style kmodtool adapted for OpenAFS and emits `%package`, dependency, scriptlet, and file-list sections for one or more kernel variants.

## Important APIs, Types, And Functions
The bash script exposes commands `verrel`, `variant`, `rpmtemplate`, and `version`. Functions include `get_verrel`, `print_verrel`, `get_variant`, `print_variant`, `get_rpmtemplate`, and `print_rpmtemplate`. It uses extended glob patterns to strip known variants such as PAE, debug, smp, xen, kdump, and handles elrepo, EL, Fedora, RHEL, and Amazon version patterns.

## Control Flow
`verrel` normalizes a `uname -r` string to the version-release base used by build dependencies. `variant` subtracts that base to obtain the kernel variant suffix. `rpmtemplate` validates kmod name, kernel version, and depmod path, computes kernel dependency/provides naming for OS families, then prints RPM macro text for `kmod-openafs` packages, depmod post scripts, module file lists, and older debuginfo subpackages.

## State And Persistence
The script is stateless and writes generated spec text to stdout. The RPM spec consumes it through `%{expand:%(... rpmtemplate ...)}`.

## Dependencies And Integration Points
It is copied into SRPM sources by `makesrpm.pl` and invoked by `openafs.spec.in`. Its output must align with kernel package naming across Fedora/RHEL/Amazon and with where the spec installs `/lib/modules/<kname>/extra/openafs/openafs.ko`.

## Risks And Test Signals
Risks include kernel naming drift, brittle shell pattern handling for new distro releases, dependency epoch differences such as Amazon 2023, and mismatches between generated `%files` paths and install paths. Test signals include `openafs-kmodtool verrel/variant` on representative `uname -r` values and successful rpmbuild dependency resolution/install for standard and variant kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-kmodtool -->
