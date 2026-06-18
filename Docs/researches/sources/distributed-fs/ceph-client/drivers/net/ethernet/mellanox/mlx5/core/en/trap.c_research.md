# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/trap.c

Purpose: implements devlink trap receive support for mlx5e. It opens a dedicated RQ/CQ/NAPI queue and direct TIR, programs trap steering rules for selected generic traps, and tears the queue down when traps return to drop action.

Important APIs and types: internal helpers include `mlx5e_trap_napi_poll`, trap RQ init/open/close, direct RQ TIR creation, parameter build, trap open/close/activate/deactivate, action trap/drop handlers, and per-trap apply logic. Public functions are `mlx5e_close_trap`, `mlx5e_deactivate_trap`, `mlx5e_handle_trap_event`, and `mlx5e_apply_traps`.

Control flow: opening a trap allocates `struct mlx5e_trap` on the CPU-local node, builds cyclic RQ params, adds NAPI, opens CQ/RQ, creates an inline direct TIR pointing at the trap RQ, enables NAPI and activates the RQ. Trap action handling lazily opens the queue, then installs VLAN or DMAC trap rules with the trap TIR number. Drop action removes the matching trap rule and deletes the queue when no active devlink traps remain. Runtime NAPI polling polls RX CQ, reposts WQEs, completes NAPI when idle, and arms CQ.

State and persistence: `priv->en_trap` points to the active trap context. The trap owns RQ, TIR, NAPI, params, CQ/RQ params, stats pointer, DMA device, netdev, and mkey. Devlink stores configured trap actions; this file applies them when the interface is open.

Dependencies and integration points: TX/RX helpers, RX params, TIR builder, mlx5e flow-steering trap rule helpers, devlink trap APIs, NAPI, RQ/CQ open/close, and netdev locking.

Risks and test signals: failures during lazy queue open must unwind NAPI/RQ/TIR correctly. Trap events while interface is down intentionally do nothing and rely on later open. Test trap-to-drop transitions, two active traps sharing one queue, unknown trap id/action rejection, interface down/up action replay, NAPI polling under trapped traffic, and resource cleanup after partial open failure.
