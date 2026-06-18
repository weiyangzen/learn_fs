<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.h -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.h

Purpose: register map, bit definitions, debug macros, hardware-version constants, and private state declaration for the ENE KB3926 CIR driver.

Important APIs and types: `struct ene_device` describes PNP/rc resources, hardware I/O and IRQ, hardware feature flags, extra RX buffer metadata, RX/TX runtime state, TX settings, RX settings, and synchronization primitives. Register macros define indexed I/O ports, firmware sample buffers/flags, IRQ registers for revision B versus C/D, CIR config/data/modulation/carrier registers, fan-input registers, GPIO transmitter selectors, PLL/version registers, and IRQ type bits.

Control flow: `ene_ir.c` uses these definitions to detect hardware revision, configure firmware buffers, select RX inputs, demodulate carrier, feed TX samples, handle interrupts, and manage wake. Function prototypes for `ene_irq_status` and `ene_rx_read_hw_pointer` support cross-use within the C file.

State and persistence: the header defines volatile driver state and hardware register addresses. Some hardware buffer addresses are saved so remove can restore firmware buffer pointers after module reload.

Dependencies and integration points: includes `linux/spinlock.h` and is private to the ENE rc driver. Debug macros rely on the C file's `debug` module parameter.

Risks: many magic register addresses are chip-specific and revision-sensitive. Comments note typos and uncertain protocol knobs, so untested register changes can regress hardware. `struct ene_device` stores caller TX buffer pointers directly during transmit, requiring synchronous completion semantics.

Test signals: compile coverage, static checks that C code and header feature flags match, hardware detection logs for each revision, and RX/TX tests exercising every state field path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ene_ir.h -->
