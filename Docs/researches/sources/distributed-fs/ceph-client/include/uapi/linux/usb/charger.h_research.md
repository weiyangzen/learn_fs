# sources/distributed-fs/ceph-client/include/uapi/linux/usb/charger.h

Purpose: Defines USB charger type and state enums shared with userspace or platform code.

Important APIs/types/functions: Charger type values identify unknown, SDP, DCP, CDP, ACA, and Apple-style charger classes. Charger state values represent removed, present, online, and unknown states.

Control flow: USB charger detection code classifies a port/charger and reports state to power-supply or platform consumers.

State and persistence behavior: Charger state is live physical/power state. It changes with cable attachment, negotiation, and removal.

Dependencies and integration points: Integrates with USB PHY/charger detection, power_supply, Type-C/BC1.2 policy, and platform battery charging logic.

Risks: Misclassification can overdraw current or undercharge. Vendor-specific Apple currents require platform policy beyond enum values.

Test signals: Simulate or attach each charger type, verify state transitions on plug/unplug, power-supply reporting, and unknown/fallback handling.
