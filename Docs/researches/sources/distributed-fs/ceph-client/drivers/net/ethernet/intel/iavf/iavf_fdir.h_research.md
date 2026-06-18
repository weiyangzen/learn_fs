# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/iavf/iavf_fdir.h

## Purpose
`iavf_fdir.h` defines the Flow Director data model and public helper interface used by ethtool ntuple and TC u32 offload code. It is the contract between userspace rule parsing, local bookkeeping, and virtchnl PF programming.

## Important APIs, Types, And Functions
`enum iavf_fdir_fltr_state_t` describes the filter lifecycle: add request/pending, delete request/pending, disable request/pending, inactive, and active. Comments clarify that delete removes a VF-side object after PF success, while disable keeps the object and moves it inactive.

`enum iavf_fdir_flow_type` enumerates supported L2, IPv4, and IPv6 FDIR families: TCP, UDP, SCTP, AH, ESP, other IP, and non-IP L2. `IAVF_FLEX_WORD_NUM` is fixed at two because ethtool exposes two `m_ext.data` words.

Data structs split rule content into `iavf_fdir_eth`, `iavf_fdir_ip`, `iavf_fdir_extra`, and flex words. `struct iavf_fdir_fltr` is the central record: list linkage, state, flow type, data/mask pairs, virtchnl action, IP version, flex words, ethtool `flow_id`/`loc`/queue, TC u32 handle, and the prebuilt `virtchnl_fdir_add` message.

`iavf_is_raw_fdir` identifies TC u32 raw filters by checking whether the prebuilt virtchnl protocol header count is zero. Prototypes expose validation, add-message filling, printing, duplicate lookup, list add/delete, and lookup.

## Control Flow
The header itself has no runtime control flow except `iavf_is_raw_fdir`. Its state enum drives control in `iavf_fdir.c`, `iavf_ethtool.c`, `iavf_main.c`, and virtchnl completion handling. A normal ethtool rule is created with parsed key/mask fields, validated, converted to `vc_add_msg`, then inserted with an initial request or inactive state. A raw TC u32 rule is inserted with raw `vc_add_msg.rule_cfg.proto_hdrs.raw` bytes and is found/deleted by `cls_u32_handle`.

## State And Persistence Behavior
`struct iavf_fdir_fltr` is persistent only for the lifetime of the adapter instance. Its `state` field captures whether PF hardware has been requested, is pending, is active, or must be disabled/deleted. The embedded `vc_add_msg` allows the driver to replay or add the same rule after link changes and resets without reparsing the original user command.

## Dependencies And Integration Points
This header forward-declares `struct iavf_adapter` and requires virtchnl types through `iavf.h` include chains. It is consumed by FDIR implementation, ethtool RXNFC support, TC u32 offload, reset/down/open handling, and virtchnl completion code that advances filter states after PF responses.

## Risks
Any change to `struct iavf_fdir_fltr` affects multiple asynchronous paths and must preserve lock discipline around `adapter->fdir_fltr_lock`. The raw-filter heuristic depends on protocol header count being zero for TC u32 raw rules; if a raw rule ever uses counted protocol headers this classification breaks. Adding new flow types requires updates in ethtool mappings, message construction, print formatting, validation, and PF capability checks.

## Test Signals
Compile coverage should catch missing enum switch cases only where warnings are enabled, so runtime tests should add/list/delete ethtool and raw u32 rules, cycle link down/up, reset the VF, disable `NETIF_F_NTUPLE`, and verify state transitions and active counters remain consistent.
