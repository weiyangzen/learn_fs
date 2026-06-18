# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/cpsw_priv.c

## Purpose
`cpsw_priv.c` contains shared CPSW implementation used by both driver front ends: interrupt control, NAPI polling, TX completion, RX VLAN reconstruction, common hardware initialization, hardware timestamp programming, CPDMA resource splitting, TX rate limiting, traffic-control offloads, XDP/page_pool management, and clsflower policer offload.

## Important APIs, Types, And Functions
It defines exported function pointer `cpsw_slave_index`, set by the active front-end driver. Interrupt/data path exports include `cpsw_intr_enable()`, `cpsw_intr_disable()`, `cpsw_tx_handler()`, `cpsw_tx_interrupt()`, `cpsw_rx_interrupt()`, `cpsw_misc_interrupt()`, `cpsw_tx_mq_poll()`, `cpsw_tx_poll()`, `cpsw_rx_mq_poll()`, and `cpsw_rx_poll()`. Initialization and recovery include `cpsw_init_common()`, `cpsw_soft_reset()`, `cpsw_set_slave_mac()`, `cpsw_ndo_tx_timeout()`, `cpsw_need_resplit()`, and `cpsw_split_res()`. Offload and data features include hardware timestamp get/set, `cpsw_ndo_set_tx_maxrate()`, `cpsw_ndo_setup_tc()`, CBS/MQPRIO/clsflower resume helpers, XDP RXQ creation/destruction, `cpsw_ndo_bpf()`, `cpsw_xdp_tx_frame()`, and `cpsw_run_xdp()`.

## Control Flow
Interrupt handlers mask wrapper interrupts, acknowledge CPDMA EOI, optionally disable broken AM33xx IRQ lines, and schedule NAPI. NAPI polls either a single channel or all active CPDMA channels and reenables wrapper IRQ bits when under budget. TX completion distinguishes skb tokens from tagged XDP frame tokens, timestamps skb TX completions, frees resources, wakes stopped queues, and updates stats. Common init reads CPSW version, chooses register offsets, initializes slave register/sliver objects, creates ALE, configures CPDMA parameters, and creates CPTS. XDP setup creates shared page pools per RX channel, registers each netdev RXQ with page_pool memory model, runs BPF programs in RX callbacks, handles PASS/TX/REDIRECT/DROP/ABORTED, and transmits XDP frames through CPDMA.

## State And Persistence
Shared state includes CPDMA controller/channels, NAPI budgets and channel weights, page pools, per-netdev XDP programs and RXQ registrations, CPTS flags, QoS shaper configuration, MQPRIO state, clsflower broadcast/multicast rate-limit cookies, and hardware registers. `cpsw_split_res()` persists TX/RX budgets and CPDMA channel weights based on link speed and configured channel rates. Timestamp enablement persists in per-port flags and slave registers.

## Dependencies And Integration Points
This file binds CPSW to `davinci_cpdma`, `cpsw_ale`, `cpsw_sl`, `cpts`, phylib, runtime PM, page_pool, XDP/BPF, TC qdisc and clsflower APIs, netdev queues, VLAN RX helpers, and kernel tracing for XDP exceptions. Front-end drivers call these routines from netdev operations, probe, open/stop, ethtool, and switchdev restore paths.

## Risks
`cpsw_slave_index` must be initialized before helpers that index slaves; wrong semantics between legacy and switchdev drivers would target the wrong port. CPDMA/page_pool/XDP lifetimes are tightly coupled to interface open/close and channel/ring changes. XDP redirect is flushed per packet because RX queue ownership can change by source port; batching would be wrong here. Rate and shaper calculations depend on current link speed and can reject or misproportion budgets if speed is unknown or changes. Hardware timestamp support excludes version 4, and source filtering expects MAC timestamping in switch mode. TC clsflower only supports broadcast or multicast destination policers in packets per second, not byte-rate policers.

## Test Signals
Test IRQ/NAPI behavior on normal and AM33xx quirk platforms, TX timeout recovery, multi-channel RX/TX, ethtool channel/ring changes, XDP attach/detach/pass/drop/tx/redirect, PTP timestamp configuration and packet stamping, CBS/MQPRIO offload and resume after link reset, TX maxrate distribution, clsflower broadcast/multicast policer add/delete/resume, and suspend/resume with active offloads.
