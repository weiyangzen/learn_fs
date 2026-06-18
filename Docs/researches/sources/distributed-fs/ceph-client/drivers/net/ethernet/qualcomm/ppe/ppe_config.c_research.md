<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.c

## Purpose
`ppe_config.c` applies the IPQ9574 PPE hardware initialization policy. It configures buffer management, queue management, scheduler arbitration, per-port scheduler resources, queue destinations, service codes, counters, RSS hash generation, queue-to-ring maps, and initial bridge/VSI behavior.

## Important APIs, Types, and Functions
- Local config types describe BM port thresholds, QM queue thresholds, scheduler directions, BM/QM scheduler entries, port scheduler loops, and per-port resource ranges.
- Static tables define IPQ9574 buffer group limits, BM port configs, QM queue configs, BM/QM scheduler order, port scheduler nodes, and scheduler resources.
- Exported APIs: `ppe_queue_scheduler_set()`, `ppe_queue_ucast_base_set()`, `ppe_queue_ucast_offset_pri_set()`, `ppe_queue_ucast_offset_hash_set()`, `ppe_port_resource_get()`, `ppe_sc_config_set()`, `ppe_counter_enable_set()`, `ppe_rss_hash_config_set()`, `ppe_ring_queue_map_set()`, and `ppe_hw_config()`.
- Internal stages: `ppe_config_bm()`, `ppe_config_qm()`, `ppe_config_scheduler()`, `ppe_queue_dest_init()`, `ppe_servcode_init()`, `ppe_port_config_init()`, `ppe_rss_hash_init()`, `ppe_queues_to_ring_init()`, and `ppe_bridge_init()`.

## Control Flow
`ppe_hw_config()` runs a fixed sequence and stops on first regmap error. BM config sets shared buffer group 0 and per-port flow-control thresholds. QM config sets queue group buffer limits, initializes unicast/multicast queues, enables enqueue/dequeue, and enables queue counters. Scheduler config programs BM and QM arbitration tables, then loops per-port scheduler node templates through L0/L1 mapping helpers. Queue destination init assigns per-port unicast bases, priority offsets, and zeroed hash offsets. Service code init configures EDMA bypass service code 1. Port config enables counters and MTU/MRU actions. RSS init seeds IPv4/IPv6 hash registers using `get_random_u32()`. Ring init maps CPU-port queues to EDMA ring 0. Bridge init constrains initial forwarding to CPU port 0 until higher-level switch/VSI support attaches ports.

## State and Persistence
All durable state is written into PPE hardware tables through regmap. The only randomized state is the RSS hash seed generated during initialization. No software state is retained beyond the `ppe_device` reference and static configuration tables.

## Dependencies and Integration Points
The file depends heavily on `ppe_regs.h` field definitions and regmap bulk/update APIs. It is invoked by `qcom_ppe_probe()` and provides exported configuration helpers likely intended for later Ethernet/switchdev/EDMA integration.

## Risks and Edge Cases
- Static resource tables assume `ppe_dev->num_ports == 8` plus one reserved resource entry; incorrect port count can index unexpected resource rows.
- `ppe_port_resource_get()` allows `port == num_ports` for the reserved row but rejects only greater values.
- Queue/multicast table addressing for multicast queues uses queue IDs directly against multicast table base, so hardware table numbering assumptions are critical.
- RSS seed is intentionally random, making exact register state nondeterministic across boots.
- Many helpers trust caller-provided IDs and bitmaps; invalid queue/profile/service values can program outside intended hardware ranges if not validated by callers.
- Regmap errors abort config, but partial hardware programming is not rolled back.

## Test Signals
Regression tests should validate probe-time `ppe_hw_config()` on IPQ9574, regmap write ranges, per-port resource outputs, RSS register programming for IPv4/IPv6, service-code bitmap encoding, queue-to-ring bitmaps, and debugfs counters increasing after traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/ppe/ppe_config.c -->
