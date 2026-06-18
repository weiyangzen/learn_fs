# sources/distributed-fs/ceph-client/drivers/media/common/siano/Kconfig

Purpose: declares common Siano mobile DTV driver configuration symbols.

Important APIs/types: `SMS_SIANO_MDTV` builds common Siano support when DVB core, DMA, and either USB or SDIO transport are present. `SMS_SIANO_RC` enables remote-controller support with RC core and media common options. `SMS_SIANO_DEBUGFS` enables smsdvb debugfs statistics, constrained to debugfs and matching USB/SDIO configuration.

Control flow: Kconfig dependency resolution selects common core, optional IR, and optional debugfs objects through the Makefile.

State/persistence: no runtime state; controls build composition.

Dependencies/integration: integrates Siano common code with transport drivers (`SMS_USB_DRV`/`SMS_SDIO_DRV`), DVB core, RC core, and debugfs.

Risks/test signals: dependency expressions can make optional features unavailable or built with missing transport support. Build matrix tests should cover USB-only, SDIO-only, RC enabled/disabled, and debugfs enabled constraints.
