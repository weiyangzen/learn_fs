# sources/distributed-fs/ceph-client/drivers/media/pci/saa7164/saa7164-bus.c

Purpose: implements the PCIe firmware message bus ring-buffer transport used by SAA7164 commands and responses.

Important APIs, types, and functions: `saa7164_bus_setup()` initializes `struct tmComResBusInfo` ring pointers and read/write-position register offsets from firmware descriptors. `saa7164_bus_dump()` logs state. `saa7164_bus_verify()` validates ring positions and intentionally `BUG()`s on corrupt state. `saa7164_bus_set()` writes a command/response header plus payload into the set ring. `saa7164_bus_get()` peeks or consumes a response from the get ring.

Control flow: setup maps command/response rings into `dev->bmmio` and calculates position-register offsets from `intfdesc.BARLocation`. Sending verifies inputs and max size, locks the bus, polls for free space with `mdelay(1)` until timeout, converts header fields to little endian, copies header/payload into the ring with wrap handling, updates write position, restores CPU-endian fields, unlocks, and verifies. Receiving locks the bus, checks empty state, reads a header with wrap handling, converts endian fields, optionally returns after peek, validates the expected header, reads payload with wrap handling, advances read position, unlocks, and verifies.

State and persistence: `dev->bus` holds ring base pointers, sizes, max request size, and register offsets. Hardware/firmware read and write positions persist in BAR registers while the device is running. No disk persistence.

Dependencies and integration points: used directly by `saa7164-cmd.c`. Depends on firmware-provided `busdesc` and `intfdesc`, MMIO accessors, `memcpy_toio/fromio`, and the shared device mutex discipline around `bus->lock`.

Risks: corruption invokes `BUG()`, crashing the kernel. Ring wrap math and free-space checks must match firmware exactly. `saa7164_bus_set()` mutates the caller's message header for endian conversion and restores it later; early exits before restore would be dangerous, though current conversion occurs after space wait. Polling with `mdelay()` can burn CPU during firmware stalls. `saa7164_bus_get()` validates consumed messages against caller expectations, so callers must pass the peeked header back unchanged.

Test signals: firmware command traffic during probe, descriptor enumeration, and streaming; bus debug dumps with sane read/write positions; forced split/wrap cases using large commands near ring end; timeout handling when firmware is unresponsive; no `Unexpected msg miss-match` or bus `BUG()` under concurrent command load.
