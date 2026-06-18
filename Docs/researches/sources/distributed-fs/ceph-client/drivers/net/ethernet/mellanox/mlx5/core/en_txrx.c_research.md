# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en_txrx.c

Purpose: NAPI and CQ event glue for mlx5e channels. It polls TX, RX, XDP, AF_XDP, internal control SQs, kTLS resync work, adaptive interrupt moderation, CQ arming, and completion/error event callbacks.

Important APIs and functions: `mlx5e_napi_poll` is the channel NAPI poll function. `mlx5e_trigger_irq` posts a NOP on an ICOSQ to force an interrupt/NAPI cycle. `mlx5e_completion_event` schedules NAPI for a CQ and increments event counters. `mlx5e_cq_error_event` logs CQ errors. Internal helpers update DIM samples for TX/RX and handle AF_XDP need-wakeup semantics.

Control flow: NAPI first polls regular TX CQs for each traffic class, then optional QoS SQ CQs under RCU. With nonzero budget it polls XDP CQs, AF_XDP RX, normal RX, ICOSQ/AICOSQ completions, kTLS resync, refills RX WQs, handles AF_XDP TX/RX posting, and decides whether the poll remains busy. If busy on a CPU outside the channel affinity mask, it forces a follow-up IRQ. On completion it arms all relevant CQs and updates DIM for TX and RX queues.

State and dependencies: state includes NAPI budget/work_done, channel stats, CQ event counters, DIM state bits, QoS SQ RCU array, XSK need-wakeup flags, ICOSQ pending bits, and RX WQ fill levels. It depends on `en/txrx.h`, RX/TX polling implementations, XDP/XSK helpers, IRQ/NAPI core, RCU, and kTLS acceleration.

Risks and test signals: risks are budget accounting mistakes, missed CQ rearm, AF_XDP need-wakeup races, QoS SQ RCU misuse, affinity-change live lock, and XDP/RX starvation. Test signals include mixed TX/RX load, budget zero polling, QoS queue creation/removal under traffic, AF_XDP zero-copy wakeups, XDP redirect/TX, kTLS RX resync, DIM transitions, and CPU affinity changes.
