# sources/distributed-fs/ceph-client/drivers/media/pci/ngene/ngene.h

Purpose: Shared private header for the nGene driver. It defines hardware register offsets, firmware command ABI structures, DMA/ringbuffer descriptors, stream/channel/device state structures, card metadata, and cross-file prototypes.

Important APIs, types, and functions: Key structures include `struct ngene_command`, packed firmware payload structs such as `FW_I2C_READ`, `FW_STREAM_CONTROL`, and `FW_CONFIGURE_FREE_BUFFERS`, DMA structures `SBufferHeader` and `SRingBufferDescriptor`, per-channel `struct ngene_channel`, CI state `struct ngene_ci`, device state `struct ngene`, and board descriptor `struct ngene_info`. It defines stream enums, mode/flag bits, firmware opcodes, buffer size constants, shared-memory offsets, DEMOD_TYPE values, and prototypes for functions implemented in core/cards/i2c/dvb files.

Control flow: The header has no executable control flow. Its packed command and descriptor layouts are consumed by firmware command construction, DMA descriptor allocation, and channel setup across the implementation files.

State and persistence: The header defines the software state containers but does not instantiate state. `struct ngene` is the top-level runtime object. `struct ngene_channel` persists per stream until device removal. Packed firmware and DMA descriptor fields mirror hardware/firmware-visible state and must preserve layout.

Dependencies and integration points: Pulls in Linux I2C, interrupt, scatterlist, DVB frontend/demux/net/ringbuffer/CA headers, workqueues, and the CXD2099 CA header. It is included by every nGene source file and forms the internal ABI between them.

Risks: Many structures are packed hardware/firmware contracts; field reordering, alignment changes, or type-size changes can break DMA or command exchange. The header mixes legacy analog/audio fields with current DVB paths, increasing maintenance surface. `struct ngene_info` uses arrays indexed by stream number, so card metadata must stay exactly aligned with `MAX_STREAM`.

Test signals: Build coverage should include all nGene source files after any header edit. Higher-value validation includes `sizeof`/offset checks for packed firmware structs against firmware documentation, channel array index tests for each card_info, and DMA descriptor ring tests that confirm physical pointers match the expected packed fields.
