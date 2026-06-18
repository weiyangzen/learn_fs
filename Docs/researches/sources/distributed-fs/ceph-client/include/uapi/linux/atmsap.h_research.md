<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmsap.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/atmsap.h

## Purpose
Defines ATM Service Access Point addressing fields for BLLI/BHLI negotiation in ATM signaling.

## Important APIs, Types, And Functions
Exports layer-2, layer-3, high-layer, mode, terminal, and multiplexing constants. `struct atm_blli` describes low-layer protocol info, `struct atm_bhli` high-layer info, `struct atm_sap` groups one BHLI plus up to three BLLIs, and `blli_in_use` tests whether a BLLI is populated.

## Control Flow
Userspace or signaling daemons populate SAP fields before SVC setup/listen. The kernel and atmsigd include these fields in signaling messages and matching logic.

## State And Persistence
SAP data is per socket/call signaling state and persists for the call/listen lifetime.

## Dependencies And Integration Points
Depends on ATM API alignment. Integrates with `atm.h`, `atmsvc.h`, atmsigd, and ATM UNI signaling.

## Risks And Edge Cases
Optional fields encoded as zero, max BLLI count, protocol-specific union interpretation, and HLI length bounds must be respected.

## Test Signals
SVC setup/listen with varied SAPs, BLLI/BHLI matching tests, omitted optional fields, maximum HLI/BLLI counts, and ABI alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/atmsap.h -->
