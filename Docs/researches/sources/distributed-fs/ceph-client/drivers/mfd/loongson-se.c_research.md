# sources/distributed-fs/ceph-client/drivers/mfd/loongson-se.c

Purpose: Loongson Security Engine MFD controller. It allocates shared DMA command/data memory, initializes the controller, exposes engine command helpers, handles controller/engine interrupts, and registers RNG/TPM child devices.

Important APIs/types/functions: exported `loongson_se_init_engine()`, `loongson_se_send_engine_cmd()`, internal `loongson_se_send_controller_cmd()`, `loongson_se_poll()`, `se_irq_handler()`, `loongson_se_init()`, and `loongson_se_probe()`.

Control flow: probe allocates controller state, initializes completion/locks, reads `dmam_size`, allocates coherent DMA memory, maps MMIO, enables interrupts, requests all platform IRQs, starts the controller and passes DMA address/size, then registers `loongson-rng` and `tpm_loongson` children. Engine init divides DMA memory per engine, assigns command/return buffers, and sends a controller command describing the engine command buffer.

State and persistence: stores MMIO base, spinlock, controller completion, DMA base/size, engine-init mutex, and per-engine command/data buffers/completions. Hardware interrupt status is cleared in the ISR.

Dependencies and integration: ACPI ID `LOON0011`, platform property `dmam_size`, coherent DMA, MMIO register definitions in `loongson-se.h`, MFD core, and child RNG/TPM drivers.

Risks: `devm_kmalloc()` leaves fields uninitialized unless all paths set them; controller command struct fields beyond assigned values should be considered carefully. IRQ request failures are logged but do not abort. DMA partitioning assumes engine0 buffer can serve as command space.

Test signals: ACPI/property binding, DMA allocation size, controller start/set-DMA command completion, IRQ completion for controller and engines, child RNG/TPM engine initialization, timeout/error paths, and concurrent engine init serialization.
