# sources/distributed-fs/ceph-client/drivers/net/ethernet/mediatek/mtk_wed_wo.c

## Purpose
This file implements the MediaTek WED WO CCIF queue and interrupt transport used by the MCU layer. It maps the WO CCIF syscon, allocates TX/RX descriptor rings, manages DMA-backed page-fragment buffers, handles RX interrupts in a tasklet, and exposes `mtk_wed_wo_queue_tx_skb()` for MCU command transmission.

## Important APIs and Functions
- `mtk_wed_wo_init()` allocates `struct mtk_wed_wo`, initializes hardware queues and interrupts, then starts the MCU firmware path.
- `mtk_wed_wo_deinit()` disables interrupts and frees queue resources.
- `mtk_wed_wo_queue_tx_skb()` copies an SKB into a preallocated TX DMA buffer, updates the descriptor, kicks the queue, and frees the SKB.
- `mtk_wed_wo_rx_run_queue()` converts completed RX fragments into SKBs and routes response vs unsolicited MCU messages.
- Internal helpers cover MMIO reads/writes, IRQ masking/ack, ring refill/dequeue/reset, and queue cleanup.

## Control Flow
Initialization obtains the `mediatek,wo-ccif` phandle, resolves a regmap, maps an IRQ, sets up a tasklet, requests the IRQ, allocates TX and RX coherent descriptor rings, refills buffers, writes ring base/size registers, and enables interrupts. The IRQ handler masks interrupts and schedules the tasklet. The tasklet reads pending channels, disables handled masks, drains RX descriptors, hands valid MCU packets to `mtk_wed_mcu_rx_event()` or `mtk_wed_mcu_rx_unsolicited_event()`, refills RX buffers, kicks hardware, acknowledges RX, and reenables interrupts.

## State and Persistence
Per-device state is stored in `struct mtk_wed_wo`: `q_tx`, `q_rx`, regmap/IRQ/tasklet state, and MCU state initialized by `mtk_wed_mcu_init()`. Queue state includes descriptor DMA address, head/tail indexes, queued count, buffer size, page-frag cache, and per-entry DMA mapping metadata. Hardware state persists in CCIF registers and descriptor memory.

## Dependencies and Integration Points
It integrates with device tree, syscon regmap, IRQ core, DMA mapping, SKB allocation, page-frag cache, `mtk_wed_mcu.c`, and register definitions from `mtk_wed_wo.h` and `mtk_wed_regs.h`.

## Risks and Test Signals
Risks include TX ring full handling returning `-ENOMEM`, DMA address truncation to 32-bit descriptor fields, RX buffer starvation under GFP_ATOMIC pressure, tasklet/IRQ ordering bugs, and deinit after partial init. Test signals include successful firmware command/response exchange, RX unsolicited event delivery, IRQ masking/reenable behavior, DMA mapping error injection, and repeated init/deinit cycles.
