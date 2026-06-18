# sources/distributed-fs/ceph-client/include/soc/mscc/ocelot_sys.h

Purpose: defines bitfields for the Ocelot SYS block, which provides port counters, front-port mode, frame aging, statistics view/clear controls, switch status, PTP timestamp extraction, pause/flow-control configuration, memory manager counters, event status, and RAM initialization.

Important APIs/types/functions: macro-only API. Key groups include `SYS_COUNT_*`, `SYS_STAT_CFG_*`, `SYS_MAC_FC_CFG_*`, `SYS_MMGT_*`, `SYS_EVENTS_*`, `SYS_PTP_STATUS_*`, `SYS_PTP_TXSTAMP_*`, `SYS_PTP_CFG_*`, and `SYS_RAM_INIT_*`.

Control flow: consumers select counter views, clear statistics, configure flow-control thresholds, read memory-manager status, and pull PTP TX timestamp messages by checking status and advancing with `SYS_PTP_NXT_PTP_NXT`.

State and persistence: state is in SYS registers, counters, memory-manager status, flow-control configuration, and PTP timestamp FIFO/status fields. Counter and sticky-like event state persists until cleared or advanced.

Dependencies and integration: included by common Ocelot code, DSA variants, and `ocelot_ptp.c`. It integrates with ethtool stats, pause/PFC support, PTP TX timestamp reporting, and low-level switch initialization.

Risks: incorrect counter view selection can report wrong stats; mishandling PTP FIFO valid/next bits can drop timestamps; bad flow-control thresholds can cause pause storms or loss. Test signals include stats read/clear tests, pause frame behavior, PTP TX timestamp validation, and RAM init/probe checks.
