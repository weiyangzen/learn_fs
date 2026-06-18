<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/install.sh -->
# sources/distributed-fs/ceph-client/arch/sparc/boot/install.sh

## Purpose
This install helper copies a built SPARC kernel image into the installed boot path and optionally runs a system install hook.

## Important APIs, Types, and Functions
The script receives kernel version, image path, System.map path, and install directory arguments from Kbuild. It handles `INSTALLKERNEL` when present and otherwise copies the image to the target install directory.

## Control Flow
Kbuild invokes the script through `make install`. The script normalizes arguments, checks for an executable external installer, delegates when available, or performs a default copy workflow.

## State and Persistence Behavior
It mutates the filesystem under the requested install path. It has no runtime kernel state.

## Dependencies and Integration Points
It depends on shell utilities and the kernel build `install` convention. It integrates with distribution boot installation scripts and SPARC boot image naming.

## Risks
Wrong install paths or missing permissions can overwrite or fail to install the kernel image. Delegating to an external installer means behavior varies by distribution.

## Test Signals
Run `make ARCH=sparc install INSTALL_PATH=<tmp>` and verify image/System.map placement and successful external installer delegation when `INSTALLKERNEL` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/boot/install.sh -->
