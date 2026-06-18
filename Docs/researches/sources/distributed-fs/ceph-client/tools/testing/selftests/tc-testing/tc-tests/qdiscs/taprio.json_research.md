# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/tc-tests/qdiscs/taprio.json

## Purpose
Defines 14 TDC cases for `taprio`. It tests multiqueue creation, multiple schedule entries, `txtime-delay`, valid delete, class show, single-queue rejection, too-short intervals/cycle times, invalid cycle time, child-qdisc grafting restrictions, CBS graft behavior under software/offloaded taprio, and class dump after explicit child delete.

## Important APIs, Types, and Functions
The cases drive `tc qdisc add|del|show` and child qdisc graft operations for time-aware priority scheduling. Options include traffic-class maps, queue maps, `sched-entry`, cycle timing, offload flags, and `txtime-delay`.

## Control Flow
Setup creates single- or multiqueue devices. Valid cases add taprio and verify display/class output. Negative cases attempt invalid timing or forbidden child placement. Graft cases add `cbs` beneath taprio classes and verify dump behavior before cleanup.

## State and Persistence Behavior
Taprio state includes gate schedules, traffic-class queue mapping, cycle timing, offload mode, and child qdisc references. All state is kernel-resident and must be deleted to restore the test device.

## Dependencies and Integration Points
Depends on `sch_taprio`, `sch_cbs`, multiqueue devices, optional offload-capable/netdevsim behavior, `tc`, and namespace setup. It integrates with qdisc timing validation, class grafting, and offload/software paths.

## Risks and Edge Cases
Timing thresholds and offload support are hardware/kernel dependent. Child qdisc graft behavior is subtle because offloaded and software taprio have different constraints. Exact class dump output can change with default child qdisc handling.

## Test Signals
Signals include valid taprio display for multiqueue schedules, expected rejection of invalid timing/single-queue cases, correct child graft accept/reject behavior, and stable class dumps after child deletion.
