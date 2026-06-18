# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp.h

Purpose: Defines internal NVMe/TCP offload state used by `qed_nvmetcp.c` and provides config-gated allocation/setup/free declarations.

Important APIs/types/functions: Constants define firmware CQ size and TCP defaults such as two-MSL timer, half-way close timeout, FIN retry count, SWS timer, and flow label. `struct qed_nvmetcp_info` owns the connection resource lock, reusable connection free list, outstanding-task limit, and async event callback fields. `struct qed_hash_nvmetcp_con` links active handles into the device hash. `struct qed_nvmetcp_conn` stores ICID/FW CID, queue chains/PBLs, MAC/IP/TCP parameters, update/destroy flags, physical queues, and NVMe/TCP CCCID/ITID table information.

Control flow: The header participates in probe/setup by exposing `qed_nvmetcp_alloc()`, `qed_nvmetcp_setup()`, and `qed_nvmetcp_free()` when `CONFIG_QED_NVMETCP` is enabled. Disabled builds get stubs returning `-EINVAL` or no-op.

State and persistence: It describes all per-connection cached state that persists between user operations and, for free-list entries, across reuse. The fields are copied into firmware ramrods by the implementation rather than directly shared.

Dependencies/integration: Includes Linux list/spinlock helpers, QED chain types, TCP common definitions, public NVMe/TCP interface structs, and core QED SP/MCP definitions.

Risks: Reused `struct qed_nvmetcp_conn` objects need complete reinitialization before offload because the header provides many sticky fields. Disabled-build stubs allow unconditional callers but make runtime feature probing necessary.

Test signals: Build with `CONFIG_QED_NVMETCP=y/m` and disabled, validate structure fields populated by acquire/offload/update paths, and verify free-list reuse does not leak previous digest/TCP/IP/NVMe/TCP settings.
