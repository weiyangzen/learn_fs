<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull.sh -->
## sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull.sh

Purpose: intended HTTP/direct pull regression test, but currently exits immediately with status 0 due to a FIXME.

Important APIs/functions: inactive body would archive the host repo, serve it over HTTP, pull into a bare-user repo, corrupt content to verify fsck marks commits partial, retry pull, test pull-local across a bind mount, and verify metadata xattrs are not copied.

Control flow/state: active control flow is only `exit 0`; no state is created. Inactive code would use tempdirs, webserver, bind mounts, and repo mutations.

Dependencies/integration: if re-enabled, requires webserver support, mount permissions, xattr tools, and host repo access.

Risks/test signals: currently provides no coverage by design. The test signal is skip-like success, so regressions in the inactive scenarios are not caught.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/nondestructive/itest-pull.sh -->
