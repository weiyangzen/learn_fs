# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/pt3.h

Purpose: Internal header for the Earthsoft PT3 driver, defining FPGA registers, I2C command-buffer limits, DMA descriptor formats, per-adapter and board state, adapter configuration structures, and cross-file prototypes.

Important APIs, types, and functions: Register macros cover system, I2C, RAM, and per-frontend DMA register blocks. I2C state is `struct pt3_i2cbuf`. DMA types include `struct xfer_desc`, `struct xfer_desc_buffer`, and `struct dma_data_buffer`, with constants for 188-byte TS packets, 4096-byte transfers, 47 transfers per data buffer, and 2..16 data buffers. Runtime state is `struct pt3_adapter` and `struct pt3_board`. Prototypes expose DMA functions from `pt3_dma.c` and I2C functions from `pt3_i2c.c`.

Control flow: No executable control flow. The macros and structures are used by `pt3.c`, `pt3_dma.c`, and `pt3_i2c.c` to coordinate the driver.

State and persistence: Defines but does not allocate state. `struct pt3_board` persists for the PCI device lifetime; `struct pt3_adapter` persists for each of four frontends. DMA descriptor structures are shared with hardware and therefore have a fixed layout.

Dependencies and integration points: Includes Linux atomic/types and DVB demux/frontend/dmxdev headers, plus TC90522, MXL301RF, and QM1D1C0042 tuner/frontend headers. It is the private contract between the PT3 source files.

Risks: DMA constants must satisfy the comment that `(num_bufs * DATA_BUF_SZ) % TS_PACKET_SZ == 0`; changes can break demux packet alignment. DMA transfers must not cross 4 GiB, so `DATA_XFER_SZ` and descriptor construction are hardware constraints. `PT3_I2C_MAX` and command nibble packing must stay aligned with internal memory layout.

Test signals: Compile all PT3 files after header edits, validate descriptor struct size against `DESCS_IN_PAGE`, assert data-buffer divisibility by TS packet size, and run DMA ring construction tests for min/max `num_bufs`.
