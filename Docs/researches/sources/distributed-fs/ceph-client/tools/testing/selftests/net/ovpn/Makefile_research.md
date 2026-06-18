# sources/distributed-fs/ceph-client/tools/testing/selftests/net/ovpn/Makefile

## Purpose
The OVPN `Makefile` builds and packages the OpenVPN data-channel accelerator selftests. It compiles `ovpn-cli`, declares shell tests, and includes supporting fixtures for the kselftest install/run harness.

## Important variables and build APIs
- `CFLAGS` enables strict warnings, debug symbols, no optimization, and kernel header includes from `KHDR_INCLUDES`.
- `pkg-config` probes `mbedcrypto-3`, `mbedtls-3`, `libnl-3.0`, and `libnl-genl-3.0`, with fallback include and library flags for common distro layouts.
- `TEST_FILES` ships `common.sh`, `data64.key`, the `json` fixture directory, peer tables, and the YNL Python CLI used for notifications.
- `TEST_PROGS` lists the executable shell tests and mode variants.
- `TEST_GEN_FILES := ovpn-cli` tells kselftest infrastructure to build the local C helper.

## Control flow
The Makefile is declarative. After setting compiler/linker inputs and test manifests, it includes `../../lib.mk`, which provides kselftest build, install, and run targets.

## State and persistence
Build output is `ovpn-cli`. Installed or staged tests include the declared fixtures and shell scripts. No runtime state is created by the Makefile itself.

## Dependencies and integration points
The helper requires libnl generic netlink and mbedTLS/mbedcrypto. The tests integrate with `tools/testing/selftests/lib.mk`, kernel headers containing `linux/ovpn.h`, the YNL CLI under `tools/net/ynl/pyynl/cli.py`, and fixture files consumed by `common.sh`.

## Risks and edge cases
Fallback library names may fail on systems using only versioned pkg-config names or nonstandard libnl paths. The test list assumes all referenced scripts and fixture directories are installed together; missing `json`, peer files, or `data64.key` causes runtime failures.

## Test signals
A successful build produces `ovpn-cli`; successful kselftest packaging includes every `TEST_PROGS` script and `TEST_FILES` dependency.
