# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/bpf.go

Purpose: Builds classic BPF bytecode and iptables match fragments for matching VXLAN datagrams by VNI.

Important APIs and functions: `vniMatchBPF` assembles a cBPF program that loads UDP payload offset, reads the VXLAN VNI field at payload offset 4, shifts off reserved bits, compares to the requested VNI, and returns match/no-match. `marshalXTBPF` serializes raw BPF instructions for `iptables -m bpf --bytecode`. `matchVXLAN` returns an iptables argument fragment for UDP destination port and BPF VNI match.

Control flow: BPF assembly panics only if static instructions are invalid. `matchVXLAN` creates a fresh argument slice so callers can append safely.

State and persistence: stateless helper; no kernel mutation itself.

Dependencies and integration points: used by overlay encryption firewall rules to mark outgoing encrypted VXLAN and drop incoming cleartext VXLAN. Depends on `golang.org/x/net/bpf` and iptables bpf match support.

Risks: cBPF depends on Linux payload-offset extension and xt_bpf behavior. VNI values are accepted as uint32 even though VXLAN VNI is 24 bits; callers often mask or validate elsewhere.

Test signals: `bpf_linux_test.go` attaches the program as a raw socket filter, and `bpf_test.go` fuzzes assembly panic safety.
