<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_user.c

## Purpose
`xdp_adjust_tail_user.c` loads and attaches the XDP ICMP packet-too-big sample, optionally updates its maximum packet size, and polls the ICMP response counter.

## Important APIs, Types, And Functions
Important functions are `int_exit()`, `poll_stats()`, `usage()`, and `main()`. It uses `bpf_object__open_file()`, `bpf_program__set_type()`, `bpf_object__load()`, `bpf_object__find_map_fd_by_name()`, `bpf_map_update_elem()`, `bpf_xdp_attach()`, `bpf_xdp_query_id()`, `bpf_xdp_detach()`, and `bpf_prog_get_info_by_fd()`.

## Control Flow
The program parses interface, timeout, packet size, skb/native/force flags, loads `<argv[0]>_kern.o`, sets the program type to XDP, optionally updates the `.data` map variable `max_pcktsz`, resolves `icmpcnt`, installs signal handlers, attaches XDP, records the program id, and polls `icmpcnt` every two seconds until timeout or signal.

## State And Persistence
State includes the attached XDP program, its program id, the `icmpcnt` map, and optional `.data` global value. Signal cleanup detaches only if the current program id still matches the one it attached.

## Dependencies And Integration Points
It depends on libbpf, XDP attach support on the selected interface, optional driver/native mode, and the companion kernel object.

## Risks And Edge Cases
The `.data` map name `xdp_adju.data` is object-name dependent and can change with build naming. If another program replaces the XDP program, cleanup intentionally does not detach it. Missing interface or mode support fails attach.

## Test Signals
Successful attach prints periodic `icmp "packet too big" sent` counts. Signal exit should remove the program if it is still the attached id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_adjust_tail_user.c -->
