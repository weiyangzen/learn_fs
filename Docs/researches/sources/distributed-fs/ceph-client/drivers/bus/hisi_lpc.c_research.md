# sources/distributed-fs/ceph-client/drivers/bus/hisi_lpc.c

Purpose: implements the HiSilicon LPC host bridge as an indirect Logical PIO provider, translating Linux I/O port operations into serialized LPC cycles and creating child devices from OF or ACPI firmware descriptions.

Important APIs and types: `struct hisi_lpc_dev` holds the cycle spinlock, MMIO base, and registered `logic_pio_hwaddr`. `hisi_lpc_ops` implements `.in`, `.out`, `.ins`, and `.outs`. ACPI helpers translate child I/O resources, fix known broken firmware resource ranges, and register IPMI or 8250 platform children.

Control flow: probe maps controller registers, registers an indirect PIO range, then either populates OF children or enumerates ACPI children. Each I/O operation translates the logical PIO address to host LPC address, programs operation length/command/address/data FIFO, starts the cycle, polls idle/finished bits, and reads or writes FIFO bytes under `cycle_lock`.

State and persistence: runtime state is the registered PIO range and child platform devices. Hardware register state is programmed per operation; no persistent driver data survives remove. Remove depopulates children and unregisters the PIO range.

Dependencies and integration: depends on `logic_pio`, OF platform population, ACPI resource walking/enumeration, serial8250 platform data, IPMI child matching, MMIO accessors, and spinlock IRQ serialization.

Risks: all LPC cycles are atomic and polling-based; timeout constants assume LPC timing. `outs()` silently stops on write error. ACPI fixups are hard-coded for known firmware defects. Test signals include single and string I/O widths up to four bytes, same-address versus incrementing cycles, timeout/finished error paths, OF child population, ACPI IPMI/UART child creation, resource translation, and remove cleanup.
