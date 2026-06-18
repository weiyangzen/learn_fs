# sources/distributed-fs/ceph-client/sound/soc/sprd/sprd-mcdt.h

Purpose: public header for the Spreadtrum MCDT controller API. It defines channel types, DMA request IDs, callback shape, the opaque-to-users `sprd_mcdt_chan` carrier, and stubs for builds where `CONFIG_SND_SOC_SPRD_MCDT` is disabled.

Important APIs and types: `enum sprd_mcdt_channel_type` distinguishes DAC, ADC, and unknown channels. `enum sprd_mcdt_dma_chan` exposes five MCDT DMA request lanes. `struct sprd_mcdt_chan_callback` carries a `notify(void *data)` hook. `struct sprd_mcdt_chan` records controller pointer, channel ID, FIFO physical address, type, DMA channel, callback, mode flags, and list linkage. API declarations mirror the exported symbols in `sprd-mcdt.c`: request/free, FIFO read/write, interrupt enable/disable, and DMA enable/disable.

Control flow and integration: users include this header to request an ADC or DAC channel, inspect `fifo_phys` for DMA slave configuration, and select manual FIFO, interrupt-driven FIFO, or DMA-driven transfer. The compile-time guard provides callable fallback stubs so dependent drivers can build without hard dependency; most stubs fail with `-EINVAL`, `sprd_mcdt_request_chan()` returns NULL, and `sprd_mcdt_chan_read()` returns 0.

State and persistence: the header intentionally warns users not to modify `struct sprd_mcdt_chan` members, but the structure is not fully opaque. Its fields are shared with the controller implementation and client drivers, so ABI-like field assumptions can leak between modules.

Dependencies: requires Linux list and scalar types through surrounding kernel includes. Real function bodies depend on `CONFIG_SND_SOC_SPRD_MCDT`; otherwise static inline-looking non-static stubs are emitted from the header.

Risks: the disabled-config stub functions are defined in the header without `static inline`, which can create multiple-definition risk if included in multiple translation units in configurations where the real driver is off. Exposed mutable state lets clients accidentally corrupt mode flags or list linkage. The `dma_chan` member is declared but the implementation primarily uses local DMA selection and does not consistently update this field.

Test signals: build both with and without `CONFIG_SND_SOC_SPRD_MCDT`, including multiple includers in the disabled configuration; run sparse/modpost for duplicate symbol issues; validate client drivers do not write to `sprd_mcdt_chan` internals; confirm disabled stubs make dependent modules degrade cleanly.
