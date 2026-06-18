# sources/distributed-fs/ceph-client/scripts/headers_install.sh

## Purpose
Sanitizes exported kernel UAPI headers for userspace installation.

## APIs, Control Flow, and State
The shell script takes exactly `INFILE OUTFILE`, creates `$OUTFILE.tmp`, and registers a trap to remove partial outputs. It first enforces that GPL SPDX identifiers for syscall headers include `WITH Linux-syscall-note`. It then runs `sed` rewrites to remove selected annotations/includes, convert `__packed`, wrap `inline/asm/volatile` as underscored names, and normalize `_UAPI` guard markers. `scripts/unifdef` removes `__KERNEL__` code and applies `__EXPORTED_HEADERS__`. A final sed program strips block comments and scans remaining code for leaked `CONFIG_*` tokens, failing if any are found.

## Dependencies and Integration
It depends on POSIX shell, sed with extended regex, `scripts/unifdef`, and kbuild header-install targets. Persistent state is only the generated output header.

## Risks and Test Signals
Risks include sed patterns missing new annotations, false positives/negatives in CONFIG leak detection, and output deletion by trap on errors. Test signals are header-install target success, missing syscall-note failure, no leaked config names, and userspace compilation against installed headers.
