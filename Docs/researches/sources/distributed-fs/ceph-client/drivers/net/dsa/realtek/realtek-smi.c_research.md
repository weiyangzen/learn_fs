# sources/distributed-fs/ceph-client/drivers/net/dsa/realtek/realtek-smi.c

## Purpose

This file implements the Realtek Simple Management Interface transport for DSA switches. SMI is a Realtek-specific bit-banged protocol using GPIO lines named like MDIO/MDC but not following the MDIO frame format. The file provides low-level start/stop, bit, byte, ACK, read/write operations, regmap transport callbacks, and exported probe/remove/shutdown helpers that integrate with the shared `rtl83xx` core.

## Important APIs, Types, and Functions

- `realtek_smi_clk_delay()` applies the variant-specific nanosecond delay.
- `realtek_smi_start()` and `realtek_smi_stop()` emit the protocol framing and switch GPIO direction/state.
- `realtek_smi_write_bits()` and `realtek_smi_read_bits()` shift data over GPIOs.
- `realtek_smi_wait_for_ack()`, `realtek_smi_write_byte()`, `realtek_smi_write_byte_noack()`, `realtek_smi_read_byte0()`, and `realtek_smi_read_byte1()` implement byte-level protocol and ACK/NACK behavior.
- `realtek_smi_read_reg()` and `realtek_smi_write_reg()` implement 16-bit register transactions under `priv->lock`.
- `realtek_smi_write_reg_noack()` supports reset writes where the chip naturally stops ACKing.
- `realtek_smi_info` provides regmap read/write callbacks to `rtl83xx_probe()`.
- `realtek_smi_probe()`, `realtek_smi_remove()`, and `realtek_smi_shutdown()` export lifecycle hooks for platform drivers.

## Control Flow

Probe calls `rtl83xx_probe()` with SMI regmap callbacks, obtains optional `mdc` and `mdio` GPIO descriptors as outputs, installs the no-ACK write callback, and registers the switch through `rtl83xx_register_switch()`. On failure after common probe, it calls `rtl83xx_remove()` to unwind.

An SMI read transaction takes `priv->lock` with IRQ save, emits start, writes the variant read command and low/high address bytes with ACK checks, reads low data byte with ACK and high data byte with final NACK, emits stop, releases the lock, and returns the 16-bit value. A write follows the same framing with variant write command, address bytes, low data byte, and high data byte with optional ACK suppression.

Remove gets drvdata, unregisters the DSA switch through the common core, and removes common resources. Shutdown delegates to `rtl83xx_shutdown()`.

## State and Persistence

Transport state is in `realtek_priv`: GPIO descriptors for MDC/MDIO, variant command bytes and clock delay, spinlock for command serialization, and no-ACK write pointer. Hardware register state persists on the switch until changed or reset. GPIO directions are driven during transactions and returned to input mode at stop.

## Dependencies and Integration Points

The file depends on GPIO consumer APIs, platform devices, regmap, spinlocks, delays, OF probing, and the common `rtl83xx` core. It exports symbols in the `REALTEK_DSA` namespace for chip platform drivers. It relies on `realtek_variant` fields (`cmd_read`, `cmd_write`, `clk_delay`) selected by the chip driver/core.

## Risks and Edge Cases

SMI timing is hardware-sensitive; too short a `clk_delay` or GPIO latency can cause ACK timeouts. The ACK retry count is fixed at 5. Optional GPIO acquisition can return NULL, but actual bit operations require valid descriptors, so board descriptions must provide working lines. Reset writes need no-ACK behavior or they may falsely fail. Because the transport uses a spinlock with IRQ save, the bit-banged transaction must remain short and non-sleeping aside from `ndelay`.

## Test Signals

Signals include successful platform probe with SMI GPIOs, correct chip detection through SMI regmap reads, successful register writes and reset no-ACK writes, no ACK timeouts under normal operation, DSA switch registration and traffic, clean remove/shutdown, and behavior under forced GPIO/ACK failures.
