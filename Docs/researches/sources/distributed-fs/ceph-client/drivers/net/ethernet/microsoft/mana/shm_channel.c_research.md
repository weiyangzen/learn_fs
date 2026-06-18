# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/shm_channel.c

## Purpose
`shm_channel.c` implements the MANA shared-memory channel used by a VF to ask the PF or hardware to establish and destroy the hardware communication channel. It packs queue physical frame addresses and protocol control fields into a 256-bit MMIO shared-memory aperture.

## Important APIs, Types, And Functions
The file defines `union smc_proto_hdr`, a 32-bit hardware protocol header containing message type, version, direction, status, VF reset request, and owner bits. Public entry points are `mana_smc_init`, `mana_smc_setup_hwc`, and `mana_smc_teardown_hwc`. Internal helpers are `mana_smc_poll_register` and `mana_smc_read_response`.

## Control Flow
`mana_smc_init` stores the device and shared-memory base pointer. `mana_smc_setup_hwc` waits until the VF owns the shared memory, validates page alignment for EQ/CQ/RQ/SQ addresses and a 16-bit MSI-X vector, packs the low 48 bits plus high 4 bits of each page frame into the aperture, writes the EQ vector, writes an establish-HWC protocol header in the final dword, then waits for and validates the PF response. `mana_smc_teardown_hwc` similarly waits for ownership, writes a destroy-HWC header into the final dword, and waits for completion so hardware invalidates state before software frees backing memory.

## State And Persistence
The only driver state is `struct shm_channel` with `dev` and `base`. Persistent state lives in device-owned shared memory and hardware ownership bits. Reset handling accepts `0xffffffff` as the shared-memory reset state when `reset_vf` is true.

## Dependencies And Integration Points
The file uses MMIO `readl`/`writel`, `usleep_range`, MANA page-frame macros, and the shared HWC setup protocol defined by MANA hardware. It is called during GDMA/HWC bring-up and teardown before or after queue memory lifetimes.

## Risks
Risks include incorrect address packing, unaligned queue addresses, endian or aliasing assumptions when writing 48-bit fields through `u64 *`, timeouts if ownership does not return, and freeing queue memory before destroy acknowledgment. The reset path must tolerate all-ones reads without treating them as malformed protocol headers.

## Test Signals
Tests should exercise normal HWC setup/teardown, reset requested setup/teardown, invalid unaligned addresses, invalid MSI-X vector values, PF timeout injection, malformed response header fields, nonzero response status, and teardown ordering under device reset.
