# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-xgene-slimpro.c

## Purpose

`i2c-xgene-slimpro.c` provides SMBus/I2C-block access to Applied Micro X-Gene SLIMpro firmware-controlled I2C bus 1 through mailbox or ACPI PCC transport. It does not drive I2C registers directly; it sends encoded firmware messages.

## Important APIs, Types, and Functions

`struct slimpro_i2c_dev` stores adapter, device, mailbox/PCC channels, mailbox client, completion, DMA buffer, and response pointer. Message helpers include `slimpro_i2c_send_msg()`, `slimpro_i2c_rd()`, `slimpro_i2c_wr()`, `slimpro_i2c_blkrd()`, and `slimpro_i2c_blkwr()`. `xgene_slimpro_i2c_xfer()` implements SMBus protocols.

## Control Flow

Probe configures mailbox client behavior differently for DT and ACPI/PCC, requests the channel, checks PCC IRQ support, sets a DMA mask, configures the SMBus adapter, and registers it. SMBus operations encode chip address, protocol, command/address length, data length, and optional DMA buffer address into three 32-bit words, send the message, wait for completion if required, and copy data to/from `dma_buffer` for block operations.

## State and Persistence Behavior

`resp_msg` is temporarily set to the response storage during a mailbox transaction and cleared afterward. `dma_buffer` is reused for block transfers. No persistent device cache exists. ACPI PCC uses shared-memory status bits and explicit `mbox_chan_txdone()`.

## Dependencies and Integration Points

It integrates with mailbox framework, PCC for ACPI, DMA mapping, platform OF/ACPI matching, SMBus algorithm callbacks, and SLIMpro firmware message format. It exposes only SMBus byte/byte-data/word/block/I2C-block capabilities.

## Risks

Firmware response `0xffffffff` is treated as no device. DMA block read copies from the DMA buffer even if firmware returned an error, relying on the error code to make callers ignore data. PCC status manipulation uses little-endian shared memory helpers and must remain race-safe. The driver hardcodes SLIMpro I2C bus 1.

## Test Signals

Test DT mailbox and ACPI PCC probe paths, PCC IRQ absence, byte/byte-data/word/block/I2C-block read/write operations, invalid device response, mailbox timeout, DMA mapping failure, block length boundaries, and channel release on probe failure/remove.
