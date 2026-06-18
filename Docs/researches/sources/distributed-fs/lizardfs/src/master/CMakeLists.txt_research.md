# sources/distributed-fs/lizardfs/src/master/CMakeLists.txt

Purpose: build configuration for the master library, unit tests, and `mfsmaster` executable.

Important APIs/functions: sets include directory and definitions, `collect_sources(MASTER)`, conditionally removes Berkeley DB name storage when DB is unavailable, builds `master`, links optional Judy/DB libraries, creates/links unit tests, builds `mfsmaster` from `${MAIN_SRC}`, and configures/installs `mfsrestoremaster`.

Control flow: CMake configures target sources based on detected dependencies, then sets install rules for the daemon and helper script.

State and persistence: build/install configuration only.

Dependencies and integration: links `master` with `mfscommon` and `ADDITIONAL_LIBS`; links `mfsmaster` with PAM and optional systemd libraries; uses `APPNAME=mfsmaster` and example subdir definitions consumed by `main.cc`.

Risks: `collect_sources` and conditional source removal require dependency detection to stay in sync with actual code. Missing DB support changes available name-storage behavior.

Test signals: `create_unittest(master ${MASTER_TESTS})` and `link_unittest(master master mfscommon)` wire master tests into the build.
