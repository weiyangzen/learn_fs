# sources/distributed-fs/ceph-client/drivers/i2c/busses/scx200_acb.c

## Purpose

`scx200_acb.c` supports National Semiconductor SCx200 ACCESS.bus controllers and AMD CS5535/CS5536 platform variants. It exposes SMBus transactions through a polling state machine over I/O ports.

## Important APIs, Types, and Functions

`struct scx200_acb_iface` stores list linkage, adapter, I/O base, mutex, state machine state, result, address/command, data pointer, reset flag, and length. `scx200_acb_machine()` advances protocol states, `scx200_acb_poll()` waits for status events, `scx200_acb_reset()` initializes hardware, and `scx200_acb_smbus_xfer()` implements SMBus protocol entry.

## Control Flow

Module init first scans ISA-style base addresses when SCx200 PCI bridge IDs are present; if none are created it registers a platform driver for `cs5535-smb`. Device creation reserves eight I/O ports, probes register behavior, resets hardware, and registers an adapter. A transfer initializes state, issues START, selects quick/address state, polls until idle, resets on error, converts word endianness after reads, and returns the state-machine result.

## State and Persistence Behavior

Each interface is protected by `iface->mutex`. `needs_reset` triggers hardware reset after bus or timeout errors. ISA-created interfaces are tracked in a global list for cleanup. The controller is left enabled after reset and adapter registration.

## Dependencies and Integration Points

It depends on platform devices, PCI presence checks for ISA probing, I/O port reservation, `linux/scx200.h`, and SMBus algorithm callbacks. Module parameter `base[]` controls ISA scan addresses.

## Risks

The polling loop spins until a short timeout, with `cpu_relax()` and `cond_resched()`, so slow hardware can produce `-EIO`. The state machine handles only a limited SMBus/I2C-block subset and rejects zero-length reads. ISA scan ignores individual creation failures if another interface succeeds. Direct port access and manual resource lifetime require strict cleanup.

## Test Signals

Validate ISA and platform discovery, I/O readback probe failure, SMBus quick/byte/byte-data/word/I2C-block transfers, read NAK as `-ENXIO`, bus error reset, timeout reset, little-endian word read conversion, multiple base addresses, platform remove, and module cleanup of ISA-created adapters.
