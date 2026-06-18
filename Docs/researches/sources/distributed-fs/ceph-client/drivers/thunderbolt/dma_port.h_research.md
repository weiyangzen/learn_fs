# sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_port.h

## Purpose

`dma_port.h` declares the Thunderbolt DMA-port mailbox interface used for switch NVM flash access and switch power/authentication operations. It hides the concrete `struct tb_dma_port` implementation from callers and exposes a small API for allocation, flash reads/writes, authentication, authentication status, and power cycling.

## Important APIs, Types, and Functions

The header forward-declares `struct tb_switch` and `struct tb_dma_port`. It defines `DMA_PORT_CSS_ADDRESS` as the magic CSS write address and `DMA_PORT_CSS_MAX_SIZE` as the maximum CSS write size. Public functions are `dma_port_alloc()`, `dma_port_free()`, `dma_port_flash_read()`, `dma_port_flash_write()`, `dma_port_flash_update_auth()`, `dma_port_flash_update_auth_status()`, and `dma_port_power_cycle()`.

## Control Flow

Callers allocate a DMA port for a switch, use the returned object for block-oriented NVM operations, then release it. Flash reads target the active region; flash writes target the non-active region except CSS writes, which use the fixed CSS address. Authentication is split into request and later status polling so root-switch resets can be handled by higher layers.

## State and Persistence Behavior

The header itself stores no state. The object returned by `dma_port_alloc()` represents a mailbox endpoint for one switch. Calls can produce persistent hardware effects: non-active NVM contents can change, firmware authentication can trigger active image swap, and `dma_port_power_cycle()` can reset the switch.

## Dependencies and Integration Points

The header includes `tb.h` for switch definitions and size macros. It is consumed by EEPROM/DROM and NVM update code that needs safe-mode-compatible flash access without exposing mailbox register details.

## Risks and Edge Cases

The API does not expose locking requirements, so callers must rely on the surrounding Thunderbolt domain lock and control-channel serialization. Address and size semantics are hardware-specific; callers must pass byte addresses and sizes acceptable to the NVM helpers and mailbox implementation.

Because authentication status is separate from authentication start, callers must handle controller reset or disappearance between calls and must not assume `dma_port_flash_update_auth()` returning success means the image was accepted.

## Test Signals

Build coverage should ensure all users include the header cleanly. Functional tests should allocate/free on switches with and without DMA capability, read flash data, reject oversize CSS writes, write non-active flash blocks, start authentication, poll status, and power-cycle a test switch or mocked mailbox.
