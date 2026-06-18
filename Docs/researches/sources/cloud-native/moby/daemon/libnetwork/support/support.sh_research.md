## sources/cloud-native/moby/daemon/libnetwork/support/support.sh

Purpose: Bash diagnostic script that gathers host, overlay network, namespace, iptables, IPVS, bridge FDB, container networking, and optional SSD consistency data for Docker/libnetwork troubleshooting.

Important functions and options: Parses `-s` to enable SSD checks. Tool paths are overrideable by environment variables (`DOCKER`, `NSENTER`, `BRIDGE`, `IPTABLES`, `IPVSADM`, `IP`, `SSDBIN`, `JQ`). `echo_and_run` echoes commands before executing them. `check_ip_overlap` scans network inspect output for duplicate endpoint/VIP addresses.

Control flow and state: The script prints host iptables tables and routes, iterates overlay networks plus `ingress_sbox`, finds matching netns files in `/var/run/docker/netns`, dumps namespace addresses/routes/neighbors/bridges/iptables/IPVS, then iterates all containers and inspects network settings. Counters track processed networks, running containers, and IP overlaps, ending with a summary.

Dependencies and integration points: Integrates with Docker CLI, Linux network namespaces via `nsenter`, iptables, `iproute2`, bridge tooling, IPVS, jq JSON parsing, and optional SSD binary. It uses `docker network inspect --verbose` when available.

Risks: Requires high privileges and host namespace access. Some shell constructs are fragile: command output is evaluated in `echo_and_run`, unquoted variables may break on spaces, and `nspath[0]` array syntax is used around Docker inspect output. It prints potentially sensitive container labels/environment/network data.

Test signals: No automated tests; diagnostic value depends on command availability and host topology.
