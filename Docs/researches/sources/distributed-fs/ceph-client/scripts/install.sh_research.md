# sources/distributed-fs/ceph-client/scripts/install.sh

## Purpose
Provides common kernel install dispatch logic for architectures that delegate installation to user or arch-specific scripts.

## APIs, Control Flow, and State
The shell script requires `KBUILD_IMAGE` and `System.map` to exist, creates `INSTALL_PATH` if set and missing, then searches executable install scripts in `${HOME}/bin/${INSTALLKERNEL}`, `/sbin/${INSTALLKERNEL}`, `${srctree}/arch/${SRCARCH}/install.sh`, and `${srctree}/arch/${SRCARCH}/boot/install.sh`. The first executable script is `exec`ed with `KERNELRELEASE`, image, `System.map`, and install path. If none are found, it exits with an error.

## Dependencies and Integration
It depends on kbuild environment variables and external installkernel-compatible scripts. It has no persistent state beyond creating the install directory.

## Risks and Test Signals
Risks include missing environment variables, custom scripts with incompatible semantics, and no fallback copy behavior. Test signals are `make install` after a build, correct argument order, and clear failure when artifacts or scripts are missing.
