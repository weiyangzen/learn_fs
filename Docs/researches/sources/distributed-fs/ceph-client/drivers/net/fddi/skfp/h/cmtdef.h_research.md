# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/cmtdef.h

## Purpose
`cmtdef.h` is the core SMT/CMT definition header. It fixes station sizing constants, event classes and event IDs, PCM/RMT/CFM/ECM state constants, mux/MAC control values, timer conversions, shared protocol structures, prototypes, debug macros, and SMT error identifiers.

## Important APIs, Types, And Functions
Important definitions include `NUMPHYS`, `NUMMACS`, `NUMPATHS`, port IDs (`PA`, `PB`, `PS`), policy bits, `EVENT_*`, `EV_TOKEN()` helpers, all `EC_*`, `CF_*`, `PC_*`, and `RM_*` events, path-test and duplicate-address enums, mux values, `MA_*` commands, entity bit helpers, `struct smt_timer`, `struct mac_parameter`, `struct mac_counter`, `struct s_pcon`, `struct lem_counter`, and `struct s_plc`. It also declares most cross-module functions.

## Control Flow
This header does not execute code, but it defines the control vocabulary for the dispatcher and all SMT state machines. Events are encoded as class/event tokens for timers and queue dispatch. State files such as `ecm.c`, `cfm.c`, PCM, RMT, SMT frame services, and FORMAC code use these constants to coordinate behavior.

## State And Persistence
It declares in-memory state types and constants only. The closest persistence boundary is the MIB/state enum compatibility comments: CFM values must match SMT specifications because they are reported externally in management frames.

## Dependencies And Integration Points
It includes `mbuf.h` and `smtstate.h` under normal builds and prototypes functions from hardware timer, SMT frame, PCM/RMT/CFM/ECM, PLC, FORMAC, PNMI, ESS/SBA, and OS-specific modules. Debug macros integrate with `struct smt_debug`.

## Risks And Edge Cases
Changing numeric event/state constants breaks wire-visible MIB values, dispatcher routing, timer tokens, and array indexing in implementation files. `NUMPHYS > 2` switches on `CONCENTRATOR`, changing structures and trace logic. Many prototypes are conditional and legacy-style; mismatched config macros can hide declarations.

## Test Signals
Build with normal DAS/SAS config, `CONC`/`CONC_II`, `ESS`, `SBA`, debug, and boot/slim variants. Runtime tests should verify queue dispatch by event class, timer token decode, state-machine transitions, debug macro compilation, and panic/error IDs in hardware error paths.
