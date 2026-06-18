# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/maxim_contaminant.c

## Purpose

`maxim_contaminant.c` implements Maxim TCPCI contaminant/water detection support. It reduces wakeups and false connects by measuring CC/SBU resistance and switching the controller between dry-detection and normal toggling states.

## Important APIs, Types, and Functions

The exported helper is `max_contaminant_is_contaminant()`, declared in `tcpci_maxim.h` and called by the Maxim TCPCI core. Internal helpers include `max_contaminant_read_adc_mv()`, `max_contaminant_read_resistance_kohm()`, `max_contaminant_read_comparators()`, `max_contaminant_detect_contaminant()`, `max_contaminant_enable_dry_detection()`, and `max_contaminant_enable_toggling()`. `enum fladc_select` selects ADC channels and `enum contamiant_state` in the header tracks not-detected, detected, and sink cases.

## Control Flow

When asked to evaluate a CC event, the helper reads CC status and power control, treats active toggling with a prior detected contaminant as contaminant, optionally delays for debounce, checks for both CC pins open, temporarily overrides role control, measures CC1/CC2/SBU1/SBU2 resistances using 1 uA sources and ADC channels, reads comparators with 80 uA source, infers sink or contaminant state, restores or adjusts role control, and either enables dry detection or resumes normal toggling. It returns whether TCPM should treat the event as contaminant and whether CC handling was already consumed.

## State and Persistence Behavior

Persistent runtime state is `chip->contaminant_state`, stored in the Maxim chip wrapper. Hardware state changes include ADC enable/channel selection, current-source configuration, OVP disable/enable, comparator enable, role control overrides, low-power dry detection, and Look4Connection commands.

## Dependencies and Integration Points

It depends on Maxim vendor registers from `tcpci_maxim.h`, generic TCPCI register definitions, regmap, bitfield helpers, TCPM/Type-C enums, and the Maxim TCPCI core's `max_tcpci_chip` object. It plugs into the TCPCI vendor hook path for contaminant checks.

## Risks and Test Signals

Risks include invasive temporary changes to `TCPC_ROLE_CTRL`, analog threshold sensitivity, cleanup on intermediate regmap failures, sleep delays inside event handling, and the misspelled `contamiant_state` enum being part of local API. Test signals include open-CC contaminant detection, sink inference through comparators, dry-to-normal transition after removal, disconnect-while-debounce path, regmap failure cleanup restoring role control, and ensuring `cc_handled` is correct for TCPM.
