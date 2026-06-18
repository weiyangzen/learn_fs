# `sources/distributed-fs/ceph-client/include/linux/usb/tcpm.h`

## Purpose

`tcpm.h` defines the Type-C Port Manager interface between low-level Type-C/PD port controllers and the generic TCPM policy engine. It describes CC status, polarity, transmit types/status, mux flags, TCPC callback vector, registration APIs, and event notification functions.

## Important APIs, Types, and Constants

- `enum typec_cc_status` defines open, Ra, Rd, and Rp current levels; `SINK_TX_NG` and `SINK_TX_OK` encode collision-avoidance thresholds.
- `enum typec_cc_polarity` identifies CC1/CC2 orientation.
- Timeouts define TCPC transmit, role-swap, and augmented power-supply control waits.
- `enum tcpm_transmit_status` and `enum tcpm_transmit_type` describe PD transmission completion and SOP/hard-reset/cable-reset/BIST targets.
- Mux flags identify USB, DisplayPort, and polarity-inverted states.
- `struct tcpc_dev` is the low-level callback vector: init, VBUS/current, CC set/get, polarity/orientation, VCONN/VBUS/current limit, PD RX enable, roles, toggling, try-role, PD transmit, BIST, FRS, auto discharge, VSAFE0V, partner USB communication, contaminant check, cable communication, and VCONN-swap discovery policy.
- APIs register/unregister ports and notify TCPM of VBUS, CC, FRS, sourcing VBUS, PD receive, transmit complete, hard reset, TCPC reset, clean port, toggling state, and error recovery.

## Control Flow and Lifetimes

A TCPC driver fills `tcpc_dev` and registers it with `tcpm_register_port()`. TCPM drives callbacks to configure CC, roles, VBUS/VCONN, PD RX/TX, mux policy, and discharge. The low-level driver reports interrupts or hardware changes through notification functions, causing TCPM policy transitions and PD message handling. Unregister stops policy and releases the port.

## State and Persistence Behavior

TCPM owns persistent runtime state for attachment, roles, negotiated PD revision, capabilities, message IDs, timers, and policy. The low-level `tcpc_dev` must remain valid until unregister completes. Hardware CC/VBUS/PD state is managed through callbacks.

## Dependencies and Integration Points

It depends on Type-C class definitions and `pd.h`. It integrates TCPCI and non-TCPCI port controllers, Type-C mux/alt-mode code, power-supply control, USB role switching, DisplayPort modes, and PD policy.

## Risks and Edge Cases

Callbacks have optional versus mandatory semantics; missing mandatory operations break policy. Hardware interrupts can race unregister. VBUS discharge, FRS, PPS/AVS, contaminant recovery, and VCONN-swap discovery are policy-heavy and hardware-dependent. PD transmit completion must be reported exactly once per transmit.

## Test Signals

Run TCPM attach/detach, source/sink negotiation, PD message RX/TX, hard reset, role swaps, VCONN swap, FRS, PPS/AVS current-limit updates, mux changes, contaminant recovery, unregister during events, and low-level callback failure injection.
