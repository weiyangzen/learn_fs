# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_prototype.h

## Purpose
`iavf_prototype.h` declares shared-code entry points that are needed before full hardware operations tables are initialized. It is the compile-time bridge from Linux-specific driver code to common AdminQ, RSS, hardware config parsing, and PF virtchnl send helpers.

## Important APIs, Types, And Functions
AdminQ lifecycle and command APIs include `iavf_init_adminq`, `iavf_shutdown_adminq`, `iavf_clean_arq_element`, `iavf_asq_send_command`, and `iavf_asq_done`. Debug and liveness helpers are `iavf_debug_aq`, `iavf_check_asq_alive`, `iavf_aq_queue_shutdown`, and `iavf_stat_str`.

RSS AdminQ helpers are `iavf_aq_set_rss_lut` and `iavf_aq_set_rss_key`. VF configuration and PF messaging helpers are `iavf_vf_parse_hw_config` and `iavf_aq_send_msg_to_pf`. The declarations use `struct iavf_hw`, `struct iavf_arq_event_info`, `struct libie_aq_desc`, `struct iavf_asq_cmd_details`, `struct iavf_aqc_get_set_rss_key_data`, and virtchnl resource/op/status types.

## Control Flow
The header itself has no runtime behavior. In `iavf_main.c`, initialization calls `iavf_init_adminq`, sends API/config messages to PF, polls `iavf_asq_done`, drains events with `iavf_clean_arq_element`, and shuts AdminQ down on reset/remove/failure. RSS configuration paths call the RSS AQ helpers when the negotiated mode requires firmware AdminQ programming.

## State And Persistence Behavior
The declared functions operate on `struct iavf_hw`, especially AdminQ rings, status, debug mask, and backpointer state. They do not define persistence here, but callers rely on them to initialize, tear down, and restore AdminQ/RSS state across reset and probe/remove.

## Dependencies And Integration Points
This header includes `iavf_type.h`, `iavf_alloc.h`, and `<linux/avf/virtchnl.h>`. It is included by `iavf_main.c` and shared AdminQ implementation files. It connects OS-dependent allocation/register helpers from `iavf_osdep.h` with common hardware code and Linux driver lifecycle.

## Risks
Prototype drift between this header and implementation files will break builds or, worse, ABI assumptions inside shared-code call sites. Many functions return `enum iavf_status`, so callers must consistently translate to Linux errno with `iavf_status_to_errno` when crossing kernel API boundaries. AdminQ command APIs take raw buffers and sizes; incorrect lifetime or size handling can corrupt PF/VF communication.

## Test Signals
Build coverage of all shared-code objects, AdminQ init/shutdown fault injection, PF message send/timeout paths, RSS AQ set key/LUT behavior, debug AQ tracing, and reset loops that repeatedly tear down and rebuild AdminQ are the practical signals.
