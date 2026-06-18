# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/core.c

## Purpose
MT7603 interrupt dispatch and register remapping helpers.

## Important APIs, Types, And Functions
- `mt7603_rx_poll_complete()` re-enables RX-done interrupts after NAPI completes an RX queue.
- `mt7603_irq_handler()` acknowledges interrupt sources, filters them through `dev->mt76.mmio.irqmask`, schedules tasklets/NAPI for MAC IRQ3, TX done, and RX done rings, and handles CSA finish on TBTT.
- `mt7603_reg_map()` programs the PCIe remap register and returns the local remap-window address for high physical register addresses.

## Control Flow
The IRQ handler reads and writes `MT_INT_SOURCE_CSR` to acknowledge all pending bits, ignores interrupts until `MT76_STATE_INITIALIZED` is set, masks by cached IRQ mask, handles MAC IRQ3 substatus by acknowledging `MT_HW_INT_STATUS(3)`, schedules pre-TBTT work, disables TX/RX done interrupts before scheduling NAPI, and returns handled. Register-map callers write the high address base to `MT_MCU_PCIE_REMAP_2` before accessing the remap window.

## State And Persistence
State includes `dev->mt76.mmio.irqmask`, NAPI scheduling state, `dev->rx_pse_check`, tasklet scheduling, and the hardware remap register. No durable persistence exists.

## Dependencies And Integration Points
Integrates with mt76 MMIO ops, tracepoints, mt7603 IRQ enable/disable helpers, NAPI instances initialized by DMA code, pre-TBTT tasklet in `beacon.c`, and CSA helpers in shared mac80211 code.

## Risks
Interrupt acknowledgement before initialization can drop early interrupts by design. Remap register access is not independently locked here, so callers must avoid concurrent conflicting high-address accesses when necessary. IRQ bits are disabled before NAPI; missing re-enable in poll completion stalls traffic.

## Test Signals
Verify RX/TX NAPI scheduling under load, interrupt mask toggling, pre-TBTT beacon tasklet execution, CSA completion on TBTT, and register accesses above the direct window. Use trace IRQ output to confirm masked bits and status acknowledgements.
