# sources/distributed-fs/ceph-client/scripts/depmod.sh

## Purpose
`depmod.sh` is a thin wrapper used during `make modules_install` to run `depmod` with the correct kernel release and `System.map`, while gracefully skipping when prerequisites are absent.

## Important APIs, Types, and Functions
It accepts exactly one argument, `kernelrelease`. It reads environment variables `DEPMOD`, `objtree`, and `INSTALL_MOD_PATH`. It builds `depmod` arguments `-ae -F ${objtree}/System.map`, optionally adding `-b $INSTALL_MOD_PATH`.

## Control Flow and State
The script validates argv count, defaults `DEPMOD=depmod`, checks for readable `${objtree}/System.map`, appends `/sbin` to `PATH`, checks command availability, then `exec`s depmod. It persists no state beyond depmod's normal module dependency outputs.

## Dependencies and Integration
It depends on POSIX shell, `command -v`, and kmod `depmod`. It is invoked by Kbuild modules installation.

## Risks and Test Signals
The `command -v` test uses unquoted command substitution, so unusual `DEPMOD` values are fragile. Missing `System.map` or `depmod` is a warning, not failure. Test missing args, missing `System.map`, custom `DEPMOD`, `INSTALL_MOD_PATH`, and successful exec argument ordering.
