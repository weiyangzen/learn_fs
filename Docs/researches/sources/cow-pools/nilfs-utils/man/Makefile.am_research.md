# File Research: sources/cow-pools/nilfs-utils/man/Makefile.am

## Scope

Defines the manual pages distributed by the NILFS utilities build.

## Build Behavior

`dist_man_MANS` lists section 8, section 5, and section 1 manpages for `nilfs`, `mkfs.nilfs2`, mount/umount helpers, checkpoint tools, segment tools, cleaner daemon/configuration, tuning, cleaning, and resizing tools.

## Dependencies And Risks

This is packaging metadata only. Correctness depends on every listed manpage existing in the man directory at distribution time; missing files would fail Automake distribution or install targets.
