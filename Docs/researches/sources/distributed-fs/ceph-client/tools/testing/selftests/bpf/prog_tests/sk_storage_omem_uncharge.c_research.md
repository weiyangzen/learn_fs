<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_omem_uncharge.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_omem_uncharge.c

Purpose: this selftest verifies that socket-local BPF storage memory accounting is uncharged when a socket is closed after storage updates. It specifically checks that updating a `BPF_MAP_TYPE_SK_STORAGE` entry and then closing the socket triggers the BPF-side close path to observe the expected cookie and zero outstanding `omem`.

Important APIs/types/functions: `test_sk_storage_omem_uncharge()` is the only test entry. It uses `sk_storage_omem_uncharge__open_and_load()`, `bpf_map__fd()`, `socket(AF_INET6, SOCK_STREAM, 0)`, `getsockopt(SO_COOKIE)`, `bpf_map_update_elem()`, and `sk_storage_omem_uncharge__attach()`. The skeleton BSS fields `cookie`, `cookie_found`, and `omem` are the test contract with the BPF program.

Control flow: the test opens and loads the skeleton, obtains the storage map FD, creates an unbound IPv6 stream socket, stores the socket cookie in skeleton BSS, inserts storage value `0`, updates it to `0xdeadbeef`, attaches the BPF program, closes the socket, and checks `cookie_found == 2` plus `omem == 0`.

State and persistence: state is limited to one socket FD, one sk_storage map entry keyed by that FD, and BSS counters in the skeleton. No namespace or durable file state is created. Cleanup destroys the skeleton and closes the socket if the close-trigger path was not reached.

Dependencies: requires kernel sk_storage support, socket cookies, libbpf skeleton support, BPF program attachment for the skeleton's close/tracing hook, and normal selftest assertion macros.

Integration points: this is a targeted regression test for interaction between socket lifetime, sk_storage map replacement, socket memory accounting, and BPF program observation during socket close. It is intentionally independent of address binding and network namespaces.

Risks: the test assumes the BPF program will observe exactly two cookie matches across the inserted and replaced storage state. If the BPF side changes accounting points, `cookie_found` may be brittle. A failure before attach leaves the accounting behavior untested, although cleanup still closes the socket.

Test signals: pass criteria are successful map updates, successful skeleton attach, close of the socket, `cookie_found` equal to `2`, and `omem` equal to `0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sk_storage_omem_uncharge.c -->
