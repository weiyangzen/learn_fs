# File Research: sources/cow-pools/nilfs2-kmod10/fs/Makefile

Second-level wrapper Makefile. It defines `SUBDIRS = nilfs2` and forwards `all`, `clean`, `install`, and `uninstall` into `fs/nilfs2`.

This mirrors the repository top-level Makefile and keeps the external module build rooted at `fs/nilfs2/Makefile`, where kbuild variables and install/unload behavior are defined.

Risk/notes: no validation or fallback exists here; failures are delegated to the child Makefile.
