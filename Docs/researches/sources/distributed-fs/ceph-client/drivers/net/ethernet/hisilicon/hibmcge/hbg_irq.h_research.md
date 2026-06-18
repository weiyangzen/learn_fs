
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_irq.h

## Purpose

This header declares HIBMCGE IRQ initialization.

## Important APIs, Types, and Functions

It includes `hbg_common.h` and declares `hbg_irq_init(struct hbg_priv *priv)`.

## Control Flow

No control flow is present.

## State and Persistence

No state is declared here.

## Dependencies and Integration Points

The declaration connects main device initialization with the IRQ implementation.

## Risks and Edge Cases

Prototype drift would break probe-time IRQ initialization.

## Test Signals

Build coverage and successful interrupt setup validate the header.
