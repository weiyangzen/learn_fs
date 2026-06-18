# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_ls2k.c

Purpose: This platform driver adapts the Loongson-2K BMC KCS register block to the generic IPMI SI engine by providing custom memory-mapped byte input/output callbacks and registering a KCS SMI for `ls2k-ipmi-si` devices.

Important APIs, types, and functions: Register constants describe LS2K FIFO heads/tails, KCS status/data/cmd registers, version register, write request/ack registers, and status bits. Version-specific callbacks are `ls2k_mem_inb_v0`, `ls2k_mem_inb_v1`, `ls2k_mem_outb_v0`, and `ls2k_mem_outb_v1`. `ipmi_ls2k_mem_setup` maps the resource and selects callbacks based on `LS2K_KCS_VERSION`; `ipmi_ls2k_probe` fills `struct si_sm_io`; `ipmi_ls2k_remove` removes by device; init/shutdown register or unregister the platform driver.

Control flow: Probe creates an SI KCS descriptor with custom `io_setup`, base address from the first platform resource, register spacing equal to resource size, and backing device pointer, then calls `ipmi_si_add_smi`. Setup maps the register region and chooses v0 or v1 accessors. Reads and writes emulate the KCS status/data register layout expected by the generic KCS state machine.

State and persistence behavior: The module tracks whether the LS2K platform driver was registered. Per-device state is the mapped I/O address stored in `si_sm_io`, which is unmapped by `ls2k_mem_cleanup`. There is no persistent storage.

Dependencies and integration points: It depends on platform devices named `ls2k-ipmi-si`, MMIO accessors, `FIELD_PREP`, and the generic SI engine. It does not expose a separate IPMI transport; it feeds a customized KCS byte-access layer into `ipmi_si_add_smi`.

Risks and edge cases: The v0 and v1 hardware protocols differ in FIFO/status semantics, so version misdetection would break KCS handshaking. Output callbacks drop writes if input-buffer state says the BMC is busy. Mapping uses resource size as register spacing, so platform resources must be accurate. Shutdown unregisters only if init marked the driver registered.

Test signals: Probe with valid/invalid resources, v0 and v1 version selection, status/data reads reflecting OBF/IBF/CMD bits, write dropping while IBF is busy, write request counter updates, successful integration with generic KCS detect/Get Device ID, remove-time unmap via SI cleanup, and init/shutdown idempotence.
