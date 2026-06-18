# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns3/hns3pf/hclge_tm.h

## Purpose
`hclge_tm.h` defines PF traffic-management command payloads, bitfields, defaults, shaper encoding helpers, and public TM APIs. It is the hardware command ABI companion to `hclge_tm.c`.

## Important Types And Constants
- MAC pause and scheduler constants define TX/RX pause enable bits, pause defaults, DWRR/SP masks, max Ethernet rate, legacy PF priority/qset counts, DSCP mapping descriptor count, and TM flush timing.
- Mapping command structs include PG-to-priority, qset-to-priority, queue-to-qset, queue-to-TC, and backpressure-to-qset mapping payloads. Qset id bitfields include an extended high-bit representation for qset ids at or above 1024.
- Weight and scheduler structs define PG, priority, qset, and ETS TC DWRR state plus priority/qset scheduler modes.
- Shaper structs define priority, PG, qset, and port shaper payloads with encoded IR/BS fields, valid flags, and rates. `hclge_tm_set_field()` and `hclge_tm_get_field()` wrap HNAE3 bitfield helpers for shaper encoding.
- Flow-control structs define PFC enable, pause parameter MAC/gap/time payloads, and PFC stats command layout.
- Public prototypes cover scheduler initialization/setup/update, pause/PFC config, PFC stats extraction, qset/port shapers, debug getters, mapping config, flush, and TC reset.

## Control Flow And Integration
Callers use the declared APIs from PF initialization, reset restore, DCB/mqprio configuration, ethtool pause/PFC paths, VF rate limiting, and debugfs. The header keeps the command-payload layout visible to implementation and diagnostic code while forward-declaring `struct hclge_dev` and `struct hclge_vport`.

## State And Risks
The header itself stores no state, but its structs must match firmware descriptor layouts exactly. Bitfield macros are central to qset id conversion and shaper parameter packing; drift from firmware definitions would cause silent misconfiguration. Public APIs assume callers pass valid TC/qset/priority ids and properly initialized `hclge_dev` TM state.

## Test Signals
Build and sparse checks catch layout/prototype drift. Runtime validation should include programming and reading back shapers, scheduler modes, weights, queue/qset mappings, PFC and MAC pause state, and TM flush support across device versions.
