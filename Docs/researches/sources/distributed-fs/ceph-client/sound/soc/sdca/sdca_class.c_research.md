# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_class.c

## Purpose
SoundWire class-compliant SDCA device driver. It owns the physical SoundWire slave, device-level regmap, attach/detach tracking, top-level IRQ chip allocation, runtime PM cache handling, and creation/removal of auxiliary SDCA function devices.

## APIs, Types, and Functions
Registers `class_sdw_driver` named `sdca_class` with SoundWire IDs `0x01FA:0x4245`, `0x01FA:0x4249`, and `0x01FA:0x4747`. Key helpers are `class_read_prop()`, `class_sdw_update_status()`, `class_wait_for_attach()`, `class_boot_work()`, `class_sdw_probe()`, `class_sdw_remove()`, `class_suspend()`, `class_resume()`, `class_runtime_suspend()`, and `class_runtime_resume()`. Device state is `struct sdca_class_drv` from `sdca_class.h`.

## Control Flow, State, and Persistence
Probe reads SWFT ACPI data, allocates `sdca_class_drv`, copies regmap config, allocates per-function data slots, initializes locks/work/completion, creates a SoundWire regmap in cache-only mode, enables runtime PM, and queues `class_boot_work()`. SoundWire status callbacks set `attached` and complete/reinitialize `device_attach`. Boot work waits up to five seconds for attach, disables cache-only mode, allocates SDCA IRQ data over the device regmap and physical IRQ, registers auxiliary function devices, and arranges devm removal before releasing runtime PM. Runtime suspend marks the device regmap cache-only because bus access may disappear; runtime resume waits for attach, marks the cache dirty, disables cache-only mode, and syncs cached registers. System suspend disables the SoundWire IRQ and force-suspends runtime PM; resume reverses that.

## Dependencies and Integration
Depends on SoundWire slave driver APIs, SoundWire SDCA registers, regmap SoundWire transport, runtime PM, workqueues, completions, `sdca_lookup_swft()`, `sdca_irq_allocate()`, and function-device registration helpers. It imports the `SND_SOC_SDCA` namespace.

## Risks and Test Signals
Risks include asynchronous boot work failing silently except runtime PM state, attach timeout sensitivity, IRQ disabling around system suspend, cache sync correctness after detach/reattach, SoundWire ID coverage limited to listed parts, and function-device removal ordering versus IRQ teardown. Test signals are attach/detach notification, boot work completion after delayed attach, runtime autosuspend/resume with register cache sync, system suspend/resume with IRQ re-enable, auxiliary function device creation for every parsed function, and error paths when IRQ allocation or function registration fails.
