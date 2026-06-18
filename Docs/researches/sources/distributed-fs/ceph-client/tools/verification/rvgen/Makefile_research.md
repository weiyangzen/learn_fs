# sources/distributed-fs/ceph-client/tools/verification/rvgen/Makefile

Purpose: this Makefile installs the Python `rvgen` runtime-verification monitor generator and its helper command.

Important variables and targets: `prefix`, `bindir`, `mandir`, and `srcdir` define install roots. `PYLIB` is detected through `python3 -c 'import sysconfig'`. `all` and `clean` are no-ops. `install` copies Python modules into `$(PYLIB)/rvgen`, installs `dot2c` and `rvgen` entry scripts into `$(bindir)`, and recursively copies templates.

Control flow and integration: there is no build step; installation is file copying. The module list includes files outside this subset such as `ltl2ba.py` and `ltl2k.py`, showing rvgen supports DOT and LTL monitor generation.

State, dependencies, risks, and tests: state is installed files under `DESTDIR`/system paths. Dependencies include Python 3 and `install`. Risks include no uninstall, no byte-compilation, no package metadata, and recursive template copy leaving stale files if reinstalling over older content. Test signals are `make install DESTDIR=...`, executable `rvgen`, executable `dot2c`, and imports from the installed `rvgen` package.
