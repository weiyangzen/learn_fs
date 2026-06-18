# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_usb.c

## Purpose
This file provides shared USB helpers for MT792x devices: vendor register access, block copy, MCU power-on, USB WFDMA/UDMA configuration, endpoint reset options, WFSYS reset, initial reset, stop, disconnect, and cleanup.

## Important APIs, Types, And Functions
Exports include `mt792xu_rr()`, `mt792xu_wr()`, `mt792xu_rmw()`, `mt792xu_copy()`, `mt792xu_mcu_power_on()`, `mt792xu_dma_init()`, `mt792xu_wfsys_reset()`, `mt792xu_init_reset()`, `mt792xu_stop()`, and `mt792xu_disconnect()`. Internal helpers include UHW register access, `mt792xu_wfdma_init()`, `mt792xu_dma_rx_evt_ep4()`, endpoint reset option toggling, and chip-specific WFSYS descriptors for MT7921 and MT7925.

## Control Flow
Register access serializes USB vendor requests under `usb_ctrl_mtx`. DMA init programs WFDMA prefetch, UDMA RX/TX enable, aggregation/padding settings, optional RX-event EP4 routing, and endpoint reset options. WFSYS reset toggles the chip-specific whole-path reset bit through UHW vendor access, waits, optionally selects status, and polls init-done. Initial reset marks reset, wakes MCU waiters, purges responses, stops USB RX/TX, resets WFSYS, clears reset, and resumes RX. Disconnect cancels init work, unregisters initialized devices, resets WFSYS, purges MCU queues, deinitializes USB queues, clears interface data, drops the USB device reference, and frees mt76 state.

## State And Persistence
State includes USB control mutex, vendor request buffers, queue allocation/initialization, UDMA/WFDMA registers, endpoint reset option bits, `MT76_STATE_INITIALIZED`, `MT76_RESET`, MCU response queue, and USB interface data/reference ownership.

## Dependencies And Integration Points
It integrates with Linux USB core, mt76 USB vendor helpers, MT792x register map, MT7925/MT7921 bus drivers, connac MAC stop logic, and mt76 queue cleanup.

## Risks
USB vendor requests must be serialized and chunked correctly. WFSYS reset descriptors differ by chip; wrong done register/mask causes reset timeouts. Endpoint reset options affect hub/device recovery. Disconnect must tolerate partially initialized devices without leaking references or freeing live queues.

## Test Signals
USB register reads/writes/copies, firmware power-on, DMA init with RX event EP4, reset on MT7921 and MT7925, suspend/resume through chip driver, unplug during init, and queue cleanup validate this helper layer.
