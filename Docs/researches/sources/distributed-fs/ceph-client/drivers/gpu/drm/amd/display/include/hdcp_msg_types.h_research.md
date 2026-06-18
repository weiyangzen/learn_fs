# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/include/hdcp_msg_types.h

Purpose: Defines the message IDs and message envelope used by AMD DC HDCP DDC/AUX transaction code. It covers HDCP 1.4, HDCP 2.2, and PS175 bridge messages.

Important APIs and types: `enum hdcp_message_id` enumerates read/write operations such as BKSV, R0/Ri, V prime, BCAPS/BSTATUS/KSV FIFO/BINFO, HDCP2 AKE/LC/SKE/repeater messages, RXSTATUS, content stream type, and PS175 command/response. `enum hdcp_version`, `enum hdcp_link`, `enum hdcp_message_status`, and `struct hdcp_protection_message` describe transaction context and result.

Control flow: Higher-level HDCP code fills a `hdcp_protection_message` with version, link, ID, data pointer, length, and retry count. The DDC/AUX layer executes it and writes `status` to indicate success, failure, or unsupported message.

State and persistence: The message struct is transient and caller-owned. It points to external data buffers, so buffer lifetime and length correctness are caller responsibilities.

Dependencies and integration points: Consumed by HDCP DDC code and state machines in `modules/hdcp`. The `link` field matters primarily for DVI dual-link behavior; DP and HDMI paths select IDs from the same enum.

Risks: IDs are ordinal and shared across HDCP versions; mismatching `version` and `msg_id` can send invalid transactions. `data` is a raw pointer with no const qualifier, so implementations may modify buffers. Retry behavior is encoded per message and must be bounded by callers.

Test signals: Validate ID-to-DDC/AUX address mapping, max message sizes, retry exhaustion, unsupported version/message combinations, and status propagation into HDCP state transitions.
