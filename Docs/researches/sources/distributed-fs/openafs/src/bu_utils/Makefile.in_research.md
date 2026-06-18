# sources/distributed-fs/openafs/src/bu_utils/Makefile.in

This makefile builds and installs the backup utility `fms`, a filemark-size measurement program for tape devices. It includes OpenAFS config and LWP make fragments and defines `all`, `fms`, `install`, `dest`, `clean`, and version-generation integration.

Important build variables are `FMSLIBS`, which links `libcmd.a`, `libusd.a`, `util.a`, `libopr.a`, roken, and `XLIBS`; `fms.o`, which depends on `fms.c` and `AFS_component_version_number.o`; and install destinations under `${sbindir}` or `${DEST}/etc`.

There is no runtime state in the makefile, but it produces `fms`, object files, and component version C. Dependencies are OpenAFS build macros, USD tape support, command parsing, util/opr, and roken. Risks include platform tape-library availability and old-style `dest` install path divergence from modern `install`. Test signals are successful build/link and clean removal.
