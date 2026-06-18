# sources/distributed-fs/ceph-client/drivers/gpib/cec/cec_gpib.c

Purpose: implements the `cec_pci` GPIB board type for CEC PCI/PCMCIA boards. It is mostly a board-specific wrapper around the shared NEC7210 core, adding PCI discovery for vendor `0x12fc`, device `0x5cec`, subsystem `0x9050`, PLX9050 interrupt enablement, and resource ownership.

Important APIs and functions: `cec_pci_interface` registers `attach`, `detach`, read/write/command/control/address/poll/EOS/status callbacks with `gpib_register_driver`. `cec_interrupt()` serializes through `board->spinlock` and delegates to `nec7210_interrupt`. `cec_generic_attach()` allocates `struct cec_priv`, initializes `nec7210_priv`, and selects IO-port access via `nec7210_ioport_read_byte` and `nec7210_ioport_write_byte`. `cec_pci_attach()` finds the PCI device, enables it, requests BAR regions, stores PLX and NEC IO bases, requests the hardware IRQ and a pseudo IRQ, initializes the chip, then enables PLX local and PCI interrupts.

Control flow and state: online setup is `gpib_common` `IBONL` -> `cec_pci_attach()` -> NEC reset/clock/online -> PLX interrupt enable. Runtime I/O calls are thin pass-throughs to NEC7210 helpers using `board->private_data`. Detach frees pseudo IRQ, disables PLX interrupts, frees IRQ, resets the NEC7210, releases PCI regions, drops the PCI reference, and frees private memory.

Dependencies and integration: depends on `cec.h`, `gpibP.h`, `nec7210` helpers, Linux PCI/IRQ/IO-port APIs, and the common GPIB driver registry. `cec_pci_probe()` is intentionally a no-op because user-space configuration selects a board through the GPIB ioctl path.

Risks: several attach failure paths return before unwinding earlier allocations, such as after `pci_enable_device`, `pci_request_regions`, IRQ allocation, or pseudo IRQ allocation. A `gpib_register_driver` failure after successful `pci_register_driver` does not unregister the PCI driver. `line_status` and local parallel poll mode are unimplemented, reducing status fidelity and command acceptor checks.

Test signals: build with `CONFIG_GPIB_CEC`; verify module registration/unregistration; exercise `CFCBOARDTYPE=cec_pci`, `IBONL`, read/write/command paths, IRQ delivery, pseudo IRQ polling, and detach after partial attach failures. Hardware tests should confirm PLX interrupt masking, NEC7210 reset/clock programming, and selected PCI bus/slot/device-path filtering.
