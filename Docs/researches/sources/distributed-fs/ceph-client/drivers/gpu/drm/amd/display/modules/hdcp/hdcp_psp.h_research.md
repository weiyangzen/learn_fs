# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/modules/hdcp/hdcp_psp.h

Purpose: declares the firmware ABI data structures, enums, command IDs, status values, and message sizes used by `hdcp_psp.c` to communicate with the PSP HDCP and DTM trusted applications.

Important APIs/types: DTM command IDs include topology update v2/v3 and ASSR enable; DTM inputs carry display handle, controller/DDC/encoder identifiers, MST VCID, ASSR, PHY, link capability, and DPIA/direct output metadata. HDCP command IDs cover HDCP1 sessions/auth/encryption, HDCP2 session/messages/encryption, destroy-all, and SRM get/set. Message ID enums define all HDCP2 AKE, LC, SKE, repeater-auth, and DP content-type messages.

Control flow role: this header has no executable control flow but defines the layout consumed by PSP shared memory. `ta_hdcp_shared_memory` and `ta_dtm_shared_memory` wrap command ID, status, and input/output unions.

State and persistence: structures carry session handles, SRM buffers, generated transmitter messages, receiver messages, authentication status, HDCP version, KM-stored flag, repeater flag, content type, and encryption protection level.

Dependencies and integration: includes PSP/amdgpu-facing declarations such as `psp_cmd_submit_buf` and expects `struct psp_context` / firmware command definitions from the AMDGPU driver. `hdcp_psp.c` treats these definitions as packed firmware contracts.

Risks: any enum renumbering, field-size change, or union change can break firmware compatibility. Buffer maxima (`TA_HDCP__HDCP2_TX_BUF_MAX_SIZE`, `TA_HDCP__HDCP2_RX_BUF_MAX_SIZE`, SRM max size) bound `memcpy` operations elsewhere. The header intentionally mirrors PSP requirements, so cleanup refactors are dangerous.

Test signals: compile-time size/layout assertions against firmware documentation, command serialization tests, HDCP2 max-message buffer tests, SRM size boundary tests, and DTM v2/v3 topology command compatibility.
