# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/ocelot/psfp.sh

Purpose: Tests Per-Stream Filtering and Policing gate behavior on Ocelot hardware using TC flower, ETF/txtime scheduling, and time-sensitive traffic.

Important APIs/functions: Sources `tc_common.sh`, `lib.sh`, and `tsn_lib.sh`. `PSFP` returns the hardware chain id. Helpers create PSFP chains, inspect hardware filter drops, set up bridge/VLAN forwarding, configure txtime with `mqprio` and `etf`, and debug incorrect packet receipt/drop.

Control flow: Setup builds host and switch topology, attaches a PSFP chain on ingress, creates an Ocelot bridge with VLAN filtering, configures traffic classes and ETF for the stream priority, and then runs gate in-band and out-of-band tests. `run_test` sends isochronous traffic with expected receive counts and checks drops.

State and persistence: Mutates TC qdiscs/filters, bridge/VLAN state, txtime/ETF scheduling, and hardware PSFP entries. Cleanup tears down txtime, chains, bridge, hosts, and interfaces.

Dependencies and integration: Requires Ocelot hardware with PSFP offload, `tc` flower offload, ETF/mqprio qdiscs, time synchronization good enough for scheduled packets, and forwarding TSN helpers.

Risks: Strongly time-sensitive; scheduler jitter and clock drift can create false failures. Hardware offload counters must be available. Debug helpers assume packet capture buffers from forwarding libs.

Test signals: PASS means packets inside allowed gate windows are received, packets outside windows are dropped with hardware filter counters increasing, and no unexpected packets appear in debug captures.
