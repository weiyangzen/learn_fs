# sources/distributed-fs/ceph-client/include/linux/mfd/rohm-bd96802.h

## Purpose

This 74-line header supplies BD96802-specific IRQ numbering for a reduced digital interface derived from BD96801. It avoids gaps in IRQ numbers for a chip variant with fewer buck/LDO blocks.

## Important APIs, Types, and Functions

It defines two enums: BD96802 ERRB IRQs for system errors and BUCK1/BUCK2 protection/shutdown faults, and BD96802 INTB IRQs for system warnings and BUCK1/BUCK2 over-current, voltage, and thermal-warning conditions. It intentionally reuses BD96801 register/mask definitions elsewhere.

## Control Flow

There is no executable flow. MFD and IRQ code select this compact enum when probing BD96802, while using BD96801-compatible register addresses for the reduced hardware block.

## State and Persistence Behavior

The header owns no state. It describes hardware IRQ latches that persist in BD96802 ERRB/INTB registers until acknowledged and cleared.

## Dependencies and Integration Points

It integrates with the BD96801-style ROHM MFD/IRQ implementation and regulator fault reporting, while exposing variant-correct IRQ numbers to child devices and device-tree interrupt consumers.

## Risks and Edge Cases

Using BD96801 IRQ numbering on BD96802 would create holes or mismatched Linux IRQ numbers. Assuming absent buck/LDO groups exist would cause invalid register reads or unhandled interrupt bits.

## Test Signals

Compile coverage for BD96802 probe paths, IRQ count/order validation against the regmap-irq tables, and hardware or emulated interrupt tests for both ERRB and INTB lines.
