# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_fcs.h

## Purpose
`bfa_fcs.h` is the shared internal interface for Fibre Channel Services in the BR-series driver. It defines FCS trace categories, fabric/lport/vport/rport/FCPIM state-machine events, major runtime structures, helper macros, protected module APIs, and BFAD callback contracts. The file is the type and API spine connecting `bfa_fcs.c`, lport/vport/rport modules, `bfa_fcs_fcpim.c`, BFAD, and lower BFA HAL services.

## Important APIs, Types, And Functions
The header defines service-specific state for name server, state-change notification, management server, FDMI, fabric topology, logical ports, virtual ports, remote ports, rport feature probing, and FCS ITNIM. `struct bfa_fcs_s` holds the FCS root; `struct bfa_fcs_fabric_s` holds base-fabric/vf state; `struct bfa_fcs_lport_s` holds each local port; `struct bfa_fcs_rport_s` holds discovered remote ports; `struct bfa_fcs_itnim_s` holds FCP initiator FC-4 state over an rport.

Externally visible APIs include main lifecycle (`bfa_fcs_attach/init/stop/exit`), VF lookup/listing, fabric module start/stop/link/UF/vport operations, lport lifecycle and discovery helpers, vport lifecycle, rport lookup/create/PRLO/SCN helpers, rport feature helpers, and FCS ITNIM create/delete/online/offline/attribute/stat APIs. BFAD callback declarations define allocation and notification hooks for lports, PBC vports, rports, and ITNIMs.

## Control Flow
The event enums document the expected flow. Fabric moves through create/start/link/FLOGI/auth/online/offline/stop/delete events. Lports react to create/online/offline/delete/stop and own subcomponents for NS, SCN, MS, and FDMI. Vports react to fabric online/offline, FDISC/LOGO responses, retry timers, duplicate WWN, and fabric capacity failures. Rports react to PLOGI, LOGO, PRLO, address changes, SCN, timeout, and FC-4 completion events. FCS ITNIM reacts to rport online, PRLI sent/response/retry, HAL online callback, driver callback, offline, initiator-only remote ports, and delete.

## State And Persistence Behavior
All structures are runtime driver objects. The header shows list-based ownership: fabrics contain vport queues, lports contain rport queues, rports own optional FC-4 role objects, and ITNIMs reference both FCS rports and HAL `bfa_itnim_s` objects. Timers and FCXP wait elements encode asynchronous protocol progress. Stats fields are maintained for UF, fabric/vf, lport, rport, and ITNIM paths. Persistent storage is not defined here; any persistent settings are handled by other modules.

## Dependencies And Integration Points
The file includes BFA common definitions, module state, and FC protocol definitions. It integrates with FCXP allocation through `bfa_fcs_fcxp_alloc()` and wait macros, with BFAD through callback declarations and driver-private pointers, with BFA HAL rport/itnim objects through embedded pointers, and with protocol code through FC WWN, COS, FDMI, ELS, and SCSI/FCP-related types. Many modules rely on the inline getters for WWNs, FCIDs, driver handles, fabric properties, and HAL handles.

## Risks And Edge Cases
The header exposes many state machines whose enum values are implicitly version-sensitive for traces; the comment warns to append only. Because structures are shared across modules, field ownership must remain clear: FCS ITNIM holds protocol negotiation flags while HAL ITNIM handles IO execution. Some comments contain stale names or typos, so maintainers should rely on field usage as well as comments. Several max constants are fixed policy values, such as rport login caps and tentative rport support limits, which can constrain scaling.

## Test Signals
Compile-time tests should catch API drift across FCS, FCPIM, BFAD, and BFA modules. Runtime tests should validate fabric/lport/vport/rport/ITNIM event sequencing, BFAD allocation/free callback pairing, inline getter correctness, FCXP wait allocation paths, and stats visibility. Trace consumers depend on stable enum values, so trace decoding compatibility is a specific regression signal.
