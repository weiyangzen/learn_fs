# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/wc.c

## Purpose
`wc.c` probes whether mlx5 BlueFlame write-combining doorbells are usable on the platform. It builds a temporary CQ/SQ pair, posts NOP WQEs through a BF register using write-combining style MMIO copies, polls the CQ, and records `mdev->wc_state` as supported or unsupported.

## Important APIs, Types, and Functions
Local types `struct mlx5_wc_cq` and `struct mlx5_wc_sq` combine mlx5 work queues, core CQ/SQ IDs, BlueFlame register allocation, producer/consumer counters, and control resources. Key helpers are `mlx5_wc_create_cq()`, `create_wc_cq()`, `mlx5_wc_create_sq()`, `create_wc_sq()`, `mlx5_iowrite64_copy()`, `mlx5_wc_post_nop()`, `mlx5_wc_poll_cq()`, `mlx5_core_test_wc()`, and exported `mlx5_wc_support_get()`.

## Control Flow and State
`mlx5_wc_support_get()` first checks BlueFlame and SQ capabilities, then serializes the one-time test with `mdev->wc_state_lock`. SF devices reuse the parent device's state. The test allocates a BFREG, creates a CQ, creates a cyclic SQ, posts 254 unsignaled NOPs and one signaled NOP, polls for a CQE for up to 100 ms, and marks support according to the returned WQE counter. Destroy paths release SQ, CQ, BFREG, WQ buffers, and doorbell records in reverse order.

State is deliberately persistent for the device lifetime in `mdev->wc_state`, so later callers avoid re-running the hardware test. Posting uses DMA and CPU ordering barriers: WQE contents are written before the doorbell record, the doorbell record before the MMIO BF copy, and CQ doorbell updates before new CQEs are enabled.

## Dependencies and Integration Points
The file depends on mlx5 CQ/SQ creation commands, the common WQ helpers in `wq.c`, BlueFlame register allocation, clock timestamp-format helpers, PCI/MMIO I/O APIs, polling helpers, and optional ARM64 kernel-mode NEON for a 64-byte SIMD store path.

## Risks and Test Signals
Risks include leaking temporary CQ/SQ resources on partial failure, misdetecting write-combining due to CQ polling timeout, wrong CQE stride handling on 128-byte CQEs, architecture-specific SIMD store bugs, and incorrect state sharing between SFs and parents. Test signals include build coverage with and without ARM64 NEON, mlx5 probe on BF-capable and non-BF hardware, SF WC state propagation, fault injection for CQ/SQ/BFREG allocation failures, and logs showing either supported state or the warning that write combining is unsupported.
