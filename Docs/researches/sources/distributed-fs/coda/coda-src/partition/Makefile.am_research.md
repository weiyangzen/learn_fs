# sources/distributed-fs/coda/coda-src/partition/Makefile.am

Purpose: automake recipe for the server partition/inode abstraction library and `inoder` utility.

Integration: under `BUILD_SERVER`, builds `libpartition.la`, `inoder`, and the `vicetab.5` manpage. Library sources include vicetab parsing, partition registry, inode operation dispatch, simple/ftree/backup backends, and inode metadata headers. Include/link dependencies cover RPC2 flags, base/util, vicedep, and LWP.

Risks/test signals: build confirms backend method tables and headers stay compatible. The partition tests have their own `tests/Makefile.am`; this file does not install runtime tests.
