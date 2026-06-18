# sources/distributed-fs/ceph-client/arch/mips/include/asm/octeon/cvmx-sriox-defs.h

Purpose: provides the large OCTEON SRIO controller CSR map and bitfield definitions for access control, assembly ID, BIST, inbound/outbound messages, doorbells, interrupts, maintenance operations, memory operations, S2M mappings, tag control, credits, link status, and transmit/receive status.

Important APIs/types/functions: address macros include `CVMX_SRIOX_ACC_CTRL`, `ASMBLY_ID`, `ASMBLY_INFO`, `BELL_RESP_CTRL`, `BIST_STATUS`, `IMSG_*`, `INT_ENABLE`, `INT_REG`, `INT_INFO0-3`, `IP_FEATURE`, `MAC_BUFFERS`, `MAINT_OP`, `MAINT_RD_DATA`, `MEM_OP_CTRL`, `OMSG_*`, `PRIOX_IN_USE`, `RX_BELL`, `RX_STATUS`, `S2M_TYPEX`, `STATUS_REG`, `TAG_CTRL`, `TLP_CREDITS`, `TX_BELL`, `TX_CTRL`, `TX_STATUS`, and write-done counters. Register unions mirror those groups and include chip-specific CN63XX/CN63XX pass-1 variants where fields differ.

Control flow: the header is declarative. SRIO code uses these macros to configure link access, enable/inspect interrupts, initiate maintenance reads/writes through `MAINT_OP` and `MAINT_RD_DATA`, set inbound message QoS/group mapping, configure outbound message matching/ports, process doorbells, and monitor credits/status.

State and persistence: all state is SRIO hardware state in CSRs, including link status, error/interrupt latches, doorbell FIFOs, message queues, credit counters, retry thresholds, and access-control denial bits. No software persistence is held here.

Dependencies and integration points: depends on `CVMX_ADD_IO_SEG` and bitfield endian configuration. It integrates with OCTEON SRIO drivers and with feature probes that gate SRIO support to relevant models.

Risks: this file contains hardware errata-like layout variants and apparent duplicated field names in some generated structs, so compiler behavior and field selection must be treated carefully. Indexed macros mask block IDs, queue offsets, and priority offsets, which silently aliases invalid inputs. Interrupt enable/status fields are dense and easy to mismatch. Maintenance operations expose pending/fail bits; callers must poll correctly before using read data. SRIO access-deny bits can block BAR or address windows.

Test signals: hardware tests should cover SRIO link up/down interrupts, doorbell send/receive, maintenance read/write completion and fail paths, inbound/outbound message queues, credit counters, and CN63XX pass-1 layout handling. Compile tests should cover both endian bitfield modes.
