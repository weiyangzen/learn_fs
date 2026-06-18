# sources/distributed-fs/ceph-client/drivers/usb/chipidea/ulpi.c

Purpose: provides ChipIdea ULPI viewport access and registration with the Linux ULPI bus when the platform PHY mode is ULPI. It lets generic ULPI PHY code identify and access an external PHY through ChipIdea controller registers.

Important APIs and functions: `ci_ulpi_wait` polls `OP_ULPI_VIEWPORT` bits with a 10 ms timeout. `ci_ulpi_read` wakes the viewport, starts a read transaction for a ULPI address, waits for `ULPI_RUN` to clear, and returns bits 15:8 as data. `ci_ulpi_write` follows the same wake and run sequence with `ULPI_WRITE` and value bits. `ci_ulpi_init` checks `ci->platdata->phy_mode`, configures PORTSC via `hw_phymode_configure`, fills `ci->ulpi_ops`, and calls `ulpi_register_interface`. `ci_ulpi_exit` unregisters the interface, and `ci_ulpi_resume` waits up to 100 ms for `ULPI_SYNC_STATE`.

Control flow: initialization is conditional and returns success without side effects for non-ULPI modes. Read/write operations always wake the viewport before accessing the target register. Resume is a synchronization check rather than a full reinitialization.

State and persistence: persistent driver state is limited to `ci->ulpi`, `ci->ulpi_ops`, and hardware viewport state. No allocation is owned here beyond the registered ULPI interface object. Timeout failures are returned to callers and logged by init.

Dependencies and integration points: uses ChipIdea hardware helpers, `linux/ulpi/interface.h`, platform PHY mode configuration, and the device driver data that maps an ULPI device back to `struct ci_hdrc`. It integrates the ChipIdea controller with external ULPI PHY drivers.

Risks: busy-wait polling can fail on clocks, reset sequencing, or inaccessible viewport state; read/write paths assume `dev_get_drvdata(dev)` is the ChipIdea controller. Test signals include boot/probe with ULPI PHYs, ULPI ID reads, suspend/resume with sync-state recovery, timeout fault injection, and verifying non-ULPI platforms skip registration.
