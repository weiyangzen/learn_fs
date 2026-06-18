# sources/distributed-fs/ceph-client/include/linux/mlx5/qp.h

## Purpose
This header centralizes mlx5 queue pair and work queue element definitions. It provides QP state/type constants, send WQE segment layouts, address vector structures, memory registration/protection-signature descriptors, data-segment formats, debug hooks, and small helpers used by mlx5 core, RDMA, Ethernet, storage offload, and packet-processing paths.

## Important APIs, Types, And Data
- QP constants include terminate scatter-list lkey, signature WQE size, DIF/protection masks, block signature flags, WQE block sizes, DS units, max WQE size, receive/send doorbell indexes, and inline/check flags.
- `enum mlx5_qp_optpar` defines modify-QP optional parameter bits such as alternate path, RRE/RAE/RWE, PKey, QKey, RNR timeout/retry, primary path, retry count, LAG affinity, SRQ/CQ bindings, DC fields, and counter set id.
- `enum mlx5_qp_state` defines reset/init/RTR/RTS/SQ error/SQD/error/draining/suspended states.
- QP service types include RC, UC, UD, XRC, MLX, DCI/DCT, special QP0/QP1, raw transport, sniffer, UMR, PTP, and max sentinel.
- WQE layout structs include FMR, control, Ethernet, XRC, masked atomic, datagram, remote address, atomic, data, UMR control, PSV get/set/check, signature, inline, block signature format, MTT/KLM/KSM, stride blocks, flow update, and header modify argument update segments.
- `struct mlx5_base_av`, `struct mlx5_av`, and `struct mlx5_ib_ah` represent address vectors and RDMA address handles.
- `struct mlx5_core_qp` embeds `mlx5_core_rsc_common` first for resource tracking, an event callback, QPN, debug handle, process id, and UID.
- `struct mlx5_core_dct` wraps a core QP and drained completion.
- `mlx5_debug_qp_add()` and `mlx5_debug_qp_remove()` register debug visibility.
- `mlx5_qp_type_str()` and `mlx5_qp_state_str()` convert transport/state values to strings.
- `mlx5_get_qp_default_ts()` selects default versus free-running timestamp format based on RoCE or general SQ timestamp capabilities.

## Control Flow
The header defines data consumed by WQE builders and QP state-machine code. Callers assemble control and payload segments in hardware order, ring doorbells elsewhere, and receive completion/error events through device queues. QP lifecycle logic outside this header uses state and optional-parameter enums to drive modify commands. Inline helpers only perform local switch-based string conversion or capability checks for timestamp format.

## State And Persistence
Hardware QP state, WQEs, PSNs, counters, and memory-key references are stored in device queues and firmware contexts. `struct mlx5_core_qp` stores software identity and callback state for a tracked QP resource. WQE segment contents are transient descriptors in send queues. Debug registration can persist while the QP exists.

## Dependencies And Integration Points
The header includes `linux/mlx5/device.h` and `linux/mlx5/driver.h`, uses RDMA core types such as `struct ib_ah`, and depends on endian fixed-width types. It integrates with mlx5 command code, RDMA verbs providers, Ethernet SQ builders, storage integrity offloads, UMR/mkey management, MACsec/IPsec metadata, and resource tracking/debugfs.

## Risks
All WQE layouts are hardware ABI and endian sensitive. Incorrect DS counts, inline lengths, masks, or segment ordering can produce device syndromes or memory corruption. `mlx5_ib_ah` assumes `struct ib_ah` embedding for `container_of`. `mlx5_get_qp_default_ts()` depends on accurate capability reporting and RoCE state. Large comments around signature/DIF constants indicate cross-feature coupling with storage integrity and UMR WQE sizing.

## Test Signals
Build tests should cover RDMA and Ethernet configurations. Runtime signals include QP create/modify transitions across states, WQE posting for send, RDMA read/write, atomic, UMR, inline, and checksum offload paths; debug QP registration visibility; timestamp format behavior with and without RoCE; and fault injection for malformed WQEs or invalid QP state transitions.
