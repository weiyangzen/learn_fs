
# sources/distributed-fs/ceph-client/include/linux/platform_data/dsa.h

## Purpose
This header defines legacy platform data for Distributed Switch Architecture switch chips. It describes port names, CPU/DSA links, associated network devices, and optional EEPROM size.

## Important APIs And Types
`DSA_MAX_PORTS` is 12. `struct dsa_chip_data` contains `netdev[DSA_MAX_PORTS]`, `eeprom_len`, and `port_names[DSA_MAX_PORTS]`. Port names use special strings: `"cpu"` for the CPU-facing port, `"dsa"` for inter-switch links, `NULL` for unused ports, and arbitrary names for user-facing physical ports.

## Control Flow, State, And Persistence
There is no executable flow. Platform data is consumed during switch registration to create the logical DSA topology and network interfaces. Runtime state lives in the DSA core and switch driver; EEPROM size describes optional persistent switch EEPROM access.

## Dependencies And Integration Points
The header forward-declares `struct device` and integrates legacy board files with the Linux DSA networking subsystem.

## Risks And Test Signals
Risks include incorrect CPU port designation, wrong DSA link labeling, missing netdev references, and exposing EEPROM operations with a bad size. Test signals include switch tree registration, port interface naming, traffic over CPU and DSA links, unused port suppression, and EEPROM read/write bounds.
