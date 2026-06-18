# sources/distributed-fs/ceph-client/drivers/ata/pata_parport/pata_parport.h

## Purpose
Defines the private ABI between the `pata_parport` core and individual parallel-port IDE protocol modules.

## Important APIs, Types, And Functions
`struct pi_adapter` stores per-adapter device state, selected protocol, I/O base, mode, delay, unit, saved register values, protocol-private storage, and parport device pointer. `struct pi_protocol` defines callbacks for register access, block transfer, connect/disconnect, tests, logging, optional init/release, module owner, driver object, and SCSI template. Macros `w0/r0` through `w4l/r4l` wrap port IO with optional delay. `module_pata_parport_driver()` registers a protocol with the core.

## Control Flow
The header has no runtime control flow but dictates callback order used by the core: optional init, probe/test, connect, read/write register and block operations, disconnect, optional release, and unregister.

## State And Persistence
The state contract is explicit in `pi_adapter`; protocol modules may use `private` for small cached values but the core owns allocation and release.

## Dependencies And Integration Points
Includes libata and exports prototypes for `pata_parport_register_driver()` and `pata_parport_unregister_driver()`.

## Risks And Edge Cases
Callbacks are synchronous and called while the parport may be claimed. Protocols must preserve saved registers and respect delay. Raw port macros assume valid I/O ranges and architecture support for in/out instructions.

## Test Signals
Build all protocol modules, modpost exported symbol resolution, protocol registration/unregistration, delay behavior, and static checking of callback table completeness.
