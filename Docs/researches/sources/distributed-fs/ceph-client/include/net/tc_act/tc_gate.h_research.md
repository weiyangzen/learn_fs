<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_gate.h -->
# sources/distributed-fs/ceph-client/include/net/tc_act/tc_gate.h

Purpose: Defines the TC gate action state for time-aware packet gating schedules.

Important APIs/types/functions: `struct action_gate_entry` is a compact exported schedule entry. `struct tcfg_gate_entry` is the internal list node with index, gate state, interval, IPV, and max octets. `struct tcf_gate_params` stores priority, base time, cycle time, extension, flags, clock id, entry count, entry list, and RCU head. `struct tcf_gate` embeds `tc_action` and runtime state: current gate status, close time, octet counters, next entry, hrtimer, and timekeeping offset. Accessors read locked params for priority, base/cycle times, entry count, and `tcf_gate_get_list()` copies the schedule list to an allocated array.

Control flow: Configuration installs a schedule list. Runtime hrtimer advances entries, opens/closes the gate, tracks max octets, and action execution allows or blocks packets according to current gate status.

State and persistence behavior: Schedule params are RCU-replaced but accessed here through the action lock. Runtime gate status, timers, current octets, and next entry mutate continuously while traffic and timer callbacks run.

Dependencies/integration points: Depends on `act_api.h`, TC gate UAPI, hrtimers, and timekeeping. Integrated with time-sensitive networking qdisc/action flows.

Risks: Entry count/list mismatch causes `tcf_gate_get_list()` to fail. Timer, lock, and RCU interactions are subtle. Allocating the exported list with GFP_ATOMIC can fail under pressure.

Test signals: Schedule validation, base-time/cycle-time timer behavior, max-octet enforcement, list dump correctness, action replace/delete while timer active, and clock-id coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_act/tc_gate.h -->
