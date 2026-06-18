# sources/distributed-fs/ceph-client/drivers/misc/mei/platform-vsc.c

## Purpose
This platform driver adapts Intel Visual Sensing Controller transport (`vsc_tp`) into the generic MEI core by providing a `mei_hw_ops` implementation over SPI/GPIO packet transfers rather than PCI MMIO registers.

## Important APIs, types, and functions
The private hardware structure is `mei_vsc_hw`, holding the transport pointer, readiness flags, write lock count, RX header/length, and aligned TX/RX buffers. Hardware ops include `mei_vsc_hw_start()`, `mei_vsc_hw_reset()`, `mei_vsc_write()`, `mei_vsc_read()`, `mei_vsc_read_slots()`, buffer-depth helpers, interrupt wrappers, and PG stubs. Driver callbacks are `mei_vsc_probe()`, `mei_vsc_remove()`, `mei_vsc_suspend()`, `mei_vsc_resume()`, and event callback `mei_vsc_event_cb()`.

## Control flow and state
Probe receives a `struct vsc_tp *` through platform data from the SPI transport driver, allocates a MEI device plus hardware storage, initializes MEI with `mei_vsc_hw_ops`, marks firmware-version support off, sets `kind = "ivsc"`, registers the transport event callback, registers MEI, starts MEI, and enables runtime PM. Start sets `host_ready`, enables VSC interrupts, and polls a transport read until firmware responds. Interrupt/event work loops while `vsc_tp_need_read()`, dispatching common MEI read/write/completion handlers under `device_lock`.

## State and persistence behavior
State is volatile: VSC readiness booleans, cached RX packet content, TX serialization via `write_lock_cnt`, and MEI core state. Reset toggles VSC firmware through the transport and reinitializes firmware when interrupts are requested. Power gating is effectively disabled (`MEI_PG_OFF`, `pg_is_enabled=false`).

## Dependencies and integration points
It depends on platform devices, runtime PM, timekeeping for host timestamps, unaligned access, common MEI core, and `vsc-tp.h`. It integrates with the SPI VSC transport via callbacks and exported namespace `VSC_TP`; it presents the resulting controller as a normal MEI device.

## Risks and test signals
Risks include malformed RX header/length pairs, over-MTU writes, atomic write-lock imbalance, event callback races with reset/remove, firmware readiness timeouts, and mismatch between MEI slot semantics and transport packet lengths. Test signals include SPI child platform creation, firmware-ready poll success/failure, MEI message read/write, event-driven queue dispatch, suspend rejection while writes are active, remove callback unregistering, and reset plus firmware-loader path coverage.
