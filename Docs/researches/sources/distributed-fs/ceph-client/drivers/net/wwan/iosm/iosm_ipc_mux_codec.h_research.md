# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_mux_codec.h

Purpose: defines mux codec wire headers, signatures, queue/flow-control thresholds, command timeout, and codec function prototypes used by mux and imem.

Important types/APIs: `mux_cmdh`, `mux_acbh`, `mux_adbh`, `mux_adth`, `mux_adgh`, `mux_lite_cmdh`, `ipc_mem_lite_gen_tbl`, `mux_type_cmdh`, `mux_type_header`, and functions for DL decode, ACB command send, netif flow control, UL trigger/encode/completion, ADB finish, and queue-level update.

Control flow role: the header separates mux session management from byte-level codec layout. MUX Lite uses `mux_lite_cmdh`, ADGH, generic QL/FCT tables; aggregation uses ACBH/CMDH and ADBH/ADTH/QLTH. Constants define when TX should stop or resume and how long open/close commands may block.

State/dependencies: no persistent state here; structs overlay SKB data and must match firmware byte layout. Dependencies include `iosm_ipc_mux.h` for session and command parameter types. Risks: ABI signatures and `offsetof`-based variable headers must stay aligned with CP; duplicate buffer-size constants with mux.h invite drift; threshold tuning affects throughput and backpressure. Test signals: layout/size assertions, encode/decode round trips, command timeout path, and boundary cases around queue-level and flow-credit tables.
