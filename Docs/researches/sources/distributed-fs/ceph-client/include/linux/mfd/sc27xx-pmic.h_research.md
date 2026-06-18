# sources/distributed-fs/ceph-client/include/linux/mfd/sc27xx-pmic.h

## Purpose

This 7-line header exposes one SC27xx PMIC helper for charger type detection.

## Important APIs, Types, and Functions

It declares `sprd_pmic_detect_charger_type(struct device *dev)`, returning `enum usb_charger_type`. The function is implemented outside this header.

## Control Flow

The header has no flow. Callers invoke the helper to ask the Spreadtrum PMIC layer to inspect charger state and return the detected USB charger type.

## State and Persistence Behavior

No state is stored in the header. Detected state comes from PMIC hardware and possibly charger-detection logic in the implementation.

## Dependencies and Integration Points

It integrates SC27xx PMIC support with USB charger/power-supply consumers. `struct device` and `enum usb_charger_type` are expected from included kernel context.

## Risks and Edge Cases

The prototype relies on external type declarations; include order must provide the USB charger enum. Detection may fail or return unknown depending on PMIC state.

## Test Signals

Compile tests for users of the helper, charger detection tests for supported cables, and error-path tests when PMIC access is unavailable.
