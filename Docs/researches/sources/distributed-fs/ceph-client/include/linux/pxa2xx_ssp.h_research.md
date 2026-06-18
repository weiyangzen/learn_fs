# sources/distributed-fs/ceph-client/include/linux/pxa2xx_ssp.h

Purpose: defines register offsets, bit fields, controller type IDs, device state, and helper APIs for PXA2xx-family SSP/SPI/I2S-style serial ports and related Intel variants.

Important APIs and types: macros cover SSCR/SSSR/SSPSP/SST*/SSACD register offsets and bit fields for PXA25x/PXA27x/PXA3xx, CE4100, Quark X1000, Merrifield, LPSS, and LPT/WPT variants. `enum pxa_ssp_type` identifies controller variants. `struct ssp_device` stores device, list node, clock, MMIO base, physical base, label, port ID, type, use count, IRQ, and OF node. Inline helpers read/write raw registers and enable/disable SSE. APIs under `CONFIG_PXA_SSP` request/free by port or OF node.

Control flow: a client requests an SSP device, programs registers through read/write helpers and bit macros, enables the port, performs transfers through higher-level SPI/serial code, disables when idle, and frees the device. Controller-specific macros select correct FIFO thresholds and data-size fields.

State and persistence: state includes hardware registers, clock enablement, use count, list membership, and MMIO mapping. Register state is hardware runtime state and may reset on suspend or power loss.

Dependencies and integration points: depends on IO accessors, clocks, device/OF model, SPI/SSP platform code, and SoC-specific register layouts. It integrates legacy PXA and Intel SSP controllers with serial/SPI/audio drivers.

Risks and test signals: risks include using wrong variant bit masks, raw MMIO ordering assumptions, unbalanced request/free use counts, enabling before clock/config, FIFO threshold mismatches, and disabled-config callers getting `NULL`. Test probe/request by port and OF, register programming for each supported variant, enable/disable sequencing, suspend/resume restore, SPI transfers, and error paths for busy ports.
