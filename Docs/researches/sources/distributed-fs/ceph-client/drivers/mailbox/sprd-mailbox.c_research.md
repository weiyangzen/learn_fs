# sources/distributed-fs/ceph-client/drivers/mailbox/sprd-mailbox.c

Purpose: implements Spreadtrum/Unisoc mailbox controllers with an inbox for TX and one or more outboxes for RX, supporting R1 and R2 FIFO/status layouts and up to 16 channels.

Important APIs/types/functions: `struct sprd_mbox_priv` owns controller, inbox/outbox/supplementary MMIO, FIFO depth, match info, reference count, lock, and channels. `struct sprd_mbox_info` identifies hardware revision and supplementary outbox id. Core functions compute FIFO length, handle outbox/supplementary RX, handle inbox txdone IRQs, send two-word messages, flush by polling busy bits, startup/shutdown shared interrupt masks, and probe.

Control flow: probe maps inbox and outbox resources, enables clock, requests inbox/outbox IRQs and optional supplementary outbox IRQ, reads FIFO depth, initializes channel ids, and registers a txdone-IRQ mailbox. Startup increments a shared refcount and on first user resets/enables outbox and inbox interrupt masks. Sending writes two `u32` words and target id to inbox registers then triggers. Inbox IRQ clears delivery/overflow status, checks busy bits per delivered channel, and calls `mbox_chan_txdone` when the target fetched the message. Outbox IRQ calculates FIFO length, drains messages, routes each by message id to a channel callback if bound, advances the FIFO pointer, and clears IRQ status.

State and persistence: shared interrupt enable state is refcounted across channels. Hardware FIFOs hold transient TX/RX state; no persistent data exists.

Dependencies and integration: depends on Unisoc DT compatibles, named inbox/outbox/supp-outbox IRQs, enabled clock, mailbox framework, and revision-specific register semantics.

Risks: outbox message id directly indexes `priv->chan` without explicit bounds check. R1/R2 status differences make regressions easy. Flush uses jiffies plus microsecond polling and only the R1 busy mask.

Test signals: R1 and R2 hardware coverage, supplementary outbox routing, FIFO wrap/full length computation, txdone IRQ and flush paths, and dropped-message logging when no client is bound.
