<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix_test.go -->
## sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix_test.go

Purpose: Unix tests for sandbox DNS option handling.

Important APIs/functions: `getResolvConfOptions` reads and parses the sandbox resolv.conf; `TestDNSOptions` exercises `setupDNS`, `startResolver`, and `rebuildDNS`.

Control flow: first sandbox starts resolver, writes DNS config, and verifies default embedded resolver option `ndots:0`. It then sets `ndots:5` and confirms setup/rebuild preserves it. A second sandbox verifies explicit `ndots:0` remains, while invalid values such as `ndots:foobar` and `ndots:-1` fall back to valid `ndots:0`.

State and persistence: uses temporary controller data dir and sandbox resolv.conf file paths. Cleanup deletes sandboxes.

Dependencies and integration points: uses internal resolvconf parser and libnetwork controller creation.

Risks and test signals: protects user DNS option precedence and resolver option sanitization. It does not exercise user-modified hash behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/sandbox_dns_unix_test.go -->
