# sources/distributed-fs/ceph-client/drivers/spmi/spmi-apple-controller.c

## Purpose

`spmi-apple-controller.c` implements the Apple SoC SPMI controller used on Apple Silicon platforms such as t8103. It provides minimal read and write callbacks for the SPMI framework using a command register, response FIFO register, and status polling.

## Important APIs, Types, And Functions

`struct apple_spmi` stores the MMIO register base. Register constants describe status, command, and response offsets plus the RX FIFO empty bit. `apple_spmi_pack_cmd()` encodes opcode, SID, address, length, and an enable/control bit. Runtime helpers are `apple_spmi_wait_rx_not_empty()`, `spmi_read_cmd()`, `spmi_write_cmd()`, and `apple_spmi_probe()`.

## Control Flow And State

Probe allocates a devres-managed SPMI controller, maps the first platform MMIO resource, assigns the OF node to the controller device, sets `read_cmd` and `write_cmd`, and adds the controller. Reads write a packed command, wait until the RX FIFO has a response, discard the reply status word, and then drain response words into the caller buffer a byte at a time. Writes write the packed command, stream payload bytes in 32-bit little-endian chunks through the command register, wait for a response, and discard the status word.

## State And Persistence Behavior

The only persistent software state is the MMIO base stored for the platform device lifetime. Transactions are synchronous and polling-based. The code does not keep an explicit software lock, so serialization relies on the SPMI core or the controller being safe for framework callback concurrency.

## Dependencies And Integration Points

The driver integrates with platform-device probing, `devm_platform_ioremap_resource()`, `readl_poll_timeout()`, OF matching for `"apple,t8103-spmi"` and `"apple,spmi"`, and the SPMI framework's devres-managed controller lifecycle.

## Risks And Test Signals

Risks include the absence of a local transfer lock, no explicit opcode/length validation beyond what the core may provide, a suspicious bitwise `&` in the write-loop condition where logical `&&` would be conventional, and limited response-status interpretation because status words are discarded rather than decoded. Test signals are probe on supported Apple SoCs, reads and writes of 1 through multiword lengths, RX FIFO timeout handling, concurrent SPMI client traffic, invalid opcode/length propagation from the core, and checking whether failed SPMI status replies are observable elsewhere.
