# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/Kconfig

Purpose: Kconfig menu for HyperBus/HyperFlash support and two controller drivers.

Important APIs/types/functions: `menuconfig MTD_HYPERBUS` enables the framework, depends on `HAS_IOMEM`, and selects CFI/map prerequisites. `config HBMC_AM654` enables TI AM65x HyperBus controller support, depends on `ARCH_K3 || COMPILE_TEST`, selects `MULTIPLEXER`, and implies `MUX_MMIO`. `config RPCIF_HYPERBUS` enables Renesas RPC-IF HyperBus support, depends on `RENESAS_RPCIF` and `MTD_CFI_BE_BYTE_SWAP`.

Control flow: build-time only. Enabling the menu exposes child controller options; child symbols compile their respective objects through the Makefile.

State and persistence: no runtime state. The symbols determine which code is built and which dependencies are forced into the kernel configuration.

Dependencies/integration: integrates HyperBus with MTD CFI AMD-standard probing and complex mappings. Controller configs ensure their platform helper frameworks are present.

Risks: incorrect dependencies can produce build failures or runtime-incomplete drivers. `RPCIF_HYPERBUS` specifically requires byte-swap CFI behavior, so testing on big/little endian mappings matters.

Test signals: `allmodconfig`/`COMPILE_TEST` builds, dependency visibility in menuconfig, and object inclusion for `MTD_HYPERBUS`, `HBMC_AM654`, and `RPCIF_HYPERBUS`.
