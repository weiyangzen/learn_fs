# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/iou-zcrx.py

Purpose: Python orchestrator for the `iou-zcrx` C helper, covering single queue, RSS context, one-shot receive, and large chunk modes.

Important APIs/functions: `mp_clear_wait()`, `create_rss_ctx()`, `set_flow_rule()`, `set_flow_rule_rss()`, `single()`, `rss()`, `test_zcrx()`, `test_zcrx_oneshot()`, `test_zcrx_large_chunks()`, `NetDrvEpEnv`, `ksft_variants`, `bkg`, `cmd`, `ethtool`, `wait_port_listen`, and `defer`.

Control flow: Setup functions configure memory-provider state, RSS contexts, and ntuple flow rules to steer traffic. `test_zcrx()` starts the local server helper on a queue, waits for the port, and runs the remote client helper. One-shot mode repeats receive submission behavior. Large chunk mode probes/uses larger receive buffers and skips when unsupported.

State and persistence: Mutates ethtool ntuple rules, RSS contexts, and memory-provider state; cleanup uses `defer()` and `mp_clear_wait()`.

Dependencies and integration points: Requires compiled `iou-zcrx`, remote endpoint, ethtool RSS/ntuple support, io_uring ZCRX kernel support, and queue IDs.

Risks and test signals: Failures identify orchestration, flow steering, memory-provider clearing, RSS context, one-shot receive, or large chunk support regressions.
