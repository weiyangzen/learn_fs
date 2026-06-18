# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/fddimib.h

## Purpose
`fddimib.h` defines the in-memory FDDI SMT MIB. It provides standard SMT, MAC, PATH, and PORT attributes plus private ESS/SBA and SysKonnect counters used by state machines, frame services, and management interfaces.

## Important APIs, Types, And Functions
It defines MIB scalar typedefs (`Counter`, `TimeStamp`, `Timer`, `SMTEnum`, `SMTFlag`), path and PMD enums, `SetCountType`, and `struct fddi_mib`. The MIB contains station identity/config/status, MAC array `m[NUMMACS]`, path array `a[NUMPATHS]`, port array `p[NUMPHYS]`, and private counters. It also defines statistic OIDs such as `SMT_OID_CF_STATE`, `SMT_OID_RMT_STATE`, and private ECF/PMF/RDF OIDs.

## Control Flow
The header has no code. CFM writes path/current placement/status fields, ECM writes ECM state and bypass flags, FORMAC updates MAC timers and counters, ESS writes SBA payload/overhead, and SMT/PMF code serializes these fields into management frames.

## State And Persistence
The `struct fddi_mib` instance inside `struct s_smc` is the driver’s authoritative runtime management state. It is not persisted to disk, but many fields mirror hardware state and are exposed externally through SMT frames or OS management APIs.

## Dependencies And Integration Points
It depends on `struct fddi_addr`, `struct smt_sid`, and sizing macros from `cmtdef.h`. It is included by `smc.h` and reached by nearly every SMT and hardware module.

## Risks And Edge Cases
Field units vary: FDDI timers often use 80 ns units, ESS payload uses bytes per 8000 bytes/s, and overhead uses bytes per `T_NEG`. Some fields are private shadows rather than directly standards-visible. Array sizes are compile-time, so concentrator builds alter structure footprint and serialization assumptions.

## Test Signals
Verify default MIB initialization, state updates from CFM/ECM/RMT/PCM, MAC counter wrap accounting, ESS payload/overhead reporting, SMT/PMF get/set serialization, OID lookup correctness, and multi-port builds with larger `NUMPHYS`.
