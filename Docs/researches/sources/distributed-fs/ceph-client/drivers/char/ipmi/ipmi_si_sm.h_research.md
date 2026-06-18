<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_sm.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_sm.h

## Purpose
Defines the low-level state-machine contract between the generic IPMI SI policy layer and concrete KCS, SMIC, and BT state machines.

## Important APIs, Types, and Functions
- `struct si_sm_data` is opaque state owned by each state-machine implementation.
- `enum si_sm_result` communicates scheduling outcomes such as immediate call, delayed call, transaction complete, idle, hosed, or attention.
- `struct si_sm_handlers` defines callbacks: `init_data`, `start_transaction`, `get_result`, `event`, `detect`, `cleanup`, and `size`.
- Extern handler tables: `kcs_smi_handlers`, `smic_smi_handlers`, and `bt_smi_handlers`.

## Control Flow
The SI core allocates handler-sized opaque state, calls `init_data()` to bind `si_sm_io` and learn I/O size, uses `start_transaction()` to submit messages, repeatedly calls `event()` under polling or interrupt-driven scheduling, and calls `get_result()` after `SI_SM_TRANSACTION_COMPLETE`.

## State and Persistence
State is intentionally hidden behind `struct si_sm_data`. The contract centralizes result codes and callback meanings so the upper layer can treat KCS, SMIC, and BT uniformly.

## Dependencies and Integration Points
Includes `ipmi_si.h` for `struct si_sm_io` and SI metadata. It is included by low-level state machine C files and by the SI core.

## Risks
The API relies on callback conventions rather than type-enforced ownership rules. A state machine returning the wrong scheduling result can cause busy loops, missed attention, or transaction stalls.

## Test Signals
State-machine unit tests should validate callback return contracts, size/init consistency, error return values for invalid transaction length/state, and `SI_SM_ATTN` behavior when hardware flags asynchronous data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_sm.h -->
