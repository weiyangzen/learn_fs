# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_adminq.h

Purpose: this header defines iavf Admin Queue data structures and helpers shared by AdminQ implementation and common AQ command wrappers.

Important APIs/types: it defines `IAVF_ADMINQ_DESC`, descriptor alignment, `struct iavf_adminq_ring`, `struct iavf_asq_cmd_details`, `IAVF_ADMINQ_DETAILS`, `struct iavf_arq_event_info`, and `struct iavf_adminq_info`. It declares `iavf_fill_default_direct_cmd_desc` and provides `iavf_aq_rc_to_posix` for converting firmware AQ return codes to Linux errno values. Constants include `IAVF_AQ_LARGE_BUF` and `IAVF_ASQ_CMD_TIMEOUT`.

Control flow and state: `iavf_adminq_info` embeds ASQ and ARQ rings, queue depths and buffer sizes, firmware/API version fields, ASQ/ARQ mutexes, and last status codes. `iavf_asq_cmd_details` controls optional callbacks, cookies, flag overrides, async/postpone behavior, and writeback descriptor capture. `iavf_arq_event_info` is the handoff object for received PF events.

Dependencies and integration: it includes OS dependency, status, and AdminQ command definition headers. It integrates the low-level ring implementation with higher-level common code and error reporting.

Risks and test signals: structure layout and descriptor macros must match ring memory allocated in `iavf_adminq.c`. Error conversion must stay aligned with `enum libie_aq_err`; invalid codes return `-ERANGE`, while AQ timeout maps to `-EAGAIN`. Tests should cover compile layout, timeout conversion, and ASQ command-detail behavior.
