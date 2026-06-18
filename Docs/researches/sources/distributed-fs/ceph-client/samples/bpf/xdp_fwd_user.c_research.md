<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_user.c

## Purpose
`xdp_fwd_user.c` loads, attaches, detaches, and configures the XDP forwarding sample across one or more interfaces.

## Important APIs, Types, And Functions
Key functions are `do_attach()`, `do_detach()`, `usage()`, and `main()`. It uses `bpf_xdp_attach()`, `bpf_xdp_query_id()`, `bpf_prog_get_fd_by_id()`, `bpf_prog_get_info_by_fd()`, `bpf_xdp_detach()`, `bpf_map_update_elem()`, and libbpf object/program/map APIs.

## Control Flow
The program parses detach, skb, force, and direct flags. In attach mode, it loads `<argv[0]>_kern.o`, selects `xdp_fwd` or `xdp_fwd_direct`, finds `xdp_tx_ports`, attaches the program to each interface, and writes each ifindex into the devmap. In detach mode, it checks the currently attached program name matches the expected app program before detaching with `old_prog_fd`.

## State And Persistence
Attach mode leaves XDP programs attached and devmap entries populated until detached or process exit tears down non-pinned maps. Detach mode only removes matching attached programs; map cleanup is noted as TODO.

## Dependencies And Integration Points
It depends on libbpf, XDP driver or skb mode, devmap lookup support in the kernel verifier, and interface names/ifindexes. It integrates with kernel FIB and the companion XDP program.

## Risks And Edge Cases
Program name checks derive from the selected section name plus `_prog`, so naming drift breaks detach. The object is not kept open after process exit unless map/program lifetimes are held by attachment, so map persistence depends on kernel link ownership. Generic mode lacks some devmap xmit stats.

## Test Signals
Attach should succeed for each interface and populate `xdp_tx_ports`; forwarding traffic should traverse XDP. Detach should refuse to remove unrelated XDP programs and remove matching ones.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_fwd_user.c -->
