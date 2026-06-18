<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/da8xx_remoteproc.c -->
# sources/distributed-fs/ceph-client/drivers/remoteproc/da8xx_remoteproc.c

Purpose: Implements the DA8xx/OMAP-L13x DSP remoteproc platform driver, including DSP start/stop, virtqueue interrupt handling, internal memory mapping, reserved-memory setup, and firmware selection.

Important APIs and types: `struct da8xx_rproc_mem` describes mapped DSP internal memory with CPU, bus, device, and size fields. `struct da8xx_rproc` stores the rproc handle, memories, DSP clock/reset, IRQ data, CHIPSIG registers, and boot register. `da8xx_rproc_ops` provides `.start`, `.stop`, and `.kick`. The module parameter `da8xx_fw_name` selects firmware, defaulting through remoteproc allocation if unset.

Control flow: Probe allocates an rproc, disables recovery, gets clock and reset, initializes reserved memory when OF is present, maps L2/L1P/L1D internal memories, gets IRQ data, maps CHIPSIG and HOST1CFG, requests a threaded IRQ, asserts reset, then adds the rproc. Start validates 1 KiB boot alignment, writes boot address, enables the clock, and deasserts reset. Stop asserts reset and disables the clock. IRQ top half clears CHIPSIG0 and acks the level interrupt; thread polls both vrings.

State and persistence: Runtime state is owned by `struct rproc` and `struct da8xx_rproc`. Hardware state includes boot address, reset line, clock enable, and CHIPSIG interrupt bits. Reserved CMA attachment persists until devm cleanup releases it.

Dependencies and integration points: Depends on remoteproc core, firmware loader, clk/reset frameworks, platform resources named `l2sram`, `l1pram`, `l1dram`, `chipsig`, and `host1cfg`, OF reserved memory, and IRQ controller ack callbacks.

Risks: The interrupt handler directly calls `irq_data->chip->irq_ack`, assuming the chip supplies a valid ack method. Error recovery is disabled. Every interrupt polls vring 0 and 1 because no queue index is encoded. Boot address alignment is a hard hardware constraint.

Test signals: Probe with all named resources, reserved-memory missing/present cases, start with aligned and unaligned boot addresses, reset/clock failure paths, CHIPSIG0 interrupt delivery and clearing, kick writes to CHIPSIG2, vring message processing, and remove/devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/remoteproc/da8xx_remoteproc.c -->
