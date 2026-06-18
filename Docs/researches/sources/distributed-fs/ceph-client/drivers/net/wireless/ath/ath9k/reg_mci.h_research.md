# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_mci.h

## Purpose
`reg_mci.h` defines the MCI Bluetooth coexistence register interface used by ath9k chips with message-based WLAN/BT coordination. It maps MCI command, RX/TX control, scheduling, GPM buffers, interrupt, priority/frequency, LNA, gain, and debug registers.

## Important APIs, types, and constants
Key registers include `AR_MCI_COMMAND0..2`, `AR_MCI_RX_CTRL`, `AR_MCI_TX_CTRL`, `AR_MCI_GPM_*`, `AR_MCI_INTERRUPT_*`, `AR_MCI_REMOTE_CPU_INT*`, `AR_MCI_RX_STATUS`, `AR_MCI_CONT_STATUS`, `AR_BTCOEX_CTRL*`, `AR_BTCOEX_WL_WEIGHTS*`, `AR_BTCOEX_MAX_TXPWR`, and debug counter controls. Composite masks such as `AR_MCI_INTERRUPT_DEFAULT`, `AR_MCI_INTERRUPT_MSG_FAIL_MASK`, `AR_MCI_INTERRUPT_RX_HW_MSG_MASK`, and `AR_MCI_INTERRUPT_RX_MSG_DEFAULT` define the standard interrupt policy.

## Control flow and integration
The file has no direct control flow. Coexistence setup code programs message attributes, scheduling tables, interrupt enables, WLAN weights, BT priorities, gain controls, and remote CPU interrupts using these constants. The composite masks are the closest thing to policy: they select which MCI failures, received messages, and remote sleep updates should wake the driver.

## State and persistence behavior
MCI state persists in hardware while the coexistence block is active: command payloads, GPM pointers, schedule tables, interrupt enables/raw status, remote sleep state, continuous priority/RSSI state, coexistence weights, and debug counters. It is reset by MCI reset, device reset, or explicit reconfiguration.

## Dependencies
Consumers need ath9k register access helpers and Bluetooth coexistence state machines. Some fields are specific to AR9462-style MCI operation and require hardware capability checks before use.

## Risks
High-risk areas include interrupt-mask drift, not clearing message-fail conditions, stale GPM read/write pointers, incorrect LNA/shared-antenna policy, and wrong coexistence weights that either starve WLAN or break Bluetooth. The fail-mask macros are critical for robust recovery paths.

## Test signals
Signals include MCI interrupt handling under BT traffic, remote sleep/wake updates, GPM message parsing, coexistence throughput with concurrent WLAN/BT use, absence of repeated message-fail interrupts, and stable reset/reinitialization after BT controller resets.
