# sources/distributed-fs/ceph-client/samples/bpf/run_cookie_uid_helper_example.sh

Purpose: wrapper for the cookie/UID helper sample that handles BPF filesystem pinning and iptables cleanup.

Important APIs/types/functions: invokes `cookie_uid_helper_example`, manages a pinned object path, installs/removes iptables `xt_bpf` rule, and forwards `-t` or `-s` test modes.

Control flow: prepares a pin path, runs the C sample with the chosen option, and on exit removes the iptables rule and pinned BPF object.

State and persistence: temporarily creates bpffs pins and iptables OUTPUT rules.

Dependencies and integration: requires bpffs, iptables with `-m bpf --object-pinned`, root privileges, and the compiled C sample.

Risks: cleanup depends on shell exit handling; interrupted or failed runs can leave firewall rules. Host iptables policy may affect unrelated traffic during the test.

Test signals: run both cookie and traffic modes, then verify no matching iptables rule or pinned object remains.
