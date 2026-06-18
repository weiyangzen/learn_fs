<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genl_magic_func.h -->
# sources/distributed-fs/ceph-client/include/linux/genl_magic_func.h

Purpose: Generates generic-netlink policies, ops, family registration, multicast helpers, struct parsing/serialization, and default initialization from a macro include file.

Important APIs/types/functions: This header repeatedly redefines `GENL_struct`, `GENL_op`, `GENL_notification`, `GENL_mc_group`, `__field`, and `__array` around `GENL_MAGIC_INCLUDE_FILE`. It creates top-level and nested `nla_policy` arrays, `*_from_attrs()` and `*_from_attrs_for_change()` parsers, `*_genl_cmd_to_str()`, kernel `genl_ops`, multicast group arrays/helpers, `*_genl_register()`, `*_genl_unregister()`, `*_to_skb()` plus privileged/unprivileged wrappers, and `set_*_defaults()` functions. Optional `GENL_MAGIC_DEBUG` prints field conversions.

Control flow: A consumer defines family/version/include macros, includes the struct header, then this function header. Macro expansion builds concrete code. Incoming genl messages are validated by generated policies, nested attributes are parsed into structs, invariant/required rules are enforced, and outgoing structs are serialized into nested skb attributes with sensitive fields optionally excluded.

State and persistence behavior: Generated static policies, ops arrays, family struct, multicast groups, and a shared `nested_attr_tb[128]` parse buffer are runtime global state. Serialization itself is per-message.

Dependencies and integration points: Depends on `genl_magic_struct.h`, generic netlink, nlattr helpers, skb helpers, and DRBD-specific attribute flags.

Risks: The shared nested parse buffer assumes serialized generic-netlink message processing. Macro misuse or duplicate numbers may compile but produce wrong UAPI unless struct assertions are included. Sensitive/invariant flags are DRBD-specific policy embedded in generic code. Array max length handling differs for NUL strings.

Test signals: Compile generated family users, netlink policy validation, required/missing/invariant change tests, sensitive-field redaction, multicast helper calls, buffer size boundary tests, and `GENL_MAGIC_DEBUG` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/genl_magic_func.h -->
