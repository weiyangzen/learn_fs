# sources/distributed-fs/ceph-client/include/linux/netfilter/nf_conntrack_tftp.h

Purpose: Defines TFTP helper constants, minimal packet header, opcodes, and the optional NAT callback for dynamic data-port expectations.

Important APIs, types, and functions: Exports `TFTP_PORT`, `struct tftphdr`, opcode constants, `nf_nat_tftp_hook_fn`, and RCU pointer `nf_nat_tftp_hook`. Detected source surface: 29 lines; includes `linux/netfilter.h`, `linux/skbuff.h`, `linux/types.h`, `net/netfilter/nf_conntrack_expect.h`; macros `TFTP_OPCODE_ACK`, `TFTP_OPCODE_DATA`, `TFTP_OPCODE_ERROR`, `TFTP_OPCODE_READ`, `TFTP_OPCODE_WRITE`, `TFTP_PORT`, `_NF_CONNTRACK_TFTP_H`; structs `nf_conntrack_expect`, `tftphdr`; enums `ip_conntrack_info`; typedefs none; function-like declarations/helpers `nf_nat_tftp_hook_fn`.

Control flow: The conntrack helper parses read/write requests on UDP port 69, creates expectations for server-selected data ports, and calls the NAT hook when address or port rewriting is required.

State and persistence behavior: The header itself has only the RCU NAT hook; per-flow state is held by conntrack expectations outside the header.

Dependencies and integration points: Depends on netfilter, skb, types, and conntrack expectation support. Integrates with UDP conntrack and NAT helpers.

Risks and test signals: Risks are accepting malformed opcodes, failing to constrain expected data flows, and hook lifetime races. Test RRQ/WRQ, DATA/ACK flows, NAT translation, retransmissions, and invalid opcodes.
