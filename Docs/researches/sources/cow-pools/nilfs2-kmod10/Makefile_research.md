# File Research: sources/cow-pools/nilfs2-kmod10/Makefile

Top-level wrapper Makefile for the out-of-tree NILFS2 kernel module source tree. It defines `SUBDIRS = fs` and forwards `all`, `clean`, `install`, and `uninstall` targets into that directory with `$(MAKE) -C $@ $(RULE)`.

The file has no direct kernel build logic; it is a dispatcher. The important integration point is that target-specific `RULE` assignments translate top-level lifecycle targets into equivalent recursive targets under `fs`.

Risk/notes: minimal logic, but recursive build behavior depends on GNU make target-specific variable handling and on the subdirectory Makefiles implementing the same target names.
