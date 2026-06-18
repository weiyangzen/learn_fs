# File Research: sources/cow-pools/bcachefs-tools/dkms/dkms.conf.in

- DKMS config template for package `bcachefs`.
- Version placeholder is filled by the top-level Makefile.
- Builds module `bcachefs` from `src/fs/bcachefs`, installs under `/kernel/fs/bcachefs`, disables stripping, auto-installs, and requires kernel >= 6.16.
