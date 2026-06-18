# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_mcu.c

## Purpose
This file implements the MediaTek WED WO MCU control path. It loads WO firmware into reserved memory regions, starts the WO CPU, builds MCU command SKBs, sends them through the WO CCIF TX queue, waits for sequence-matched responses, and handles unsolicited firmware events such as log dumps, profiling records, and RX counter updates.

## Important APIs and Functions
- `mtk_wed_mcu_send_msg()` is the serialized command entry point. It allocates an MCU message, pushes `struct mtk_wed_mcu_hdr`, sends through `mtk_wed_wo_queue_tx_skb()`, and optionally waits on `wo->mcu.wait`.
- `mtk_wed_mcu_msg_update()` is the higher-level WED device entry point. It checks RX capability and dispatches WO module commands.
- `mtk_wed_mcu_rx_event()` queues response SKBs on `wo->mcu.res_q`; `mtk_wed_mcu_rx_unsolicited_event()` consumes asynchronous events.
- `mtk_wed_mcu_init()` initializes MCU synchronization state, loads firmware, and polls `MTK_WED_DUMMY_CR_FWDL` until firmware clears the download marker.
- Firmware loading is split between `mtk_wed_mcu_load_firmware()`, `mtk_wed_get_memory_region()`, and `mtk_wed_mcu_run_firmware()`.

## Control Flow
Initialization maps reserved-memory regions named `wo-emi`, `wo-ilm`, `wo-data`, and `wo-boot`, writes a firmware-download marker into WED scratch space, selects a firmware name from hardware version/index and compatible string, copies trailer-described firmware regions to matching physical regions, writes the WO boot address, clears MCU reset bits, and waits for firmware acknowledgement. Runtime commands are serialized by `wo->mcu.mutex`; responses are dequeued until the expected sequence is found, with out-of-order responses returning `-EAGAIN`.

## State and Persistence
The file maintains global static `mem_region[]` metadata, including mapped IO addresses and `consumed` flags for shared regions. Per-WO MCU state lives in `wo->mcu`: sequence counter, timeout, response queue, mutex, and waitqueue. Firmware state persists in reserved memory and device registers outside this file.

## Dependencies and Integration Points
It depends on `mtk_wed_wo.c` for queue transmission and RX delivery, `mtk_wed_wo.h` for MCU message and firmware metadata layouts, `mtk_wed_regs.h` for scratch and boot registers, device tree reserved-memory names, Linux firmware loading, unaligned little-endian helpers, and WLAN callbacks such as `wed->wlan.update_wo_rx_stats`.

## Risks and Test Signals
Risks include malformed firmware trailers causing bad length arithmetic, global `mem_region[]` state being shared across hardware instances, unmatched response sequence SKBs being dropped after parse, and missing reserved-memory nodes silently yielding zero-sized regions. Useful tests are boot on MT7981/MT7986/MT7988 variants, firmware load failure paths, response timeout behavior, unsolicited RX counter parsing with short buffers, and concurrent command serialization under RX event pressure.
