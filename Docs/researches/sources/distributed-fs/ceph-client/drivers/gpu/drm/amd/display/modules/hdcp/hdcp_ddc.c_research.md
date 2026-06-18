# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_ddc.c

Purpose: provides the HDCP DDC/AUX transport implementation for HDCP 1.x and 2.2 messages. It maps logical HDCP message IDs to HDMI I2C offsets or DP DPCD addresses, chunks DP AUX transfers to 16 bytes, and copies protocol data into `hdcp->auth.msg`.

Important APIs: exported functions include HDCP1 reads/writes (`mod_hdcp_read_bksv`, `mod_hdcp_read_bcaps`, `mod_hdcp_read_bstatus`, `mod_hdcp_read_r0p`, `mod_hdcp_read_ksvlist`, `mod_hdcp_read_vp`, `mod_hdcp_write_aksv`, `mod_hdcp_write_ainfo`, `mod_hdcp_write_an`) and HDCP2 operations (`mod_hdcp_read_hdcp2version`, `mod_hdcp_read_rxcaps`, `mod_hdcp_read_rxstatus`, `mod_hdcp_read_ake_cert`, `mod_hdcp_write_ake_init`, `mod_hdcp_write_no_stored_km`, `mod_hdcp_write_stored_km`, `mod_hdcp_write_lc_init`, `mod_hdcp_write_eks`, `mod_hdcp_read_rx_id_list`, `mod_hdcp_write_stream_manage`, `mod_hdcp_write_content_type`, `mod_hdcp_clear_cp_irq_status`, `mod_hdcp_write_poll_read_lc_fw`).

Control flow: common `read()` and `write()` validate message IDs, select DP DPCD or HDMI I2C based on `is_dp_hdcp(hdcp)`, and call function pointers in `hdcp->config.ddc.funcs`. DP HDCP2 messages skip the message ID byte for writes and synthesize it for reads. Receiver-id-list reads are special: DP reads an initial block, derives device count, and reads the remaining aligned portion.

State and persistence: mutates `hdcp->auth.msg.hdcp1`, `hdcp->auth.msg.hdcp2`, and scratch buffer `hdcp->buf`. It does not own authentication state but its byte layout directly feeds PSP validation and logging.

Dependencies and integration: depends on DDC callbacks supplied by the display manager and on HDCP bitfield macros from included headers. Atomic locality helpers use `atomic_write_poll_read_i2c` or `atomic_write_poll_read_aux`.

Risks: offset/address tables are protocol-critical. Buffer sizing, the DP receiver-id-list second-part length expression, and I2C write staging in `hdcp->buf` are sensitive to overflow and off-by-one mistakes. CP_IRQ clear chooses ESI0 for DP 1.4+ links.

Test signals: mock DDC callbacks for HDMI and DP, verify byte offsets, chunked AUX transactions, message-ID inclusion/exclusion, locality combo failures, CP_IRQ clear address selection, and error propagation on failed reads/writes.
