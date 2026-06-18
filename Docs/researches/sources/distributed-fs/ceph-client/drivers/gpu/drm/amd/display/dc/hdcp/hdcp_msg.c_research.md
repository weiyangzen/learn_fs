# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hdcp/hdcp_msg.c

Purpose: Implements HDCP message transport for AMD display links. It maps HDCP 1.4/2.2 message ids to HDMI DDC/I2C offsets or DP DPCD AUX addresses, chooses transport by signal type, and retries failed transactions.

Important APIs and functions: `dc_process_hdcp_msg` is the public entry point returning `HDCP_MESSAGE_SUCCESS`, `FAILURE`, or `UNSUPPORTED`. `hdmi_14_process_transaction` builds DDC transactions to HDCP I2C addresses `0x3a/0x3b`. `dpcd_access_helper` chunks DPCD accesses by `DEFAULT_AUX_MAX_DATA_SIZE` and has special repeated handling for KSV FIFO reads. `dp_11_process_transaction` wraps DPCD access. `get_protection_properties_by_signal` maps signal/version to supported processing callbacks.

Control flow: the caller supplies signal, link, and message. The function validates message id, selects a protection backend by signal and HDCP version, attempts the transaction once, then retries up to `message_info->max_retries`. HDMI write transactions allocate a temporary buffer prepended with the register offset; HDMI reads use a two-payload offset-then-read command. DP transactions use DPCD address tables.

State and persistence: no long-lived state is stored. Transient heap memory is used only for HDMI writes and freed after submission. Hardware state changes happen at the sink over DDC/AUX.

Dependencies and integration: depends on `dm_helpers_submit_i2c`, `core_link_read_dpcd`, `core_link_write_dpcd`, link DPCD capabilities, and HDCP message type definitions. Integrated with the HDCP authentication state machine and link service.

Risks and test signals: HDCP 2.2 currently reuses HDMI/DP transport callbacks with TODO comments, so semantic coverage depends on message id tables being correct. KSV FIFO code logs errors for invalid sizes but continues. Tests should cover unsupported DP-VGA dongles, primary/secondary HDMI address selection, AUX chunking boundaries, retry counts, invalid message ids, and KSV FIFO lengths over 635 bytes or not divisible by five.
