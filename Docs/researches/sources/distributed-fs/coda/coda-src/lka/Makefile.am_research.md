# sources/distributed-fs/coda/coda-src/lka/Makefile.am

Purpose: automake recipe for the lookaside database library and `mklka` client utility. It builds `liblka.la` from the public/private LKA headers, runtime database manager, and SHA helpers.

Integration: `mklka` is built only under `BUILD_CLIENT`. Include paths pull in LWP, base helpers, and `rwcdb`; link dependencies include `liblka`, `librwcdb`, and `libbase`.

Risks/test signals: build coverage verifies that the C files remain C-compatible with the configured OpenSSL/SHA, LWP, and rwcdb APIs. There are no automake test targets here; functional validation comes from `mklka` and `testlka`.
