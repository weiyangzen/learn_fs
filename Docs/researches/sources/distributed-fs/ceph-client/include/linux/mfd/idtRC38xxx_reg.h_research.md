# sources/distributed-fs/ceph-client/include/linux/mfd/idtRC38xxx_reg.h

Purpose: This file provides register definitions for Renesas/IDT RC38xxx timing hardware. It covers page addressing, DPLL/TOD register families, sync and output control, GPIO/status blocks, firmware/hardware IDs, and reset/status constants used by timing-card drivers.

Important APIs, types, and constants: The header is macro-only. It defines device identification and status offsets, DPLL base registers, time-of-day configuration/status/trigger fields, output mux and synchronization-related registers, reset controls, firmware version fields, and bit masks for DPLL operating state and trigger operations. The pattern mirrors the other IDT timing headers but targets the RC38xxx register layout.

Control flow, state, and persistence: Consumers perform paged register access, configure DPLL operating modes and TOD triggers, poll DPLL status, and route outputs/GPIOs. Hardware keeps persistent state for PLL lock/holdover, TOD counters, output divider configuration, reset state, and firmware identity.

Dependencies and integration points: It is consumed by PTP/time synchronization drivers and lower-level register access layers. It integrates with DPLL/PTP frameworks, clock-output configuration, and possibly GPIO/event reporting for timing cards.

Risks and test signals: Risks include mixing RC38xxx offsets with 82P33 or 8A340 layouts, using wrong page/offset calculations, and misinterpreting lock-state bitfields. Test signals include register identity readback, TOD trigger tests, DPLL mode/status polling, output mux validation, soft reset recovery, and cross-checking all masks against hardware programming guides.
