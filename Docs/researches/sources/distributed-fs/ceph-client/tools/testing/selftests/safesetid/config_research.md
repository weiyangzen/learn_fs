<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/config

## Purpose

Config fragment for SafeSetID selftests.

## Important APIs, Types, and Functions

Requests CONFIG_SECURITY=y and CONFIG_SECURITYFS=y; SafeSetID itself is implied by the test requirements even if not listed here.

## Control Flow and Integration

Used by kselftest config merge/check tooling.

## State and Persistence Behavior

Static metadata only.

## Dependencies and Integration Points

Kernel security framework and securityfs.

## Risks and Edge Cases

The C test still requires CONFIG_SAFESETID; this short fragment can be insufficient by itself.

## Test Signals

Config validation plus successful access to /sys/kernel/security/safesetid policy files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/safesetid/config -->
