# sources/cloud-native/moby/daemon/libnetwork/agent.go

## Purpose
Implements libnetwork's cluster agent integration around NetworkDB gossip, service discovery, driver table watches, encryption-key distribution, and swarm-scoped network membership.

## Important APIs, Types, And Functions
`nwAgent` stores `NetworkDB`, bind/advertise/datapath addresses, and cancel functions. Address helpers resolve IPs, hostnames, or interface names. Controller methods `agentSetup`, `agentInit`, `agentJoin`, `agentDriverNotify`, `agentClose`, `handleKeyChange`, `getKeys`, and `getPrimaryKeyTag` manage cluster lifecycle and keys. Network/Endpoint methods join/leave networks, publish/delete driver entries, publish/disable/delete service info, and add/cancel driver watches. `handleEpTableEvent` translates NetworkDB endpoint events into service binding or container name-resolution calls.

## Control Flow
Setup reads cluster provider addresses, initializes NetworkDB if an advertise address exists, registers table watches, notifies global drivers, then joins remote peers. Endpoint publication marshals `EndpointRecord` into `libnetworkEPTable`; deletion either removes the entry or marks it disabled. Watch handlers unmarshal previous/current records, compare semantic equivalence ignoring `ServiceDisabled`, remove stale bindings, and add or disable current bindings.

## State And Persistence
State lives in NetworkDB gossip tables, local controller key slices, driver watch cancel maps, and local DNS/LB binding stores. Key changes update NetworkDB gossip keys and notify datapath drivers.

## Dependencies And Integration Points
Depends on cluster provider, NetworkDB, driver discovery/table APIs, protobuf records, overlay/service binding code, and diagnostic handlers.

## Risks And Test Signals
Key ordering is subtle: primary key is the second Lamport-sorted key and `getKeys` swaps the first two. Endpoint add/delete paths guard sandbox races with service locks. Tests focus on endpoint equivalence and transition actions across create/update/delete/replace events.
