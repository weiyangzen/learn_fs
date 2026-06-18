# sources/distributed-fs/openafs/src/WINNT/afsd/cm.h

## Purpose
`cm.h` is a foundational Windows cache-manager header. In this subset it mainly establishes pthread mode, imports RX/VLDB/AFS interfaces and cache-manager errors, defines common cache-manager operation flags, volume-type indexes, the default callback port, and a shared lock hierarchy used across AFSD modules.

## Important APIs, Types, And Constants
Operation flags include creation, case folding, exclusive create, symlink following, 8.3-name restriction, mount-point suppression, directory search, path checking, no-probe cell lookup, and DFS referral handling. Volume indexes `RWVOL`, `ROVOL`, and `BACKVOL` are used as array indexes in volume structures. Lock hierarchy constants assign numeric ordering to redirector, SMB, scache, daemon, buffer, volume, user, cell, server, callback, DNLC, freelance, ACL, EACCES, token, and syscfg locks.

## Control Flow, State, And Integration
The header has no executable control flow or storage, but it affects lock initialization and ordering in files such as `cm_aclent.c`, where `cm_aclLock` uses `LOCK_HIERARCHY_ACL_GLOBAL`. Its flags are consumed by cache-manager lookup, cell, and volume operations throughout the Windows AFSD tree.

## Risks And Test Signals
The main risk is lock-order drift: changing hierarchy values can introduce deadlocks or false lock-order assertions. Flag values are ABI-like within the cache-manager code and must remain compatible with callers. Test signals are compile coverage, lock-order assertion tests, callback-port behavior, and path/namei operations that combine flags such as casefold, no-probe, and DFS referral.
