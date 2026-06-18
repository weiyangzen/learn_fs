# sources/distributed-fs/ceph-client/tools/testing/selftests/net/can/test_raw_filter.c

Purpose: this kselftest harness validates CAN RAW socket filter semantics for standard-frame, extended-frame, and remote-transmission-request flag matching. For each variant it installs one `struct can_filter`, sends four frames carrying the same standard id with all EFF/RTR flag combinations, and verifies only the expected frames are received.

Important APIs and types: the test uses `PF_CAN`, `SOCK_RAW`, `CAN_RAW`, `struct sockaddr_can`, `struct can_frame`, `struct can_filter`, `CAN_RAW_FILTER`, `CAN_RAW_RECV_OWN_MSGS`, `SIOCGIFINDEX`, `CAN_SFF_MASK`, `CAN_EFF_MASK`, `CAN_EFF_FLAG`, `CAN_RTR_FLAG`, and the kselftest harness fixture/variant macros. The global `CANIF` is populated from the `CANIF` environment variable and identifies the interface under test.

Control flow: `main` requires `CANIF`, copies it into the global buffer, and calls `test_harness_run`. Fixture setup opens a CAN RAW socket, looks up the interface index, enables reception of frames sent by the same socket, and binds to the interface. `send_can_frames` sends four one-byte frames tagged with the current testcase id in `data[0]`. Each variant defines a filter id, mask, expected receive count, and ordered expected flags. `TEST_F(can_filters, test_filter)` installs the filter, sends frames, then loops one extra receive attempt: expected frames must arrive before a 50 ms `select` timeout, and the extra iteration must time out.

State and persistence: state is per-socket and per-variant. No files are written. Kernel state includes the bound CAN socket and its raw filter. The receive-own-message option deliberately loops transmitted frames back into the same socket to make the test self-contained on vcan.

Dependencies and integration points: the shell wrapper provides a vcan or physical CAN interface and exports `CANIF`. The Makefile builds this binary as `TEST_GEN_FILES`. It depends on kselftest harness headers and CAN kernel support.

Risks and test signals: ordering is assumed to match the order of writes that pass the filter. The 50 ms timeout can be fragile on slow or overloaded systems. `setsockopt` return values for `CAN_RAW_RECV_OWN_MSGS` and `CAN_RAW_FILTER` are not asserted, so failures there can show up as later receive mismatches. Strong signals are exact expected receive counts, id equality after masking with `CAN_SFF_MASK`, correct testcase byte, and flag equality after excluding `CAN_ERR_MASK`.
