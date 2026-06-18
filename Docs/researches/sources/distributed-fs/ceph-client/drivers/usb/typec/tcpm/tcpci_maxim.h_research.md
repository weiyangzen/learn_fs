# sources/distributed-fs/ceph-client/drivers/usb/typec/tcpm/tcpci_maxim.h

## Purpose

`tcpci_maxim.h` defines Maxim TCPCI vendor register constants, contaminant-detection state, shared chip state, raw regmap helpers, and the contaminant helper API.

## Important APIs, Types, and Functions

Register and bit definitions cover vendor CC status, fast low-power ADC status/control, CC control, dry detection, low-power mode, OVP controls, source current settings, and water-detection timing. `enum contamiant_state` tracks contaminant detection state. `struct max_tcpci_chip` combines generic `tcpci_data`, the registered `tcpci` handle, device/I2C/TCPM handles, contaminant state, VCONN swap veto, and optional VBUS regulator. Inline helpers read/write 8-bit and 16-bit registers via raw regmap operations. `max_contaminant_is_contaminant()` is declared for the Maxim contaminant module.

## Control Flow

The header has no standalone runtime flow. Inline helpers provide direct raw register access used by Maxim core and contaminant code.

## State and Persistence Behavior

The shared chip structure stores runtime Maxim state, including contaminant tracking and VCONN swap policy. Vendor register state remains in hardware.

## Dependencies and Integration Points

It depends on `struct tcpci_data`, `struct tcpci`, regmap, regulators, TCPM, and TCPCI definitions included by users. It is the local contract between `tcpci_maxim_core.c` and `maxim_contaminant.c`.

## Risks and Test Signals

Risks include the misspelled enum name becoming part of local API, raw endianness assumptions for 16-bit register access, and tight coupling between contaminant helper and Maxim core state. Test signals include compile coverage of Maxim composite module, raw register read/write helpers, contaminant state transitions, VCONN swap veto users, and VBUS regulator handling in the Maxim core.
