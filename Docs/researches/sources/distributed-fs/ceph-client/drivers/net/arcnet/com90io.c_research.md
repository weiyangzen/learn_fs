# sources/distributed-fs/ceph-client/drivers/net/arcnet/com90io.c

## Purpose
`com90io.c` supports legacy COM90xx ARCnet cards whose packet buffers are accessed through I/O-mapped address/data registers rather than directly mapped shared memory. It requires an I/O base address, optionally auto-detects IRQ, validates the card signature, registers a single ARCnet netdev, and implements ARCnet hardware callbacks using programmed I/O.

## Important APIs, Types, and Functions
- `com90io_probe()` validates a specified I/O address, resets the device, checks status flags and signature byte, configures I/O-mapped 8-bit mode, and probes IRQ when none is supplied.
- `com90io_found()` requests the IRQ and I/O region for runtime, installs `arcnet_local.hw` callbacks, reads the station ID, and registers the netdev.
- `get_buffer_byte()`, `get_whole_buffer()`, and `put_whole_buffer()` implement indexed access through COM9026 address and memory-data registers.
- `com90io_reset()`, `com90io_command()`, `com90io_status()`, `com90io_setmask()`, `com90io_copy_to_card()`, and `com90io_copy_from_card()` are the callback table used by the ARCnet core.
- Module parameters `io`, `irq`, and `device` and non-module `com90io=` setup configure the single supported device.

## Control Flow
Initialization allocates an ARCnet device, applies module parameters, normalizes IRQ 2 to 9, and calls the probe. Probe refuses autoprobe without an I/O address, claims the I/O region temporarily, checks for empty status `0xff`, resets by reading `COM9026_REG_R_RESET`, waits, validates post-reset flags, clears reset/config flags, writes I/O-map config, and verifies `TESTvalue` at buffer offset zero. If no IRQ is set, it enables the `NORXflag` interrupt under `probe_irq_on/off()` to discover the line. It then releases the temporary region and calls `com90io_found()`.

Runtime copy callbacks compute `bufnum * 512 + offset`, program high/low address registers with `AUTOINCflag`, and transfer bytes through `COM9026_REG_RW_MEMDATA`. Exit unregisters the netdev, clears `IOMAPflag` to leave the card in memory-mapped mode for old drivers, frees IRQ and region, and frees the ARCnet device.

## State and Persistence
The module stores one global `my_dev`. Runtime state includes `dev->base_addr`, `dev->irq`, `lp->config`, and the registered netdev. Hardware state includes COM9026 config, status, reset, interrupt mask, and buffer address pointer. There is no persistent storage.

## Dependencies and Integration Points
The driver depends on `arcdevice.h` for ARCnet core callbacks and flags and `com9026.h` for register offsets. It integrates with module parameters, legacy boot setup, Linux resource management (`request_region`, `request_irq`), and the generic ARCnet interrupt and TX/RX path.

## Risks
The driver explicitly cannot autoprobe I/O-mapped cards without a base address. Auto-IRQ probing can fail or be unsafe on some systems. Indexed I/O access is stateful, so concurrent unexpected access would corrupt transfer offsets, though the ARCnet core normally serializes hardware operations. The exit path assumes `my_dev` exists after successful init.

## Test Signals
Test evidence includes correct rejection of missing/empty I/O addresses, status and signature validation, IRQ autoprobe or configured IRQ operation, station ID read from buffer byte 1, successful netdev registration, TX/RX data copied through I/O ports, reset recovery, and cleanup restoring memory-mapped mode.
