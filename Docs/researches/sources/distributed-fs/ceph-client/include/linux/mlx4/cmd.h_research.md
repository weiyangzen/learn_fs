# sources/distributed-fs/ceph-client/include/linux/mlx4/cmd.h

## Purpose
Defines the mlx4 firmware command namespace, command mailbox format, invocation wrappers, VF configuration APIs, checksum/offload configuration, and command-channel helpers.

## Important APIs/Types
Opcode enums cover initialization, HCA/port, memory translation, EQ/CQ/SRQ/QP state, multicast, Ethernet, virtualization, flow steering, debug, statistics, and congestion control. It also defines timeout classes, mailbox size/alignment, set-port and MAD demux modifiers, native/wrapped modes, RX checksum mode bits, `mlx4_config_dev_params`, congestion-control enums, `mlx4_cmd_mailbox`, and wrappers `mlx4_cmd`, `mlx4_cmd_box`, and `mlx4_cmd_imm` around `__mlx4_cmd`.

## Control Flow
Callers prepare immediate parameters or DMA mailboxes, select opcode/modifiers, and submit through `__mlx4_cmd`. Mailbox commands pass DMA addresses; immediate commands copy scalar output. Wrapped/native mode controls SR-IOV command mediation.

## State And Persistence
Commands mutate firmware/device state: resources, ports, queues, steering, VF policy, counters, and offloads. Mailboxes are transient DMA buffers.

## Dependencies And Integration Points
Depends on DMA mapping, if_link VF structs, mlx4 device definitions, and netdevice types. Integrates with mlx4 core, mlx4_en, mlx4_ib, SR-IOV management, ethtool stats, and error handling.

## Risks
Wrong op/modifier combinations, mailbox alignment or endian errors, timeout misuse, native/wrapped confusion, and VF operations aimed at the wrong port/slave.

## Test Signals
Command status mapping, mailbox DMA allocation, HCA/port lifecycle, QP/CQ/SRQ transitions, VF config, stats retrieval, checksum/offload retrieval, internal-error completion wakeups, and SR-IOV mediation.
