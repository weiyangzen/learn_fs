
# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hibmcge/hbg_diagnose.h

## Purpose

This header declares the HIBMCGE diagnostic push entry point.

## Important APIs, Types, and Functions

It includes `hbg_common.h` and declares `hbg_diagnose_message_push(struct hbg_priv *priv)`.

## Control Flow

No control flow is present in the header. The service task calls the declared function.

## State and Persistence

No state is stored here.

## Dependencies and Integration Points

It connects `hbg_main.c` service work to `hbg_diagnose.c`.

## Risks and Edge Cases

Prototype drift would break the periodic diagnostics integration.

## Test Signals

Build coverage and BMC diagnostic push behavior validate the header contract.
