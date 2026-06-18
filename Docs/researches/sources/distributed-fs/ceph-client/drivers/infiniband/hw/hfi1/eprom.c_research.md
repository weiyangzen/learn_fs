# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/eprom.c

Purpose: EPROM controller support and platform configuration extraction for discrete HFI1 devices. It initializes the SPI EPROM controller, reads arbitrary EPROM byte ranges via page reads, and locates a platform configuration file in either legacy partition format or segment/table-of-contents format.

Important APIs/functions: `eprom_init()` resets and wakes the EPROM controller and marks `dd->eprom_available`. `eprom_read_platform_config()` arbitrates EPROM access and returns allocated platform config data. Internal helpers include `read_page()`, `read_length()`, `read_partition_platform_config()`, and `read_segment_platform_config()`. Local metadata types are `struct hfi1_eprom_footer` and `struct hfi1_eprom_table_entry`.

Control flow: initialization only runs for discrete PCI device ID `PCI_DEVICE_ID_INTEL0`, acquires `CR_EPROM`, resets the controller, sets full speed, sends release-powerdown, and releases the resource. Reads acquire `CR_EPROM`, read the last page of the first 128 KiB segment, choose segment mode if `FOOTER_MAGIC` is present, otherwise read partition 1. Segment mode validates footer version, oprom size, table bounds, finds file type `HFI1_EFT_PLATFORM_CONFIG`, validates size and offset arithmetic, then copies file bytes across segments while skipping footer/table space in segment zero. Partition mode reads the 4 KiB config partition, checks `APO=` magic, and trims at trailing `egamiAPO` if found.

State and persistence: hardware-persistent state is the external EPROM contents and SPI controller state. Software persistent state is `dd->eprom_available`; returned buffers are caller-owned. The shared ASIC resource bit prevents concurrent EPROM access across HFI instances.

Dependencies and integration: uses CSR definitions from `chip_registers.h` through `hfi.h`, common definitions, chip resource arbitration, PCI device IDs, and kernel allocation/copy helpers. Platform initialization code can consume this data when EFI variables are absent or unsuitable.

Risks: the EPROM may wrap reads beyond physical size even when addresses fit the command field, so malformed offsets can return unexpected but hardware-valid data. Segment parsing must defend against footer/table overlap, oversized config files, and integer wrap. The 80 second resource timeout reflects erase/write time, so callers can block for a long time. Only discrete chips are supported.

Test signals: EPROM init on discrete and non-discrete devices, resource contention, valid partition and segment images, missing magic, bad footer version, oversize config entry, offset wrap rejection, cross-segment file extraction, and caller validation of returned config bytes.
