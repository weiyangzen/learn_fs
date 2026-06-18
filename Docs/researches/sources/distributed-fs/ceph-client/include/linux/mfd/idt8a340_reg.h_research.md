# sources/distributed-fs/ceph-client/include/linux/mfd/idt8a340_reg.h

Purpose: This header maps a broad subset of Renesas/IDT 8A340 DPLL/timing-device registers. It is used by timing/PTP drivers to select pages, identify hardware/firmware revision, control DPLL TOD, synchronize output dividers, read DPLL/GPIO status, issue resets, and handle GPIO/TOD/clock-output routing.

Important APIs, types, and constants: Constants define global page address registers, hardware revision and DPLL base addresses, DPLL TOD control/override/output offsets, channel synchronization control registers, sync source IDs, sync trigger bits, Q8/Q11 special fanout and sync masks, reset commands, status block offsets, DPLL status registers, GPIO output/status registers, and many additional output, input, DPLL, TOD, and event status offsets through the file. The file is macro-only and uses register-block base plus offset patterns heavily.

Control flow, state, and persistence: Runtime flow in consumers uses the page selector to access 16-bit register windows, performs reset and sync-trigger writes, polls status, and reads or writes TOD/DPLL configuration. Persistent state is in DPLL lock/filter state, TOD counters, output divider sync setup, GPIO state, firmware revision fields, and NVM/OTP-selected product configuration.

Dependencies and integration points: It integrates with regmap or custom paged bus access, PTP clock drivers, DPLL state management, clock-output configuration, GPIO support, and board-specific synchronization routing.

Risks and test signals: Risks include page-register misuse, incomplete support for device version differences such as v5.20 reset/GPIO offsets, one-shot sync trigger bits left asserted, and mismatched output channel assumptions. Test signals include revision/product ID readback, reset command acceptance, DPLL lock status transitions, TOD capture/set tests, Q-channel sync tests, GPIO status/output tests, and PTP frequency/phase adjustment validation.
