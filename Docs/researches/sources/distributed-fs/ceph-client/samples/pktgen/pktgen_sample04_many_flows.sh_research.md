# sources/distributed-fs/ceph-client/samples/pktgen/pktgen_sample04_many_flows.sh

## Purpose

This sample configures pktgen for many concurrent flows. It varies source IP addresses from the `198.18.0.0/15` benchmarking range and uses pktgen `flows`, `flowlen`, and `FLOW_SEQ` to model repeated packets per flow.

## Important APIs, Types, and Functions

Key helper APIs are the pktgen shell wrappers from `functions.sh`. Pktgen attributes include `IPSRC_RND`, `src_min`, `src_max`, `flows`, `flowlen`, `FLOW_SEQ`, `QUEUE_MAP_CPU`, common packet fields, optional `UDPDST_RND`, and optional `UDPCSUM`.

## Control Flow

After common setup, the script defaults destination parameters, `FLOWS=8000`, `FLOWLEN=10`, and rejects `BURST` because burst mode is not supported in this flow-generation mode. It parses the fixed source network, resets pktgen unless appending, configures each selected thread device, randomizes source IPs, sets the flow table size and packets-per-flow, then starts pgctrl and prints per-thread results unless in append mode.

## State and Persistence Behavior

Pktgen's in-kernel flow table and generator configuration hold the runtime state. `FLOW_SEQ` changes packet ordering so `FLOWLEN` packets are sent back-to-back from one flow before advancing. No repository or filesystem state is persisted beyond procfs configuration.

## Dependencies and Integration Points

It depends on pktgen flow support and the helper scripts. Receiver-side RSS, flow hashing, conntrack, routing, and application lookup caches are typical integration targets for the generated workload.

## Risks and Edge Cases

Large flow counts can stress receiver tables and test infrastructure. `FLOWS` is bounded by pktgen's maximum. Burst rejection is explicit, but invalid helper-derived thread ranges still fail through procfs writes.

## Test Signals

Validate via pktgen result output, packet captures showing many source IPs, receiver RSS distribution, and behavior changes when varying `FLOWS` and `FLOWLEN`.
