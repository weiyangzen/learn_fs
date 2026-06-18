# sources/distributed-fs/ceph-client/drivers/bluetooth/hci_ag6xx.c

## Purpose

`hci_ag6xx.c` implements the HCI UART protocol support and setup sequence for Intel AG6xx/iBT 2.1 devices. It provides H4-style packet framing, firmware/BD data application, Intel manufacturing-mode setup, memory patch writes, and HCI UART protocol registration.

## Important APIs, Types, and Functions

- `struct ag6xx_data` holds the RX reassembly SKB and TX queue.
- `struct pbn_entry` describes Intel PBN patch entries: target address, payload length, and payload bytes.
- `ag6xx_open()`, `ag6xx_close()`, `ag6xx_flush()`, `ag6xx_enqueue()`, and `ag6xx_dequeue()` provide HCI UART queue lifecycle and prepend H4 packet type on transmit.
- `ag6xx_recv()` uses `h4_recv_buf()` with ACL/SCO/event packet descriptors.
- `intel_mem_write()` sends vendor opcode `0xfc8e` memory writes in chunks up to 247 bytes.
- `ag6xx_setup()` enters manufacturing mode, reads Intel version, validates AG6xx identity, applies optional `.bddata`, applies `.pbn` patch entries, exits manufacturing mode with reset, sets vendor event mask, and checks BDADDR.
- `ag6xx_init()` and `ag6xx_deinit()` register/unregister `HCI_UART_AG6XX`.

## Control Flow

Opening allocates private data and initializes the TX queue. Setup assigns Intel diagnostic and BDADDR callbacks, enters manufacturing mode, reads version data, and rejects unsupported hardware platform/variant. It first tries to request a board-data file named from hardware platform and variant; failure is nonfatal and patching continues. If the controller already reports a firmware patch number, setup exits manufacturing mode without applying patch firmware. Otherwise it requests the PBN patch file named from hardware and firmware version fields, iterates entries until address `0xffffffff`, writes each patch to controller memory, and exits manufacturing mode with a reset and patched flag.

## State and Persistence

State is per-UART instance: queued TX SKBs and current RX reassembly SKB. Firmware and BD data are loaded from external firmware files but not persisted by this driver. Controller state changes happen through manufacturing mode commands and memory writes.

## Dependencies and Integration Points

The file integrates with `hci_uart`, H4 receive helpers, Intel Bluetooth helper functions in `btintel.h`, Linux firmware loading, and HCI command sync APIs. It registers a protocol rather than a platform/serdev driver.

## Risks

Patch parsing trusts PBN entry lengths after a bounds check that rejects entries whose end reaches or passes the firmware end; this edge condition must remain exact to avoid out-of-bounds reads or rejecting valid terminators. `intel_mem_write()` uses pointer arithmetic on `const void *data`, a GNU C extension accepted by the kernel but sensitive to style changes. Returning early after `btintel_enter_mfg()` failures can leave manufacturing-mode cleanup to the caller/controller reset path. Missing BD data is tolerated, while missing patch firmware is tolerated only by completing without patching, so bring-up failures may appear later.

## Test Signals

Signals include version logs, unsupported platform/variant rejection, successful `.bddata` command, PBN entry progress logs, `Patching complete`, manufacturing-mode exit, vendor event mask setup, and BDADDR checks. Tests should cover already-patched devices, missing optional BD data, missing patch file, malformed PBN lengths, memory write fragmentation boundaries, and UART RX frame reassembly.
