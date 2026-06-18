# sources/distributed-fs/ceph-client/drivers/media/mmc/Kconfig

Purpose: top-level Kconfig include point for media drivers on MMC/SDIO buses.

Important APIs/types/functions: no runtime APIs. The file sources `drivers/media/mmc/siano/Kconfig`, thereby exposing Siano SDIO DVB adapter configuration under the media tree.

Control flow: during configuration, this file delegates all current MMC media options to the `siano` subdirectory.

State/persistence: generated kernel configuration only; no runtime state.

Dependencies/integration: integrated by the broader media Kconfig hierarchy and coupled to the Siano SDIO driver subtree.

Risks/test signals: minimal file, but stale include paths would hide all MMC media options. Kconfig tests should confirm `SMS_SDIO_DRV` remains visible when DVB/MMC prerequisites are enabled.
