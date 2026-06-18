# sources/distributed-fs/ceph-client/tools/testing/selftests/net/forwarding/Makefile

## Purpose
The forwarding `Makefile` enumerates the shell programs, support files, generated binaries, and include dependencies that make up the networking forwarding selftests. It is declarative glue for the kselftest build/install harness rather than executable test logic.

## Important APIs, Functions, and Types
Key make variables are `TEST_PROGS`, `TEST_FILES`, `TEST_GEN_PROGS`, and `TEST_INCLUDES`. `TEST_PROGS` lists runnable forwarding scenarios, including bridge, VXLAN, GRE/IPIP, router, tc, scheduler, mirroring, and nexthop tests. `TEST_FILES` lists shared shell libraries and sample configuration files copied with the tests. `TEST_GEN_PROGS := ipmr` declares a generated helper binary. `TEST_INCLUDES` pulls shell libraries from `../lib/sh/*.sh` and `../lib.sh`. The file includes `../../lib.mk`, which supplies standard kselftest build, install, and run rules.

## Control Flow
Make processing is simple: variable lists are expanded and then interpreted by `lib.mk`. There are no custom rules in this file. The trailing comments mark the end of each variable block and help avoid accidentally appending later content to long backslash-continued lists.

## State and Persistence
The Makefile itself does not create runtime state. Through `lib.mk`, it influences build outputs for `TEST_GEN_PROGS` and install/copy behavior for scripts and libraries. Its main persistent effect is determining which test files are visible to kselftest automation.

## Dependencies and Integration Points
This file is an integration point between individual forwarding shell tests and the top-level kselftest infrastructure. The bridge files in this subset are listed in `TEST_PROGS`, while common harness files such as `lib.sh`, `devlink_lib.sh`, `tc_common.sh`, and tunnel libraries are listed in `TEST_FILES`. External dependencies are not declared here; each shell test performs its own feature checks.

## Risks
The long continuation lists are easy to break by missing a backslash or placing content after the `# end` comments. Adding a test script without listing it in `TEST_PROGS` prevents normal kselftest discovery. Removing a library from `TEST_FILES` can cause installed test trees to fail even when in-tree runs work. The Makefile does not encode per-test prerequisites, so scheduling systems must rely on scripts to skip unsupported environments.

## Test Signals
The Makefile has no direct pass/fail signals. Its correctness is reflected by kselftest being able to build generated helpers, install all required support files, and discover/run the listed forwarding scripts.
