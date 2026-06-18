# sources/distributed-fs/ceph-client/sound/firewire/motu/motu-transaction.c

## Purpose

This file centralizes MOTU asynchronous FireWire register access and inbound notification address registration. It abstracts the MOTU register aperture and publishes a local address that the device writes when status changes occur.

## Important APIs, types, and functions

`snd_motu_transaction_read()` and `snd_motu_transaction_write()` validate quadlet alignment and choose quadlet versus block transaction TCODEs against `SND_MOTU_ADDR_BASE`. `snd_motu_transaction_register()` installs a four-byte `fw_address_handler`. `snd_motu_transaction_reregister()` writes the handler address into MOTU `ASYNC_ADDR_HI/LO`. `handle_message()` stores inbound quadlet messages in `motu->msg`.

## Control flow

Registration configures the handler, adds it in the high response address region, then writes the address to the device; failures remove the handler. Inbound writes are accepted only for a quadlet at the registered offset. The callback stores the big-endian payload under `motu->lock`, responds complete, and wakes `hwdep_wait`. Unregister removes the handler and writes zeroes to the device address registers.

## State and persistence behavior

Persistent hardware state is the device's async callback address. Driver state includes `async_handler`, the last `msg`, and wait-queue wakeups. Bus resets clear device-side registers, so `snd_motu_transaction_reregister()` is called from the driver update callback.

## Dependencies and integration points

It depends on FireWire core address handlers and `snd_fw_transaction()`. Protocol v3 clock waits and hwdep event reads rely on `motu->msg` updates.

## Risks and test signals

Risks include stale handler addresses after bus reset, accepting unexpected tcode/lengths, and unregister writes racing with disconnect. Tests should cover probe/register failure paths, bus reset re-registration, v3 clock notification wakeups, and removal while clients are blocked in hwdep read.
