# sources/distributed-fs/ceph-client/sound/soc/sdca/sdca_interrupts.c

## Purpose
Implements SDCA interrupt chip registration and per-control interrupt dispatch. It maps the SoundWire SDCA interrupt status/mask registers into regmap IRQs and routes parsed control interrupt positions to handlers for function status, jack detected mode, HID reports, FDL ownership, or generic logging.

## APIs, Types, and Functions
Exports `sdca_irq_request()`, `sdca_irq_free()`, `sdca_irq_data_populate()`, `sdca_irq_populate_early()`, `sdca_irq_populate()`, `sdca_irq_cleanup()`, `sdca_irq_allocate()`, `sdca_irq_enable_early()`, `sdca_irq_enable()`, and `sdca_irq_disable()`. Internal handlers include `base_handler()`, `function_status_handler()`, `detected_mode_handler()`, `hid_handler()`, and `fdl_owner_handler()`.

## Control Flow, State, and Persistence
`sdca_irq_allocate()` allocates shared interrupt info, installs a regmap IRQ chip over SDCA INT/INTMASK registers, initializes the IRQ lock, and stores the device regmap into every interrupt slot. Early population scans controls for XU FDL owner interrupts, allocates FDL state, and requests threaded IRQs before component registration. Normal population scans all controls with interrupt positions, populates names/regmap/component/function/entity/control pointers, selects a handler by control type, allocates jack or FDL state as needed, and requests threaded IRQs unless the slot is already claimed. Handlers runtime-resume the device, read/clear function status or call jack/HID/FDL processors, then runtime-put. FDL handler avoids runtime PM waits during system resume. Cleanup frees requested IRQs for a function and releases allocated names. Enable helpers split early FDL IRQ re-enablement from normal IRQ re-enablement after resume.

## Dependencies and Integration
Depends on regmap IRQ, SoundWire SDCA registers, runtime PM, SDCA parser metadata, SDCA FDL/HID/jack helpers, and ASoC components. It is allocated by the class driver and populated by the class function driver during boot and component probe.

## Risks and Test Signals
Risks include duplicate FDL state allocation between early and normal population, handler/runtime PM interactions during suspend/resume, stale `interrupt->name` if cleanup is skipped, base handler masking unimplemented IRQ semantics, function-status recovery left as FIXME, and global SDCA interrupt slot conflicts when multiple controls claim the same position. Test signals are regmap IRQ chip registration, requesting and freeing individual IRQs, early FDL interrupts before card registration, jack/HID/FDL events under runtime suspend, resume IRQ enable ordering, and malformed interrupt positions rejected.
