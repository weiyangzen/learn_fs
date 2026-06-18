
# sources/distributed-fs/openafs/src/usd/Makefile.in

This makefile builds the USD user-space device library as both libtool shared/static output and a legacy `libusd.a`, and installs `usd.h`. Objects are `usd_file.lo` and `AFS_component_version_number.lo`; dependencies include `liboafs_opr`.

Targets include `liboafs_usd.la`, `libusd.a`, top-level library/header copies, install, dest, and clean. It includes top-level config, pthread config, and libtool rules. The makefile only builds the POSIX implementation in this path; Windows builds use the platform makefile and `usd_nt.c`.

Persistence is build artifact installation into library and include directories. Risks are build-system consistency between libtool and legacy static outputs, symbol list alignment through `liboafs_usd.la.sym`, and ensuring `usd.h` is copied to the top include tree. Test signals are full library build, install/dest staging, and downstream link of the USD test.
