# sources/distributed-fs/ceph-client/drivers/input/serio/gscps2.c

## Purpose

`gscps2.c` implements the HP GSC PS/2 keyboard/mouse controller driver for PA-RISC workstations. It registers each LASI/DINO PS/2 port as a serio `SERIO_8042` port and handles the shared-interrupt behavior of HP GSC PS/2 hardware.

## Important APIs, Types, and Functions

`struct gscps2port` stores list linkage, PA-RISC device, serio port, spinlock, MMIO base, circular buffer indices, buffered data/status entries, and port ID. Important functions include `wait_TBE()`, `gscps2_flush()`, `gscps2_writeb_output()`, `gscps2_enable()`, `gscps2_reset()`, `gscps2_read_data()`, `gscps2_report_data()`, `gscps2_interrupt()`, serio callbacks `gscps2_write/open/close()`, and PA-RISC driver probe/remove/init/exit.

## Control Flow

Probe verifies an IRQ, adjusts the HPA for DINO variants, allocates state and serio port, maps registers, resets the port, reads keyboard/mouse ID, requests the shared IRQ, validates the ID, registers the serio port, and adds the port to a global list. Opening resets and enables the port, then manually invokes the interrupt handler to flush pending data. The interrupt handler first reads data from every listed port under each port lock, then reports buffered data to serio outside the read phase; if new composite interrupt status appears during reporting, it breaks so the handler can restart. Writes wait for transmit-buffer empty, wait for receive-buffer empty, write the byte under lock, delay, then manually service incoming data.

## State and Persistence Behavior

The driver persists a global list of active PS/2 ports, per-port MMIO mappings, spinlocks, serio ports, and small circular buffers. Hardware state includes enable/reset/control bits, receive/transmit buffers, and shared composite interrupt status. Open/close toggles the controller enable bit.

## Dependencies and Integration Points

The file depends on PA-RISC device infrastructure, shared IRQs, MMIO byte access, spinlocks, delay helpers, and serio core. It integrates with standard PS/2 keyboard/mouse drivers through `SERIO_8042`.

## Risks and Edge Cases

The shared interrupt design requires reading all ports before reporting any bytes to avoid blocking writes while another port has pending data. Buffer indexing uses a 16-entry mask but `gscps2_read_data()` as shown does not advance `append`, which would prevent reporting newly read bytes unless this source variant relies on behavior not visible here; that is a high-value review point. Remove frees `ps2port` but not the separately allocated serio directly, relying on serio unregister ownership. Some memory-region release code is disabled.

## Test Signals

Tests should cover LASI keyboard and mouse ports, shared interrupt storms, write while peer port has data, timeout/parity flag reporting, open reset/enable sequencing, close disable, DINO offset builds if enabled, remove cleanup, and review or instrumentation of circular-buffer append/report behavior.
