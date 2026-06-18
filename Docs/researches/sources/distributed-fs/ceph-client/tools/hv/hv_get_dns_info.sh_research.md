<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_get_dns_info.sh -->
# sources/distributed-fs/ceph-client/tools/hv/hv_get_dns_info.sh

Purpose: Example external helper for the Hyper-V KVP daemon to print configured DNS nameserver addresses.

Important APIs/types/functions: Runs `awk '/^nameserver/ { print $2 }' /etc/resolv.conf` and redirects awk stderr to `/dev/null`.

Control flow: The script replaces itself with awk via `exec`; every `nameserver` line emits the second field.

State and persistence: No state is modified. Output is a newline-separated list of resolver addresses.

Dependencies/integration: Depends on `/etc/resolv.conf` semantics and awk. It is installed by the Hyper-V Makefile under `hypervkvpd/hv_get_dns_info`.

Risks/tests: Risks include resolver state managed elsewhere, comments/spacing not handled beyond lines starting exactly with `nameserver`, and no validation of printed addresses. Test signals are resolv.conf fixtures with IPv4/IPv6, leading whitespace, comments, missing file, and daemon consumption of multiple lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/hv/hv_get_dns_info.sh -->
