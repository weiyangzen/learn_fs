# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-nl.h

Purpose: shared scalar-key netlink helper definitions for LNet.

Important APIs/types: `enum lnet_nl_key_format` flags describe whether a key is flow/block and mapping/sequence. `enum lnet_nl_scalar_attrs` defines generic nested scalar-list attributes: list, list size, index, nla type, string value, integer value, and key format. `ln_key_props` describes one scalar key with value string, key format, and data type. `ln_key_list` contains a max attribute and flexible array of key properties.

Control flow/state: declarative UAPI only. Internal code in `lib-types.h` defines `scalar_attr_policy` and `lnet_genl_send_scalar_list()` to serialize these definitions through generic netlink.

Dependencies/integration: used by LNet generic netlink code and user tools that need stable scalar lists for changing LNet netlink ABI.

Risks and test signals: flexible-array layout and string pointers are not directly wire-safe; kernel code must translate to netlink attributes rather than exposing raw pointers. Test signals are scalar list encoding/decoding, max attribute bounds, padding handling, and user-space compatibility across added keys.
