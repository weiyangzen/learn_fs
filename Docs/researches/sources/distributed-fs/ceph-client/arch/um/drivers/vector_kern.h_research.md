<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.h

Purpose: declares kernel-side data structures and constants for UML vector network devices.

Important APIs/types/functions: constants include `QUEUE_SENDMSG`, `QUEUE_SENDMMSG`, `VECTOR_RX`, `VECTOR_TX`, `VECTOR_BPF`, `VECTOR_QDISC_BYPASS`, `VECTOR_BPF_FLASH`, `ETH_MAX_PACKET`, `ETH_HEADER_OTHER`, and `MAX_FILTER_PROG`. `struct vector_queue` stores mmsg/iov/skb arrays and queue indices/locks/depth. `struct vector_estats` defines ethtool counters. `struct vector_private` is the netdev private state containing NAPI, timer, work item, FDs, queues, IRQs, parsed args, transport callbacks/data, header buffers, state flags, stats, BPF, and trailing user storage. It declares `build_transport_data()`.

Control flow: no executable flow exists here; `vector_kern.c` and `vector_transports.c` use the declarations.

State and persistence: the header defines runtime state layout but owns no instances.

Dependencies and integration points: depends on Linux netdevice/platform/skbuff/socket/list/workqueue/interrupt APIs, atomics, and `vector_user.h`.

Risks: callback fields `form_header` and `verify_header` are transport ABI between transport builders and core RX/TX paths. Queue size and feature flags must match vector core assumptions.

Test signals: compile vector core/transports, open each transport, validate ethtool stat layout, and test vnet-header transport callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_kern.h -->
