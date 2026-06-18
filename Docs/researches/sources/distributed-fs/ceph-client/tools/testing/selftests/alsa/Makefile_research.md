# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/Makefile

Purpose: builds ALSA kselftest binaries and a shared local configuration helper library.

Important APIs/types/functions: verifies `pkg-config --exists alsa`; adds ALSA CFLAGS/LDLIBS, pthreads, output rpath, and `KHDR_INCLUDES`; sets `TEST_GEN_PROGS` to `mixer-test`, `pcm-test`, `test-pcmtest-driver`, `utimer-test`; `TEST_GEN_PROGS_EXTENDED` to `libatest.so` and `global-timer`; `TEST_FILES` to `conf.d` and `pcm-test.conf`; builds `libatest.so` from `conf.c`; links programs against `-latest`.

Control flow: `lib.mk` handles kselftest targets; pattern rules make each C test depend on the shared library and header.

State and persistence: writes binaries and `libatest.so` under `OUTPUT`; installs config files as test assets.

Dependencies/integration: requires ALSA development package and libasound. Integrates all ALSA selftests with shared config lookup code.

Risks and test signals: build hard-fails if ALSA pkg-config metadata is missing. Runtime rpath assumes tests can locate `libatest.so` in the execution directory.
