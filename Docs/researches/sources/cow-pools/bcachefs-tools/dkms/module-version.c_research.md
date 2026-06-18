# File Research: sources/cow-pools/bcachefs-tools/dkms/module-version.c

This C file includes Linux module support and generated `version.h`, then emits `MODULE_VERSION(bcachefs_version)`.

Integration role: DKMS-only object appended by `fs/Makefile` to embed module version metadata.

Risk/maintenance notes: depends on `version.h` being generated and copied into the DKMS source tree.
