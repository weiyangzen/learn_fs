# sources/distributed-fs/ceph-client/drivers/mailbox/arm_mhu_db.c

## Purpose
Implements the ARM MHU doorbell variant. It exposes individual doorbell bits within the three physical MHU channels as dynamically allocated mailbox channels.

## Important APIs, Types, And Functions
`struct mhu_db_link` stores physical channel IRQ and TX/RX registers. `struct mhu_db_channel` stores parent controller, physical channel index, and doorbell bit. `mhu_db_mbox_xlate()` translates a two-cell mailbox specifier `(physical-channel, doorbell)` into a free mailbox channel. `mhu_db_send_data()` sets the selected doorbell bit; `mhu_db_last_tx_done()` checks whether it is still set; `mhu_db_mbox_rx_handler()` maps IRQ status bits back to registered channels, calls `mbox_chan_received_data()`, and clears each bit.

## Control Flow
Probe requires `"arm,mhu-doorbell"` and `#mbox-cells = <2>`, maps registers, allocates up to `MHU_CHAN_MAX` channel slots, registers the controller with a custom `of_xlate`, then requests one threaded IRQ per present physical channel. A client request allocates a `mhu_db_channel` in the first free slot; shutdown clears the bit and frees that private data.

## State, Dependencies, And Integration
State includes fixed physical link info and dynamically populated mailbox channel `con_priv` entries. It depends on AMBA, OF mailbox specifiers, devm memory/IRQ management, MMIO register access, and the generic mailbox framework. It builds with `CONFIG_ARM_MHU` alongside the non-doorbell driver.

## Risks And Test Signals
Only twenty logical channels are reserved even though hardware has up to 96 doorbells, trading RAM for capacity. IRQ handler status scanning reports unregistered doorbells as errors and loops until no registered pending channel remains. `devm_kfree()` on shutdown must not conflict with devm cleanup. Test signals include invalid specifier bounds, duplicate doorbell allocation, channel exhaustion, unregistered doorbell IRQs, TX polling, and shutdown/reallocation of the same doorbell.
