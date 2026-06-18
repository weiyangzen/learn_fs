# sources/distributed-fs/coda/coda-src/partition/tests/Makefile.am

Purpose: automake recipe for small partition backend test utilities.

Integration: builds `basic`, `setupvt`, `createmany`, `deletemany`, and `scaninodes`; distributes a sample `vicetab`; includes partition/util/vicedep/base paths; links against `libpartition`, `libutil`, and LWP.

Risks/test signals: these are command-line/manual tests rather than an automated harness. They are useful for exercising simple and ftree create/delete/list paths but may require directory setup and `makeftree` preparation.
