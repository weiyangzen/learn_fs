# sources/distributed-fs/ceph-client/drivers/net/ethernet/ibm/emac/Kconfig

Purpose: Defines Kconfig options for the IBM EMAC Ethernet family used on 4xx embedded PowerPC chips and Axon southbridge systems.

Important configuration entries: `IBM_EMAC` is the main tristate, depends on `PPC_DCR`, and selects `CRC32` and `PHYLIB`. Tunables `IBM_EMAC_RXB`, `IBM_EMAC_TXB`, `IBM_EMAC_POLL_WEIGHT`, and `IBM_EMAC_RX_COPY_THRESHOLD` configure receive buffers, transmit buffers, NAPI/MAL polling weight, and RX copy threshold. `IBM_EMAC_DEBUG` enables debugging. Hidden platform-selected booleans include `IBM_EMAC_ZMII`, `IBM_EMAC_RGMII`, `IBM_EMAC_TAH`, `IBM_EMAC_EMAC4`, `IBM_EMAC_NO_FLOW_CTRL`, `IBM_EMAC_MAL_CLR_ICINTSTAT`, and `IBM_EMAC_MAL_COMMON_ERR`.

Control flow: This file is sourced from the IBM vendor Kconfig. User-visible options configure the EMAC driver; hidden booleans are selected by SoC/platform code to include connector/accelerator variants and hardware quirks. The EMAC Makefile consumes those symbols to include optional objects.

State and persistence: Values persist in `.config`. Numeric tunables shape compile-time constants or runtime defaults in the EMAC driver; this file itself has no runtime state.

Dependencies and integration: Depends on PowerPC DCR support and integrates with PHYLIB, CRC32, and the IBM EMAC Makefile. Hidden symbols map directly to optional object files such as `zmii.o`, `rgmii.o`, and `tah.o`.

Risks: Buffer/tuning options accept arbitrary integer values in Kconfig; downstream code must validate or tolerate unusual values. Hidden platform selects must match actual hardware topology or required bridge objects will be omitted. The comment notes these options should be selected by processor/platform definitions, so manual edits can create unsupported builds.

Test signals: `CONFIG_IBM_EMAC=m/y` builds, platform configs selecting ZMII/RGMII/TAH/EMAC4, unusual buffer counts and poll weight builds, debug builds, and PHYLIB dependency resolution.
