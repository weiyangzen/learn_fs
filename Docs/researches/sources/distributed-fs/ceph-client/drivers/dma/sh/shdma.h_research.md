# sources/distributed-fs/ceph-client/drivers/dma/sh/shdma.h

Purpose: defines the SH DMAE hardware-specific wrapper structures used by `shdmac.c` on top of the generic SHDMA base library. It binds generic `struct shdma_*` objects to SH DMAE register layout, platform data, slave configuration, and per-transfer hardware register images.

Important APIs/types/functions: exported definitions are `SH_DMAE_MAX_CHANNELS`, `SH_DMAE_TCR_MAX`, `struct sh_dmae_chan`, `struct sh_dmae_device`, `struct sh_dmae_regs`, and `struct sh_dmae_desc`. Conversion macros include `to_sh_chan`, `to_sh_desc`, `tx_to_sh_desc`, and `to_sh_dev`; only the `to_sh_dev` style is used by `shdmac.c`, while some macros appear stale against the actual `struct sh_dmae_desc` naming.

Control flow: this header has no runtime control flow. It provides the data layout consumed when `shdmac.c` embeds `struct shdma_chan` in `struct sh_dmae_chan`, embeds `struct shdma_dev` in `struct sh_dmae_device`, and embeds `struct shdma_desc` behind `struct sh_dmae_regs` in `struct sh_dmae_desc`.

State and persistence: per-channel state includes the generic SHDMA channel, selected slave config, transfer-size shift, MMIO base, IRQ name, PM error field, and resolved slave address. Per-device state includes the generic SHDMA device, channel pointer array, platform data, global device list node, channel register base, optional DMARS base, CHCR offset, and interrupt-enable bit. Per-descriptor state is a register snapshot containing SAR, DAR, and TCR plus the generic descriptor. No persistent state is represented.

Dependencies and integration points: includes `linux/sh_dma.h`, `linux/shdma-base.h`, DMAengine, interrupt, and list headers. It is tightly integrated with platform data from `struct sh_dmae_pdata` and `struct sh_dmae_slave_config`, and with the callback contract in `include/linux/shdma-base.h`.

Risks: because this is a layout header, ABI-like risks are field order/embedding assumptions between the base library and hardware driver. The macros referencing `struct sh_desc` look inconsistent with this header's `struct sh_dmae_desc`; accidental use would fail compilation. The fixed maximum of 20 channels and 24-bit TCR limit are hardware assumptions that must match platform data.

Test signals: compile coverage of all SH DMAE configurations is the primary signal. Runtime tests should indirectly validate that `sh_dmae_desc` embedding works through `sh_dmae_embedded_desc`, channel pointer arrays do not exceed `SH_DMAE_MAX_CHANNELS`, and platform data CHCR/DMARS fields map correctly to the wrapper state.
