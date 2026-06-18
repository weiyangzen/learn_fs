# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/mad.c

## Purpose
`mad.c` is the HFI1 management datagram implementation. It handles OPA and legacy IB Subnet Management Agent and Performance Management Agent requests, reports and mutates port state, validates management keys and P_Keys, manages traps, exposes counters and error info, programs fabric-management tables, and applies congestion-control state.

## Important APIs, types, and functions
- Trap support centers on `struct trap_node`, `send_trap()`, `check_and_add_trap()`, `hfi1_handle_trap_timer()`, `subn_handle_opa_trap_repress()`, and event helpers such as `hfi1_bad_pkey()`, `hfi1_cap_mask_chg()`, `hfi1_sys_guid_chg()`, and `hfi1_node_desc_chg()`.
- SMA validation and dispatch use `check_mkey()`, `process_subn_opa()`, `process_subn()`, `subn_get_opa_sma()`, `subn_set_opa_sma()`, aggregate handlers, and length/status helpers.
- Port state and configuration are served by `__subn_get_opa_portinfo()`, `__subn_set_opa_portinfo()`, `__subn_get_opa_psi()`, `__subn_set_opa_psi()`, transition tables, and `set_port_states()`.
- Fabric tables include P_Key table handlers, SL-to-SC, SC-to-SL, SC-to-VL transmit/non-transmit mappings, buffer control, VL arbitration, cable info, LED info, and link-width/speed setters.
- PMA support includes OPA port status, data counters, error counters, error info, clear operations, and legacy IB `PortCounters` and `PortCountersExt` compatibility.
- Congestion control uses `struct cc_state`, `apply_cc_state()`, congestion setting/table get/set handlers, and HFI congestion log extraction.
- `hfi1_process_mad()` is the exported entry point called by the MAD core and dispatches by base version to OPA or IB processing.

## Control flow
Incoming MADs enter `hfi1_process_mad()`. OPA packets go through `hfi1_process_opa_mad()`, which selects the limited management P_Key for replies, identifies local SMPs, applies local SMP P_Key checks, and dispatches subnet or performance classes. IB-format packets go through the smaller `hfi1_process_ib_mad()` path, which supports legacy node info and performance counters.

OPA subnet processing copies the request to the response buffer, validates class version and M_Key, sets the response length to the OPA SMP header, and dispatches GET, SET, TRAP_REPRESS, or pass-through response methods. GET usually clears the SMP data area before filling the requested attribute. SET mutates driver or hardware state, then often calls the corresponding GET handler to return current state. Aggregate GET/SET iterates nested attributes inside one SMP and flags segment-level errors.

PMA processing validates class version and attribute modifiers, checks selected port and VL masks, computes response sizes with flexible-array helpers, reads HFI1 device and port counters, converts transmit-wait counters from TXE cycles to flit times, and clears selected counters on SET clear requests. Trap flow creates notice payloads, queues by priority, rate-limits list length, sends through QP0 via the MAD send agent, and honors trap repress messages.

## State and persistence
The file mutates substantial runtime and hardware state: port LID/LMC, SM LID/SL/AH, M_Key and lease timers, subnet timeout, link width/speed enable masks, link state, partition enforcement and P_Key tables, MTUs per VL, operational VLs, SC/VL/SL tables, buffer-control and VL-arbitration tables, congestion-control shadows, LED override state, counters, and cached LCB read values. Trap state is held in `ibp->rvp.trap_lists`, trap timer, TIDs, and send-agent AH. Congestion-control active state is RCU-protected and replaced atomically after updates.

Most state is not persistent across reset, but many writes program hardware CSRs or fabric-manager tables and therefore affect live link behavior immediately. Several counters are cumulative until explicitly cleared or link-up reset paths run.

## Dependencies and integration points
`mad.c` integrates with the RDMA MAD core, rdmavt port/QP/AH state, HFI1 port and device counter APIs, HFI1 link-state control, P_Key helpers, fabric-manager table helpers, cable EEPROM access, LED override, event dispatch, tracepoints, RCU, timers, spinlocks, and hardware CSR access. It consumes OPA definitions from RDMA headers and local compatibility/header files.

## Risks
- This is a high-blast-radius management path: invalid SET handling can bounce links, change partitioning, alter VL mappings, or clear counters.
- M_Key and P_Key validation are security-sensitive, especially the difference between local SMPs, limited management P_Key, and full management P_Key.
- Flexible response sizes for OPA PMA and aggregate attributes must stay within MAD data buffers.
- Trap lifetime crosses timers, send buffers, repress messages, and port-down cleanup; list and `in_use` state must remain consistent.
- Counter conversion keeps previous samples in `ppd`; link-width changes, counter wraps, and clear operations must keep derived flit counters coherent.
- Congestion-control state uses RCU replacement and spinlock-protected staging; readers and writers must preserve the lock/RCU contract.

## Test signals
- Compile with RDMA MAD, OPA, HFI1, and rdmavt enabled, plus sparse/smatch for endian, bounds, and flexible-array checks.
- Unit or hardware tests should cover M_Key failures, lease timeout, bad P_Key traps, trap repress, port-down trap cleanup, and local versus remote SMP P_Key rules.
- Fabric-manager tests should exercise PortInfo/PSI state transitions, LID/SM changes, MTU/VL changes, P_Key updates with and without limited management P_Key, and SC/VL table restrictions while Armed or Active.
- PMA tests should verify response sizing, selected port/VL masks, counter saturation, clear masks, link-width conversion, A0/BX differences, and legacy IB counter compatibility.
- Congestion tests should validate setting congestion settings and CCT blocks, reading logs, RCU state replacement, and log reset-on-read behavior.
