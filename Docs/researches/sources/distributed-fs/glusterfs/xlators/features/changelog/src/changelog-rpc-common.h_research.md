# sources/distributed-fs/glusterfs/xlators/features/changelog/src/changelog-rpc-common.h

## Purpose
Defines shared RPC program numbers, procedure numbers, common RPC state, and function prototypes for changelog forward and reverse RPC paths.

## APIs, Types, and Functions
Forward procedures are `CHANGELOG_RPC_PROC_NULL` and `CHANGELOG_RPC_PROBE_FILTER` under `CHANGELOG_RPC_PROGNUM` version 1. Reverse procedures are `CHANGELOG_REV_PROC_NULL` and `CHANGELOG_REV_PROC_EVENT` under `CHANGELOG_REV_RPC_PROCNUM` version 1. `NR_ROTT_BUFFS` and `NR_DISPATCHERS` size the event rotating-buffer/dispatcher setup. `changelog_rpc_t` groups an RPC service, client, and socket path. Prototypes cover poller, client init, request submission, invocation, reply submission, server init, and server destroy.

## Control Flow, State, and Persistence
No direct control flow. The constants define the network/RPC ABI between the xlator and libgfchangelog and the default dispatcher topology.

## Dependencies and Integration
Includes `rpcsvc.h`, `rpc-clnt.h`, `gf-event.h`, and generated `changelog-xdr.h`. Used from both source trees, making it a shared contract.

## Risks and Test Signals
Risks include program-number/procedure-number incompatibility, hard-coded dispatcher counts, and ABI drift with generated XDR structures. Test signals are interop between xlator and library built from the same headers plus negative tests for mismatched procedure numbers.
