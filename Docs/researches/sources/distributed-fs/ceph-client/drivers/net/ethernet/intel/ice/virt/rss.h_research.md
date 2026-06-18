# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/rss.h

## Purpose
This header exposes the ICE VF RSS virtchnl handlers implemented in `rss.c` to the rest of the ICE virtualization code. It is intentionally narrow: it forward-declares `struct ice_vf`, includes Linux scalar types, and publishes only the functions needed by the virtchnl dispatcher.

## Important APIs, Types, And Functions
The public API consists of `ice_vc_handle_rss_cfg()`, `ice_vc_config_rss_key()`, `ice_vc_config_rss_lut()`, `ice_vc_config_rss_hfunc()`, `ice_vc_get_rss_hashcfg()`, and `ice_vc_set_rss_hashcfg()`. The `bool add` parameter on `ice_vc_handle_rss_cfg()` lets the dispatcher reuse one handler for `VIRTCHNL_OP_ADD_RSS_CFG` and `VIRTCHNL_OP_DEL_RSS_CFG`. The remaining handlers map one-to-one to legacy RSS virtchnl operations.

## Control Flow
The header has no executable control flow. Its role in control flow is indirect: `virtchnl.c` includes it, assigns these functions into `struct ice_virtchnl_ops`, and calls them from `ice_vc_process_vf_msg()` after virtchnl message validation and opcode allowlist checks.

## State And Persistence
No state is defined in this header. All state changes occur through the opaque `struct ice_vf *` passed to the functions, including per-VF RSS contexts, capabilities, and VSI-backed hardware configuration.

## Dependencies And Integration Points
The header depends on `<linux/types.h>` for `u8` and `bool`, and on ICE VF definitions only through a forward declaration. This keeps compile-time coupling low while allowing `virtchnl.c` to integrate RSS support without importing `rss.c` internals.

## Risks
Because this is a dispatcher-facing interface, prototype drift between `rss.h`, `rss.c`, and `struct ice_virtchnl_ops` would break builds or misroute callbacks. The simple `u8 *msg` signature also means type safety is enforced inside implementations and by virtchnl validation, not by the header.

## Test Signals
Build coverage with `CONFIG_PCI_IOV` enabled is the primary signal. Runtime signals come from each RSS virtchnl opcode reaching the correct handler and producing a response through `ice_vc_send_msg_to_vf()`.
