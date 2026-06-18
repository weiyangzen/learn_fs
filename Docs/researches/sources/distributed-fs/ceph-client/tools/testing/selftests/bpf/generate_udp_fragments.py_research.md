# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/generate_udp_fragments.py

Purpose: generator script for deterministic IPv4 and IPv6 fragmented UDP packet byte arrays used by defragmentation tests.

Important APIs and functions: constants mirror `ip_check_defrag.c`; `print_header()`, `print_frags()`, and `print_trailer()` emit C header text; `main()` builds Scapy IPv4/UDP and IPv6/fragment/UDP packets, fragments them, and writes `ip_check_defrag_frags.h`.

Control flow: when run as a script, resolves its directory, opens the target header for writing, builds packets with fixed addresses/ports/message, fragments at fixed sizes, and emits arrays.

State and persistence: overwrites generated header file in the same directory. No runtime state after script exits.

Dependencies and integration points: requires Python 3 and Scapy; generated header is consumed by C defrag tests and must stay synchronized with constants.

Risks: wildcard `from scapy.all import *`; generated output changes if Scapy serialization changes; IPv4 source is `0.0.0.0` to be filled by `IP_HDRINCL`; maintainers must rerun after constant changes.

Test signals: generated `ip_check_defrag_frags.h` contains `frag_*` and `frag6_*` arrays with the magic payload split across fragments.
