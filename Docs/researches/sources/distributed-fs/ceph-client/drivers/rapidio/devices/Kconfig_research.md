# sources/distributed-fs/ceph-client/drivers/rapidio/devices/Kconfig

Purpose: declares RapidIO master-port device driver options. In this subset it exposes only the IDT Tsi721 PCI Express Serial RapidIO controller driver.

Important option: `RAPIDIO_TSI721` is a tristate labeled `IDT Tsi721 PCI Express SRIO Controller support`. It depends on `RAPIDIO && PCIEPORTBUS` and defaults to `n`.

Control flow and integration: enabling this symbol causes `drivers/rapidio/devices/Makefile` to build the Tsi721 mport object. When `RAPIDIO_DMA_ENGINE` is also enabled, the Tsi721 DMA support object is linked into the same module.

State and persistence: no runtime state; the selected symbol persists in `.config` and controls whether PCI probing for vendor/device ID Tsi721 is present.

Dependencies: Kconfig symbol `RAPIDIO`, PCIe port bus support, and the Tsi721 PCI hardware.

Risks: the dependency on `PCIEPORTBUS` ensures PCIe services are present but does not by itself guarantee MSI/MSI-X availability or BAR layout compatibility; those are handled at probe time. Default `n` avoids pulling in hardware-specific code unexpectedly.

Test signals: Kconfig dependency tests should verify the option is hidden without `RAPIDIO` or `PCIEPORTBUS`, and module builds should include `tsi721_mport` only when enabled.
