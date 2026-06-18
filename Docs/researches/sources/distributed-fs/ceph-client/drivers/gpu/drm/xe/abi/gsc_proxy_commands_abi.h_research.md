# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/abi/gsc_proxy_commands_abi.h

Purpose: Defines the GSC proxy-message ABI for routing messages among KMD, GSC, and CSME.

Important APIs/types: `HECI_MEADDRESS_PROXY`, `struct xe_gsc_proxy_header`, `GSC_PROXY_TYPE`, `GSC_PROXY_PAYLOAD_LENGTH`, addressing constants, and `enum xe_gsc_proxy_type`.

Control flow: Proxy handlers parse type and payload length from `hdr`, inspect source/destination, and handle query/payload/end/notification messages.

State/persistence: Proxy packet state is transient; status and addressing live in each packed header.

Dependencies/integration: Used by xe GSC proxy code and generic GSC HECI submission.

Risks/test signals: Length-mask validation before payload access, invalid route/type rejection, firmware ABI drift, proxy sequence tests, notification handling, and fuzzed malformed headers.
