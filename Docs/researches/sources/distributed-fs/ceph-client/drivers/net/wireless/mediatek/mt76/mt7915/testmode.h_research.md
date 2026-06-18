# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/testmode.h

## Purpose
This header defines the packed firmware command payloads and local enums used by `testmode.c` for MT7915 ATE and RF test operations. It is the ABI description between the driver testmode path and firmware extended commands.

## Important APIs, Types, And Functions
Important structures are `mt7915_tm_trx`, `mt7915_tm_freq_offset`, `mt7915_tm_slot_time`, `mt7915_tm_clean_txq`, `mt7915_tm_cmd`, `tm_tx_cont`, and `mt7915_tm_rf_test`. `mt7915_tm_cmd` is the generic ATE control wrapper with `testmode_en`, `param_idx`, and a union for parameter-specific payloads. `mt7915_tm_rf_test` is the RF-test wrapper with operation mode, frequency, function index, continuous TX parameters, and padding for firmware expectations.

The enums define MAC TRX modes (`TM_MAC_TX`, `TM_MAC_RX`, `TM_MAC_TXRX`, RXV variants), RF operation modes (`RF_OPER_NORMAL`, `RF_OPER_RF_TEST`, ICAP, overlap, spectrum), and TAM arbitration modes (`TAM_ARB_OP_MODE_NORMAL`, `TEST`, `FORCE_SU`).

## Control Flow
There is no code flow in the header. `testmode.c` fills these structures when changing state, enabling RX/TX, setting slot/frequency/queue cleanup, or switching continuous TX through RF test mode.

## State And Persistence
All structures are transient command buffers. Persistent effects occur only after firmware accepts the commands, where it may alter RF mode, ATE state, MAC TRX gates, timing, and queues until later command reversal.

## Dependencies And Integration Points
The header depends on Linux fixed-width and endian types. It is included by `testmode.c` and must match firmware command layouts for `MCU_EXT_CMD(ATE_CTRL)` and `MCU_EXT_CMD(RF_TEST)`.

## Risks
The structures are `__packed` and field order is firmware ABI. Any padding, size, endian, or enum value change can silently misprogram factory-test firmware. The `test[72]` and `_pad[80]` areas are placeholders for command size compatibility and should not be reused without firmware confirmation.

## Test Signals
Compile-time coverage should verify packed structures remain accepted by firmware. Runtime signals are successful ATE commands for TRX, slot time, queue cleanup, frequency offset, RF mode switching, and continuous TX start/stop without firmware rejects or malformed command traces.
