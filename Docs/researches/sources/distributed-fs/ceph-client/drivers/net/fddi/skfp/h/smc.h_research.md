# sources/distributed-fs/ceph-client/drivers/net/fddi/skfp/h/smc.h

## Purpose
`smc.h` is the central context header for the SysKonnect SMT driver. It pulls target, protocol, MIB, hardware, OS, and ESS/SBA headers together and defines `struct s_smc`, the shared state block used by all SMT and hardware modules.

## Important APIs, Types, And Functions
It defines event queue structures, module state structs (`s_ecm`, `s_rmt`, `s_cfm`, `s_pcm`, `s_phy`, `s_timer`, `s_srf`, `s_srf_evc`, `smt_values`, `smt_config`, optional debug), ring-status bits and `RS_SET`/`RS_CLEAR`, station attach types (`SMT_DAS`, `SMT_SAS`, `SMT_NAC`), and the aggregate `struct s_smc`. It also declares board and interrupt entry points such as `init_board()`, `init_fplus()`, `mac*_irq()`, `plc*_irq()`, and `timer_irq()`.

## Control Flow
The header itself has no code, but its structures define the runtime graph. State machines share one `struct s_smc`; events move through `struct s_queue`; timers use `struct s_timer`; hardware and OS state must be the first fields because default initialization zeroes everything after `hw`.

## State And Persistence
`struct s_smc` contains all runtime state: OS and hardware state, configuration constants, SMT values, ECM/RMT/CFM/PCM/PHY state, event queue, timers, SRF data, MIB, and optional ESS/SBA/debug state. Nothing here is disk-persistent, but much of the MIB is externally reported and must remain coherent.

## Dependencies And Integration Points
It conditionally includes `osdef1st.h`, `smt.h`, `cmtdef.h`, `fddimib.h`, `targethw.h`, `targetos.h`, and `sba.h`. Every C file in this subset includes it directly or indirectly.

## Risks And Edge Cases
The field-order comment for `os` and `hw` is a hard initialization contract. `NUMPHYS` changes affect array sizes, trace bitmaps, event queue size, and MIB serialization. Ring status macros invoke callbacks as side effects. Conditional compilation can materially change structure layout.

## Test Signals
Initialization/default reset of `struct s_smc`, build variants for PCI/TAG_MODE/SUPERNET_3/ESS/CONCENTRATOR/debug, event queue wraparound, timer list behavior, ring-status callbacks, MIB pointer setup for each PHY, and state-machine interactions sharing one context.
