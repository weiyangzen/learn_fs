# File Research: sources/cow-pools/bcachefs-tools/dkms/Makefile

- DKMS external-module Makefile.
- Exports `BCACHEFS_DKMS=1`, includes generated `build.vars`, and forwards debug/test/restart-injection flags.
- In kbuild context, adds include path and builds `src/fs/bcachefs/`.
- Outside kbuild, invokes the running kernel build tree and provides a clean target.
