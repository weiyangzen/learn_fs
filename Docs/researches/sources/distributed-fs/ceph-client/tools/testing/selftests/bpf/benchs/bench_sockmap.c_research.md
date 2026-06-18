# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/benchs/bench_sockmap.c

Purpose: benchmarks sockmap/sk_msg forwarding and pass-through modes by moving deterministic data across two loopback TCP socket pairs and measuring producer, BPF, and receiver throughput.

Important APIs and functions: mode macros classify RX stream-verdict and TX sk_msg variants. `create_sockets()` builds `c1/p1` and `c2/p2` TCP pairs from one listener. `setup_rx_sockmap()` attaches stream parser/verdict/pass programs and populates `sock_map_rx`; `setup_tx_sockmap()` attaches sk_msg verdict/pass and populates `sock_map_tx`. `producer()` writes a repeated data file with `sendfile`; `consumer()` reads/forwards and verifies byte pattern. Argp options select RX/TX mode, strparser packet size, delayed consumer, and bounded producer duration.

Control flow: validation requires two consumers, one producer, and CPU affinity. Setup loads the skeleton, creates sockets, attaches the selected BPF path, and populates sock maps. The producer sends from the endpoint required by the selected mode. Consumer 0 reads final data from `c2`; consumer 1 is only relevant for RX normal proxy mode.

State and persistence: `ctx` owns skeleton, sockets, counters, mode, data sizes, and timing knobs. Counters are atomically swapped each measurement. Temporary file data persists for the producer lifetime.

Dependencies and integration points: integrates with `bench_sockmap_prog.skel.h`, libbpf `bpf_prog_attach`, BPF sockmap map updates, TCP loopback sockets, `sendfile`, and `bench.h`.

Risks: mode setup is subtle because ingress/egress endpoints differ; nonblocking sendfile can spin on `EAGAIN/ENOMEM/ENOBUFS`; data verification exits on the first mismatch; `set_non_block()` names its boolean inversely to behavior, which can confuse maintainers; resource cleanup only runs on setup error.

Test signals: progress reports Send, BPF, and Receive MB/s plus call rates. Correctness signals include byte-pattern verification and BPF `process_byte` matching transported data.
