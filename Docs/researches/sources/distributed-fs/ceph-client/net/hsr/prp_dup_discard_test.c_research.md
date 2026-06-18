## sources/distributed-fs/ceph-client/net/hsr/prp_dup_discard_test.c

Purpose: KUnit suite for PRP duplicate-discard behavior implemented in the HSR frame registry. It builds minimal in-memory `hsr_port`, `hsr_frame_info`, and `hsr_node` objects and verifies sequence bitmap behavior for forwarding, duplicates, timeouts, and out-of-order frames.

Important APIs/types/functions: `build_prp_test_data()` allocates test data, configures `node.seq_port_cnt`, allocates `node.block_buf` based on `hsr_seq_block_size()`, initializes the xarray `seq_blocks` and `seq_out_lock`, connects the frame to source node and receive port, and defaults receive port to `HSR_PT_SLAVE_A`. `check_prp_frame_seen()` and `check_prp_frame_unseen()` inspect sequence blocks and bits. Test cases call exported `prp_register_frame_out()`.

Control flow and state: each test constructs isolated state through KUnit allocators. The duplicate-discard state is maintained in per-node sequence blocks indexed by sequence number. Accepted frames set the appropriate bit; duplicate frames on the opposite LAN should return `1`; expired blocks are aged by manually setting `block->time` before a repeat call.

Dependencies and integration points: depends on KUnit and HSR frame registry internals exported for KUnit via `MODULE_IMPORT_NS("EXPORTED_FOR_KUNIT_TESTING")`. It exercises `hsr_framereg` behavior using definitions from `hsr_main.h`.

Risks: the tests create synthetic objects rather than full netdevices, so they verify frame registry sequencing, not RX handler integration, skb parsing, netlink, or real PRP trailer validation. The timeout test mutates internal block time directly, which is useful but tied to implementation details.

Test signals: suite name `prp_duplicate_discard`; cases cover normal forward, exact duplicate drop, entry timeout clearing old state, out-of-sequence acceptance followed by duplicate drop, and LAN B late duplicate drops.
