# sources/distributed-fs/ceph-client/include/linux/atm_tcp.h

## Purpose
Declares driver-specific operations for the ATMTCP virtual ATM driver.

## Important APIs, Types, And Functions
`struct atm_tcp_ops` provides `attach()`, `create_persistent()`, `remove_persistent()`, and module owner fields. The global `atm_tcp_ops` is exported for driver-specific utilities and users. It also imports the UAPI ATMTCP definitions.

## Control Flow, State, And Persistence
The global ops table routes attach and persistent-interface management to the active ATMTCP implementation. Persistent interface state is owned by that driver, not by the header.

## Dependencies And Integration Points
Depends on UAPI ATMTCP definitions and forward-declared `atm_vcc` and `module`. Integrates with ATM VCC setup, ATMTCP driver module ownership, and management utilities.

## Risks And Test Signals
An uninitialized or stale ops table can route calls into absent modules. Tests should cover attach failure, persistent interface create/remove, module reference ownership, and UAPI command compatibility.
