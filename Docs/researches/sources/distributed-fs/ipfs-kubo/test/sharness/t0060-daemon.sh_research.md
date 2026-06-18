## sources/distributed-fs/ipfs-kubo/test/sharness/t0060-daemon.sh

Purpose: broad daemon command coverage for initialization, runtime addresses, API/gateway access, version/help output, transport security negotiation, streaming output, stdin pipe behavior, failure cleanup, and file descriptor limits.

Important control flow: creates a Pebble init config, runs daemon `--init` with profiles, verifies config materialization, sets resource manager env vars, launches a normal daemon, checks PeerID, swarm local/listen addresses, allowed-origin API/gateway requests, daemon output text, version/deps/help output, socat-based TLS/Noise/plaintext transport probes, streaming command output, manual daemon kill, daemon startup with stdin pipe, cleanup after failed start, and raised fd limit with `hang-fds`.

State and dependencies: creates `.ipfs`, daemon logs, API/gateway files, network listeners, and process state. Depends on `pollEndpoint`, curl, socat prereq, hang-fds, ulimit behavior, and daemon helper functions.

Risks: high platform and timing sensitivity, especially fd limits, socat probes, and process cleanup. Test signals are readiness, expected daemon output, security handshake acceptance/rejection, successful streaming output, and absence of daemon errors.
