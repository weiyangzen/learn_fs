# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_cmd.c

## Purpose
Implements device command submission plumbing for legacy FIFO and newer command-buffer managers. It initializes and tears down FIFO state, reserves/commits command space, pings the host, emits fences and dummy queries, and reports whether 3D/command submission is supported by the virtual device.

## Important APIs, Types, And Functions
- `vmw_supports_3d()` checks SVGA capabilities, GBOBJECTS/MOB support, FIFO hardware version, and display-unit constraints.
- `vmw_fifo_create()` initializes FIFO registers, allocates static bounce storage, and records FIFO capabilities.
- `vmw_fifo_wait()`, `vmw_fifo_wait_noirq()`, and `vmw_fifo_is_full()` wait for FIFO space with IRQ or polling paths.
- `vmw_local_fifo_reserve()` reserves FIFO bytes in place or uses static/dynamic bounce buffers.
- `vmw_local_fifo_commit()` copies bounce data if needed, advances `NEXT_CMD`, clears `RESERVED`, and pings the host.
- `vmw_cmd_ctx_reserve()`, `vmw_cmd_commit()`, `vmw_cmd_commit_flush()`, and `vmw_cmd_flush()` abstract command-buffer versus FIFO submission.
- `vmw_cmd_send_fence()` emits SVGA fences or falls back to marker-based waiting.

## Control Flow
Initialization writes FIFO min/max/next/stop/busy registers and enables `CONFIG_DONE`. Reserve chooses command buffers when `dev_priv->cman` exists; otherwise it only allows non-context FIFO commands. FIFO reserve serializes with `fifo_mutex`, verifies size, waits for space, and either returns FIFO memory or a bounce buffer. Commit finalizes reserved bytes, handles wraparound copying, updates FIFO registers under `rwsem`, pings the host, and unlocks.

## State, Persistence, Dependencies, And Integration
State is in `struct vmw_fifo_state`: static/dynamic buffers, reserved size, bounce flag, mutex/rwsem, and capability bits. Dependencies include SVGA registers/FIFO memory, wait queues, IRQ waiters, command-buffer manager APIs, TTM BO placement for dummy query memory, and vmwgfx fence/query code. All command emitters use these reserve/commit wrappers.

## Risks And Test Signals
Risks include FIFO wraparound errors, stuck FIFO timeouts, bounce-buffer leaks, issuing context commands without command buffers, and fence fallback sequencing bugs. Test signals include FIFO full waits with and without IRQMASK, reservations at end-of-ring, large dynamic bounce submissions, command-buffer and FIFO mode parity, fence seqno wrap avoidance, dummy query emission for legacy and MOB paths, and SVGA v3 command-buffer capability gating.
