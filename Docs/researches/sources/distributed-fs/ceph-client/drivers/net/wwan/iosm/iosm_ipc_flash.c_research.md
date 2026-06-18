# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_flash.c

Purpose: implements modem flashing over the devlink SIO channel, including PSI transfer, EBL transfer, capability negotiation, SWID reading, flash erase checks, full erase, regional FLS download, and secpack flashing.

Important functions: `ipc_flash_link_establish`, `ipc_flash_boot_psi`, `ipc_flash_boot_ebl`, `ipc_flash_boot_set_capabilities`, `ipc_flash_read_swid`, and `ipc_flash_send_fls`. Internal helpers format EBL packets, compute checksums, validate EBL responses, write payload chunks, poll erase completion, and stream raw image regions.

Control flow: link establishment opens the devlink channel and reads the LER response. PSI is written in ROM phase and waits for a two-byte ACK, with coredump list retrieval on the coredump ACK. EBL is loaded only from PSI execution stage via an RPSI command/length/data handshake, then stores the EBL response. FLS flashing optionally full-erases NAND, sends either `FLASH_SEC_START` for monolithic images or per-region erase/address/raw-write commands, and sends `FLASH_SEC_END` on the last region.

State and dependencies: it mutates `ipc_devlink->param` erase flags and `ebl_ctx` response/capability bytes. It depends on imem devlink read/write, MMIO execution stage, coredump helpers, firmware blobs, devlink status notifications, and sleeps for erase polling. Risks are endian assumptions in response casting, firmware/header size trust, timeout sensitivity, and destructive full erase. Test signals: mocked read/write transcripts, invalid stage rejection, short reads, erase timeout, region splitting, SWID notification, and coredump ACK path.
