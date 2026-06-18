# sources/distributed-fs/ceph-client/include/net/smc.h

## Purpose
This header exposes shared SMC socket and device-facing definitions for Shared Memory Communications over RDMA/ISM, plus optional BPF handshake-control hooks.

## Important APIs, Types, And Functions
`SMC_MAX_PNETID_LEN` sizes PNET identifiers. `struct smc_hashinfo` stores a lock and hlist hash table. `struct smcd_gid` carries ISM GID values. `struct smcd_dev` describes an ISM device: DIBS device pointer, connection array, VLAN list, event workqueue, PNET id and ownership flag, link-group list/lock/count, deletion waitqueue, and going-away flag. `struct smc_hs_ctrl` registers named handshake-control callbacks for SYN and SYN-ACK option decisions, with inheritable flags. `smc_call_hsbpf()` invokes configured callbacks under RCU when BPF control is enabled, otherwise returns the initial value.

## Control Flow
TCP handshake paths can call `smc_call_hsbpf()` before emitting or responding to SMC options. SMC device management uses `smcd_dev` to coordinate connections, VLANs, events, link groups, and teardown.

## State And Persistence
Persistent state includes per-net handshake controller pointers, SMC hash tables, and long-lived ISM device objects with locks, workqueues, and atomic counters.

## Dependencies And Integration Points
It depends on device, spinlock, waitqueue, DIBS, TCP sock, inet request sock, RCU, and optional `CONFIG_SMC_HS_CTRL_BPF`. It integrates with SMC-R/SMC-D connection setup and TCP option negotiation.

## Risks And Test Signals
Risks include RCU callback lifetime, device teardown races, PNET id ownership mistakes, SYN/SYN-ACK policy mismatches, and BPF-disabled behavior drift. Test signals include SMC option negotiation, BPF handshake control, ISM device removal, VLAN/link-group cleanup, and per-net controller inheritance.
