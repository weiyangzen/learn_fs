# sources/distributed-fs/ceph-client/drivers/thunderbolt/dma_port.c

## Purpose

`dma_port.c` implements the DMA configuration based mailbox used to access switch flash/NVM and power operations through the NHI/DMA port. It is designed to work even when a switch is in safe mode, where normal validation and functionality are limited.

## Important APIs, Types, and Functions

`struct tb_dma_port` records the owning switch, NHI port number, mailbox capability base, and a temporary data buffer. Public APIs are `dma_port_alloc()`, `dma_port_free()`, `dma_port_flash_read()`, `dma_port_flash_write()`, `dma_port_flash_update_auth()`, `dma_port_flash_update_auth_status()`, and `dma_port_power_cycle()`.

Internal helpers include `dma_find_port()`, `dma_port_read()`, `dma_port_write()`, `dma_port_wait_for_completion()`, `dma_port_request()`, `dma_port_flash_read_block()`, `dma_port_flash_write_block()`, and `status_to_errno()`. The mailbox uses `MAIL_DATA`, `MAIL_IN`, and `MAIL_OUT` registers, with command/status bitfields for flash read, flash write, flash update authentication, and power cycle.

## Control Flow

Allocation probes candidate NHI ports 3, 5, and 7 by reading port type at config offset 2. If it finds `TB_TYPE_NHI`, it allocates a `tb_dma_port` and uses capability base `0x3e`.

Read and write helpers construct raw control-channel config packets using custom relaxed match/copy callbacks. They do not enforce the normal config-address validation because safe-mode switches expose only restricted behavior. Mailbox requests write a command to `MAIL_IN`, poll until `MAIL_IN_OP_REQUEST` clears, read `MAIL_OUT`, and convert status to errno.

Flash reads and writes are block oriented through `tb_nvm_read_data()` and `tb_nvm_write_data()`. A flash read submits a read command for a dword address and then reads up to 16 dwords from `MAIL_DATA`. A flash write writes the data block first, then submits a write command, using the CSS bit for the CSS magic address range.

Authentication and power-cycle operations submit short mailbox commands with a 150 ms completion wait. Authentication status is read later from `MAIL_OUT` because authenticating a root switch can reset the host controller before a normal synchronous result is observable.

## State and Persistence Behavior

The only kernel state is the allocated DMA-port object. Persistent hardware effects are significant: flash writes update the non-active NVM region, CSS writes update the authentication header area, update-auth can swap active/non-active firmware regions after validation, and power-cycle resets the switch.

`dma_port_flash_update_auth_status()` consumes no local state; it interprets the current mailbox output register and returns `1` when the last status belongs to the update-auth command. `dma_port_flash_write()` enforces `DMA_PORT_CSS_MAX_SIZE` for CSS writes but otherwise delegates alignment and retry handling to the NVM helpers.

## Dependencies and Integration Points

The file depends on `ctl.h` request transport, switch routing from `tb.h`, config-space definitions from `tb_regs.h`, delay/jiffies helpers, and NVM block helpers (`tb_nvm_read_data()` and `tb_nvm_write_data()`). EEPROM/DROM code uses it to copy host-router DROM from NVM when EFI data is unavailable.

It integrates with firmware update flows through NVM read/write/authenticate operations and with safe-mode recovery where the normal switch functionality is not available.

## Risks and Edge Cases

The relaxed response matching accepts packets by route/type/size only and does not verify sequence, address, or error packet details. That is intentional for safe mode but increases stale-response risk if callers issue overlapping requests to the same route. The broader control-channel layer warns that callers should serialize messages for a given switch.

`dma_port_wait_for_completion()` polls with 50 ms request timeouts and ignores timeout reads until the overall deadline. A controller that repeatedly times out on reads may delay failure until the full mailbox timeout.

Address and dword count fields are masked into fixed-width bitfields. Large addresses or block sizes outside what `tb_nvm_*` passes could be truncated. CSS writes are specially bounded, but non-CSS write sizes depend on the common NVM helper respecting the 16-dword mailbox limit.

## Test Signals

Validation should cover NHI port discovery on ports 3/5/7, safe-mode reads that would fail normal validation, mailbox completion polling, status-to-errno mapping, flash read/write retries, CSS size rejection, update-auth asynchronous status, and power-cycle request behavior. Fault tests should inject config read/write timeouts, access/auth errors in `MAIL_OUT`, and route removal during mailbox polling.
