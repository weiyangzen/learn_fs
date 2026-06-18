# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mcu.c

## Purpose
Common MCU message allocation, synchronous send/response handling, response queueing, retry behavior, and firmware chunk transfer support for mt76 drivers that implement the low-level MCU transport callbacks.

## Important APIs, Types, And Functions
- `__mt76_mcu_msg_alloc()` allocates an SKB with chip-defined headroom/tailroom, zeroes the backing buffer, reserves headroom, and optionally copies payload.
- `mt76_mcu_rx_event()` queues MCU event/response SKBs on `dev->mcu.res_q` and wakes waiters.
- `mt76_mcu_get_response()` waits until a response is queued, timeout expires, or `MT76_MCU_RESET` is set.
- `mt76_mcu_send_and_get_msg()` supports direct `mcu_send_msg` ops or allocates an SKB and delegates to the SKB path.
- `mt76_mcu_skb_send_and_get_msg()` serializes commands with `dev->mcu.mutex`, prepares sequence metadata, sends via driver ops, waits for matching responses, retries if configured, and returns an optional response SKB.
- `__mt76_mcu_send_firmware()` splits large firmware payloads into bounded chunks and optionally cleans the firmware download queue between chunks.

## Control Flow
Callers either pass data to `mt76_mcu_send_msg()` wrappers or build an SKB. The common send path locks the MCU mutex, lets the chip driver prepare a command and sequence number, sends via `mcu_skb_send_msg`, and, when a response is required, waits on `dev->mcu.wait`. Responses from RX are pushed through `mt76_mcu_rx_event()`. The chip-specific parser returns success, retry-needed `-EAGAIN`, timeout, or command errors. Firmware upload loops over chunks without waiting for per-chunk responses unless the chip op implements that behavior.

## State And Persistence
State is transient: `dev->mcu.msg_seq`, `timeout`, response SKB queue, and waitqueue. The MCU mutex provides command serialization. No persistent storage is written; firmware bytes are streamed to hardware queues.

## Dependencies And Integration Points
This code depends on chip-provided `struct mt76_mcu_ops`, mt76 queue ops for firmware TX cleanup, SKB queues, waitqueues, mutexes, and device state bits. Chip RX paths must classify MCU events and call `mt76_mcu_rx_event()`.

## Risks
If the chip parser does not discard nonmatching responses correctly, stale events can starve the current command. Retry uses `orig_skb` only when prepare ops created a reusable original; ownership is delicate because send ops consume SKBs. Timeout behavior marks failures but depends on chip code setting reset bits. Firmware chunking assumes `max_len` aligns with MCU expectations.

## Test Signals
Probe firmware load, command response matching, injected timeout/retry, reset during wait, and firmware download with queue cleanup. Validate no SKB leaks with kmemleak or debug counters and ensure MCU event RX wakes blocked command senders.
