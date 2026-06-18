# sources/distributed-fs/ceph-client/drivers/net/arcnet/com90xx.c

## Purpose
`com90xx.c` is the normal shared-memory COM90xx ARCnet chipset driver. It can scan legacy I/O ports and shared memory windows, match a reset controller to its buffer memory, detect memory mirrors, register ARCnet devices, and implement the ARCnet hardware callbacks using `memcpy_toio()`/`memcpy_fromio()` over mapped card memory.

## Important APIs, Types, and Functions
- `com90xx_probe()` performs the five-stage legacy probe across possible I/O ports and shared memory addresses.
- `check_mirror()` tests whether adjacent shared-memory windows mirror the same card buffer.
- `com90xx_found()` allocates and initializes a netdev for a matched port/IRQ/shared-memory tuple, reserves the full mirrored memory range, maps it, reads station ID, installs callbacks, and registers the device.
- `com90xx_reset()`, `com90xx_command()`, `com90xx_status()`, `com90xx_setmask()`, `com90xx_copy_to_card()`, and `com90xx_copy_from_card()` are the ARCnet hardware callback set.
- Global `cards[16]` and `numcards` track registered devices for module exit.

## Control Flow
Probe builds candidate port and shared-memory lists from module parameters or defaults (`0x200..0x3f0` ports and `0xA0000..0xFF800` memory in 2 KiB steps). Stage 1 filters reserved or empty ports and resets plausible controllers. Stage 2 waits for reset completion. Stage 3 maps candidate memory windows, checks the ARCnet signature, verifies writability, and marks mirrors by overwriting the signature. Stage 5 validates controller status, clears reset/config flags, optionally probes IRQ, resets the controller again, and finds which shared-memory window regained the signature. A successful pair is passed to `com90xx_found()`.

`com90xx_found()` allocates a device, determines the real mirrored memory range by walking backward and forward with `check_mirror()`, reserves and maps that entire range, requests IRQ, fills the ARCnet callback table, reads the station ID, registers the netdev, and stores it in `cards`. Runtime packet transfers directly copy to/from `lp->mem_start + bufnum * 512 + offset`. Exit iterates registered cards, unregistering netdevs, freeing IRQs, unmapping memory, releasing I/O and memory regions, and freeing devices.

## State and Persistence
Runtime state is tracked in `cards[]`, `numcards`, `dev->base_addr`, `dev->irq`, `dev->mem_start/end`, and `arcnet_local.mem_start`. Hardware state includes reset/config/status registers and shared packet memory. No disk persistence exists. The probe mutates candidate shared memory and later restores `TESTvalue` for leftover windows.

## Dependencies and Integration Points
The file depends on `arcdevice.h`, `com9026.h`, Linux resource APIs, I/O mapping APIs, module parameters, boot setup parsing, and the generic ARCnet core. It is the memory-mapped counterpart to `com90io.c`.

## Risks
Legacy probing touches broad low-memory ranges and I/O ports, so false positives or platform conflicts are possible despite resource checks. The probe logs one `arc_cont()` line using `*p` in the match print path where the loop variable is not the matched pointer, which is suspicious for diagnostics. Mirror detection depends on `TESTvalue` behavior and can mis-size unusual cards. `cards[16]` bounds the number of registered cards.

## Test Signals
Important signals are each probe stage pruning expected candidates, successful status/reset clearing, IRQ detection, correct shared-memory pairing, mirror range sizing, station ID read, netdev registration, packet transfer by mapped memory, and clean multi-card module exit. Tests should include parameter-specified and scanned configurations, no-card systems, mirrored-memory cards, and reset failure paths.
