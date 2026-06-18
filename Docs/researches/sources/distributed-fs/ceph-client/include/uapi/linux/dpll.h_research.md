## sources/distributed-fs/ceph-client/include/uapi/linux/dpll.h

Purpose: This generated UAPI header defines the generic-netlink family contract for Digital Phase Locked Loop devices and pins. It exposes clock selection, lock status, quality, phase/frequency monitoring, and pin control for synchronization hardware.

Important APIs and types: The family is `DPLL_FAMILY_NAME` `"dpll"` version 1 with monitor multicast group `DPLL_MCGRP_MONITOR`. Device enums cover mode, lock status, lock-status error, clock quality, type, and device attributes `DPLL_A_*`. Pin enums cover type, direction, state, capabilities, supported frequencies, phase adjustment, fractional frequency offset, embedded sync, reference sync, and measured frequency through `DPLL_A_PIN_*`. Commands include device id/get/set/create/delete/change notifications and pin id/get/set/create/delete/change notifications.

Control flow and state: Userspace queries device or pin IDs, gets attributes, and sends set commands for mutable fields such as mode, pin state, priority, direction, phase adjust, or monitor toggles where supported. Drivers publish notifications for device and pin lifecycle and changes. Lock status transitions from unlocked to locked, locked with holdover acquired, or holdover based on input signal availability and hardware state.

Persistence and dependencies: Runtime state is held in synchronization hardware and kernel dpll objects, not persisted by this header. It is auto-generated from `Documentation/netlink/specs/dpll.yaml`, so source-of-truth changes should regenerate it via `tools/net/ynl/ynl-regen.sh`.

Integration points: DPLL integrates with NICs, SyncE, GNSS, PPS, telecom timing, PTP-adjacent clock infrastructure, and netlink YNL tooling. Pin types identify external, SyncE Ethernet port, internal oscillator, GNSS, and mux pins.

Risks and test signals: Risks include manual edits being overwritten, enum value stability, unsupported mutable attributes, misreported units using dividers for temperature/phase/frequency, and racey notifications. Tests should validate YNL spec regeneration, netlink policy for each attribute, get/set permission failures, notification delivery, lock-status error reporting, and driver conformance for pin capabilities.
