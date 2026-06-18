<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-makesrc.sh -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-makesrc.sh

## Purpose
Converts kernel RPMs into kernel source/build trees under `/usr/src/kernels` for older OpenAFS module build workflows. It extracts each RPM's embedded `lib/modules/*/build` directory and renames it to the convention expected by packaging scripts.

## Important APIs, Types, And Functions
The shell script uses `rpm -qp`, `rpm2cpio`, `cpio`, `sed`, `mkdir`, `chmod`, `rmdir`, and positional RPM arguments. It derives `vers`, `smp`, `arch`, and destination `kd=/usr/src/kernels/<vers><smp>-<arch>`.

## Control Flow
For each RPM argument it queries the package name, extracts the kernel version and variant prefix, derives architecture from the RPM filename, skips if the destination already exists, otherwise extracts `*lib/modules/*/build/*` into `/usr/src/kernels`, moves the build directory to the computed destination, fixes permissions, and removes empty intermediate directories.

## State And Persistence
It creates persistent kernel source directories under `/usr/src/kernels`. It also creates `/usr/src/kernels` if absent and removes temporary `lib/modules` extraction directories after a successful move.

## Dependencies And Integration Points
This supports `openafs-buildall.sh` and old RPM flows that expect local kernel build directories instead of `kernel-devel` packages. It depends on the structure of kernel RPM contents.

## Risks And Test Signals
Risks include root-owned system path mutation, fragile version/variant regexes, cleanup assumptions if extraction fails, and lack of quoting. Test signals include conversion of plain and SMP/PAE kernel RPMs, resulting build tree usability for rpmbuild, and no leftover `/usr/src/kernels/lib` directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-makesrc.sh -->
