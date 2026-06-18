# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge.h

Purpose: is the main shared header for the ddbridge driver. It defines versioning, limits, board/link/port/tuner constants, register map metadata, device identity structures, DMA and DVB state, I2C adapters, ports, LNB state, IRQ slots, links, the top-level device object, and exported core lifecycle APIs.

Important APIs/types/functions: important structs are `ddb_regset`, `ddb_regmap`, `ddb_ids`, `ddb_info`, `ddb_dma`, `ddb_dvb`, `ddb_ci`, `ddb_io`/input/output aliases, `ddb_i2c`, `ddb_port`, `ddb_lnb`, `ddb_irq`, `ddb_link`, and `ddb`. Constants define maximum adapters/ports/links and tuner/CI classes. Prototypes declare flash read, IRQ handlers, port/buffer/device lifecycle, `ddb_init()`, `ddb_unmap()`, and module-level core init/exit helpers.

Control flow: not executable, but all ddbridge C files consume these contracts to share state and call across modules.

State and persistence: describes in-memory runtime state only. Persistent hardware identities are read into `ddb_ids`; durable flash is only read through declared APIs.

Dependencies/integration: includes Linux PCI, I2C, interrupt, workqueue, DVB, demux, CA, net, and ringbuffer headers.

Risks and test signals: structure layout and constants affect all driver modules; changing limits or class/type constants can break array indexing and frontend dispatch. Compile all ddbridge objects and test representative board classes: tuner, CI, loop, MAX, and MCI.
