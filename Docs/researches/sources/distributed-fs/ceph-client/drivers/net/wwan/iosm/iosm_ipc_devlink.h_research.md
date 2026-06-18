# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_devlink.h

Purpose: declares the IOSM devlink-facing firmware flashing and coredump contract. It defines the firmware image header, RPSI commands, devlink parameter IDs, coredump region metadata, EBL response context, and the `struct iosm_devlink` object tying devlink, PCIe, SIO channel, flash parameters, and coredump regions together.

Important APIs/types: `iosm_devlink_sio`, `iosm_flash_params`, `iosm_devlink_image`, `iosm_ebl_ctx_data`, `iosm_coredump_file_info`, `iosm_rpsi_cmd`, and exported prototypes `ipc_devlink_init`, `ipc_devlink_deinit`, `ipc_devlink_send_cmd`. Constants such as `IOSM_DEVLINK_HDR_SIZE`, `IOSM_EBL_RSP_SIZE`, and `IOSM_NOF_CD_REGION` form ABI-sized parsing limits.

Control flow and integration: implementation users allocate this object during boot-stage imem initialization, open the devlink SIO channel through imem ops, then use the flash and coredump helpers to exchange RPSI/EBL commands with the modem. State is in-memory only: `rx_list`, `read_sem`, `channel_id`, erase flags, EBL response bytes, and region handles. Dependencies include Linux devlink, SKBs, completions, PCIe, and imem ops.

Risks: the packed firmware header and fixed buffer sizes must match firmware tooling exactly; malformed image headers or unexpected component types can drive incorrect flashing behavior. Test signals include devlink registration, parameter read/write, component-type parsing, coredump region registration, command CRC behavior, and erase flag transitions.
