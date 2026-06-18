# sources/distributed-fs/coda/coda-src/venus/mgrp.cc

## Purpose
This file implements Venus multicast group (`mgrpent`) behavior for replicated server sets. It creates and tears down RPC2 multicast groups, manages per-server RPC handles for a VSG, reconciles multi-RPC return codes, chooses dominant/primary hosts, and records which replicas accepted mutating operations. It is a core communication layer between higher-level replicated volume/file code and Vice servers.

## Important APIs, Types, and Functions
`Mgrp_Wait()` and `Mgrp_Signal()` coordinate waiters looking for available multicast groups. `RepOpCommCtxt::RepOpCommCtxt()` initializes active handles, hosts, retcodes, primary host, multicast info pointer, and dying flags; `AnyReturned()` scans live hosts for a return code. `mgrpent::CreateMember()`, `KillMember()`, `GetHostSet()`, and `PutHostSet()` synchronize the current RPC2 group membership with the VSG host set. `CheckResult()`, `CheckNonMutating()`, `CheckCOP1()`, and `CheckReintegrate()` translate Vice/RPC2 results and collapse per-replica outcomes into Venus-level codes such as `EASYRESOLVE`, `ESYNRESOLVE`, `ERETRY`, and `EALREADY`. `RVVCheck()`, `PickDH()`, `DHCheck()`, and `GetPrimaryHost()` enforce version-vector and dominant-host policy.

## Control Flow
Callers obtain an mgrp, then `GetHostSet()` creates missing RPC2 connections via `srvent::Connect()`, adds them to the RPC2 mgrp, removes stale members, and ensures a primary host exists. After a multi-RPC, callers use one of the `Check*` routines. Those first invoke `CheckResult()` to convert server-specific failures and kill timed-out/retry hosts, then attempt unanimity under increasingly broad masks for tolerated errors. Mutating COP1 operations additionally populate `UpdateSet` for replicas where the operation succeeded. Dominant-host selection is based on hosts with successful retcodes and valid remote version vectors, with bandwidth used as a tie-breaker.

## State and Persistence Behavior
The file manages transient RPC state only: `rocc` holds live RPC2 handles, host addresses, return codes, primary host, multicast pointer, and dying flags. It does not directly write RVM state, but its `UpdateSet` and resolution decisions determine whether replicated persistent volume state can be trusted, retried, or must be resolved. Destructor cleanup can notify servers with `ViceDisconnectFS`, remove active members, unbind handles, and delete the RPC2 multicast group.

## Dependencies and Integration Points
It depends on RPC2 multicast APIs, VSG/server abstractions (`vsgent`, `srvent`), Vice error codes, version-vector helpers (`InitVV`, `VV_Check`, `FPrintVV` via callers), mariner logging, and Venus private error conventions. `fsobj`, `repvol`, `reintvol`, `volent`, `ClientModifyLog`, and `cmlent` are friends because they need direct access to the replicated operation context for multi-server operations.

## Risks and Test Signals
High-risk areas are return-code masking, bitmask constants, member lifetime while mgrp references are active, primary-host invalidation, and translation of retry/authentication failures. Tests should exercise unanimous success/failure, partial timeouts, mixed maskable/non-maskable errors, `EINCOMPATIBLE` handling for normal COP1 versus reintegration, dominant-host version-vector disagreement, all-members-lost behavior, and cleanup of dying members after an mgrp is put.
