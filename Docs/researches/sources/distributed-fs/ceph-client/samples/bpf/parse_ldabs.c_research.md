# sources/distributed-fs/ceph-client/samples/bpf/parse_ldabs.c

Purpose: packet parser sample using legacy absolute load helpers/macros.

Important APIs/types/functions: `ip_is_fragment` and `SEC("ldabs") int handle_ingress(struct __sk_buff *skb)`. Includes `bpf_legacy.h` for `load_byte`/`load_half` style access.

Control flow: reads packet protocol/header fields through absolute loads, checks IPv4 fragmentation, and returns a classifier verdict for selected UDP traffic such as pktgen default port.

State and persistence: stateless per packet.

Dependencies and integration: built as a BPF object by the sample Makefile and usable with tc/socket parser tests.

Risks: absolute loads are legacy and less flexible than direct packet access. Header offsets must be correct and packet truncation handling depends on helper behavior.

Test signals: attach to a packet path and verify it accepts/drops or classifies expected UDP/IP packets without verifier errors.
