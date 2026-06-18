<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-payload-link.sh -->
# sources/cloud-native/ostree/tests/test-payload-link.sh

## Purpose
`test-payload-link.sh` verifies payload-link detection/reporting for commits that can use reflink-like shared payloads.

## Important APIs, Types, And Functions
It probes `cp --reflink=always`, uses `ostree commit`, payload-link output inspection, `assert_streq`, and TAP helpers.

## Control Flow
The script first checks whether the filesystem supports reflinks. If so, it creates files/directories, commits content in a way that should produce payload-link metadata, lists payload links, and asserts exactly one payload-link entry appears.

## State And Persistence
State is temporary files `foo`, `bar`, directory `d`, the repository objects created by commit, and `payload-links.txt`.

## Dependencies And Integration Points
It covers filesystem reflink capability, OSTree commit payload-link generation, and CLI listing of payload links.

## Risks And Test Signals
The test may skip or behave differently on filesystems without reflinks. Passing signals include one and only one payload-link line, indicating duplicate payload detection works without over-reporting.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/test-payload-link.sh -->
