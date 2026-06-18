## sources/distributed-fs/ipfs-kubo/test/sharness/t0061-daemon-opts.sh

Purpose: focused daemon option tests for transport encryption disabling, offline gateway behavior, and invalid DHT option errors.

Important control flow: starts daemon with `--disable-transport-encryption` and, when `SOCAT` is available, verifies plaintext transport works; starts an offline daemon and confirms gateway access still works for locally available content; then asserts daemon startup fails for bad DHT options and deprecated/unsupported `supernode` mode with informative output.

State and dependencies: creates temporary repo/daemon state and network listeners. Depends on socat for plaintext probe, gateway/API readiness helpers, and exact daemon error text.

Risks: security-option behavior is sensitive; plaintext should only be enabled when explicitly requested. Error-message assertions may need updates if CLI wording changes. Test signals are plaintext availability under the flag, offline gateway success, and nonzero exits for invalid DHT modes.
