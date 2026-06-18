# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_common.h

- Purpose: Shared Mantis definitions: debug macro, MMIO helpers, PCI ID helpers, board configuration contract, and the central device state object.
- Important APIs/types/functions: `dprintk`, `mmread/mmwrite`, `MAKE_ENTRY`, `enum mantis_i2c_mode`, `struct mantis_hwconfig`, `struct mantis_pci_drvdata`, `struct mantis_pci`, `mantis_mask_ints()`, `mantis_unmask_ints()`.
- Control flow: Consumers include this header to access MMIO through the local `mantis` variable convention and to mutate device-wide state. Board files fill `mantis_hwconfig`; probe copies it into `mantis_pci`; helpers serialize interrupt mask updates with `intmask_lock`.
- State and persistence: `struct mantis_pci` owns all live kernel resources: PCI/MMIO, RISC DMA buffers, workqueues, I2C adapter, DVB adapter/demux, frontend pointer, CA state, UART work, and rc-core state. It is volatile per-device state only.
- Dependencies and integration points: Connects Linux PCI, DVB, I2C, workqueue, mutex/spinlock, UART and CAM link headers. `MAKE_ENTRY` embeds compound-literal driver data in PCI ID rows.
- Risks: The debug macro assumes a visible variable named `mantis`; misuse in another scope will fail or log the wrong device. Interrupt helpers require valid MMIO and initialized spinlock. Compound literal lifetime in static PCI tables relies on file-scope static storage semantics.
- Test signals: Compile coverage is the main header test; runtime signals are correct verbose logging, safe interrupt mask transitions, and board configs carrying sane power/reset/I2C/TS settings.
