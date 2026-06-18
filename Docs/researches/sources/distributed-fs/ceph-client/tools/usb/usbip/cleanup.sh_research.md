# sources/distributed-fs/ceph-client/tools/usb/usbip/cleanup.sh

Purpose: `cleanup.sh` removes generated Autotools and build files from the usbip userspace directory.

Important commands and data: if a readable `Makefile` exists, it first runs `make distclean`. It then removes a fixed `FILES` list containing `aclocal.m4`, `autom4te.cache`, `compile`, `config.*`, `configure`, `depcomp`, `install-sh`, `libtool`, `ltmain.sh`, top-level and subdir `Makefile`/`Makefile.in`, `missing`, and `cscope.out`.

Control flow and persistence: the script is linear and destructive for generated files only. It uses `rm -vRf`, so deletion is recursive for directories such as `autom4te.cache` and verbose for auditability.

Dependencies, risks, and tests: it assumes the current directory is `tools/usb/usbip`. Risks include deleting a user-maintained file if it has the same generated filename, and `make distclean` executing arbitrary generated make rules. Test signals are a clean source tree where `autogen.sh` can regenerate the removed files and `git status` shows only expected generated-file changes.
