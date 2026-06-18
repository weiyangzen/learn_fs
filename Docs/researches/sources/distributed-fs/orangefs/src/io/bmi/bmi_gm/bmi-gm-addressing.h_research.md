<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addressing.h -->
## sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addressing.h

Purpose: Defines GM-specific address payload stored inside generic BMI method addresses.

Important APIs, types, and functions: Constants define `BMI_GM_MAX_PORTS` and `BMI_GM_UNIT_NUM`. `struct gm_addr` contains a quicklist link, GM `node_id`, GM `port_id`, associated generic `BMI_addr_t`, and operation queues for send and handshake behavior.

Control flow and state: Header only. Instances are allocated as method-private payloads by `alloc_gm_method_addr()` in `bmi-gm.c`, inserted into `gm_addr_list`, and used to route sends and match incoming events.

Dependencies and integration points: Includes `bmi-types.h`, `quicklist.h`, `op-list.h`, and `<gm.h>`. It bridges generic BMI addresses with GM node/port identifiers.

Risks and test signals: `BMI_GM_UNIT_NUM` is hard-coded to 0, limiting multi-adapter configurations unless changed elsewhere. Queue fields are not initialized in this header; allocation paths must zero or initialize them. Tests should parse GM URLs, verify node/port matching, and exercise unexpected registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/io/bmi/bmi_gm/bmi-gm-addressing.h -->
