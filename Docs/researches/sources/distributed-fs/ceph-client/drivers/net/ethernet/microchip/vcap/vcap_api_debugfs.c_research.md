# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs.c

## Purpose
`vcap_api_debugfs.c` implements read-only debugfs views for VCAP state. It exposes per-port callback output, full decoded VCAP instance dumps, and raw address/keyset scans for diagnosing installed rules and hardware layout.

## Important APIs and Functions
The exported entry points are `vcap_port_debugfs` and `vcap_debugfs`. Internally, `vcap_debugfs_show_rule_keyfield` and `vcap_debugfs_show_rule_actionfield` format typed values, including IPv4, IPv6, MAC, decimal, and hex representations. `vcap_debugfs_show_keysets`, `vcap_debugfs_show_rule_keyset`, `vcap_debugfs_show_rule_actionset`, and `vcap_show_admin_rule` compose a decoded rule dump. `vcap_show_admin_info` prints model/admin metadata. `vcap_show_admin` decodes each stored rule, while `vcap_show_admin_raw` scans addresses and calls `vcap_addr_keysets`.

## Control Flow
`vcap_debugfs` creates a `vcaps` directory, then for each admin creates `raw_<name>_<instance>` and `<name>_<instance>` files. The normal view locks the admin, decodes each rule through `vcap_decode_rule`, prints metadata and fields, then frees the decoded copy. The raw view locks the admin, walks from `last_valid_addr` down to `first_valid_addr`, identifies keysets at each address, and prints aligned rule starts. `vcap_port_debugfs` creates a netdev-named file whose show callback delegates to the platform `port_info` callback for each instance zero admin.

## State and Persistence Behavior
Debugfs files store small `devm_kzalloc` info wrappers pointing at existing `vcap_control`, `vcap_admin`, and `net_device` objects. They do not own rules or hardware state. Show paths read hardware through the same cache/decode functions as the API and are serialized by `admin->lock`.

## Dependencies and Integration Points
The file depends on `debugfs`, `seq_file` show attributes, private VCAP internals, name/stat tables, and platform callbacks. It integrates with the public `vcap_api_debugfs.h` stubs so callers can compile without debugfs.

## Risks and Test Signals
Debugfs reads can be expensive because full dumps decode rules and raw dumps scan address ranges. Formatting assumes generated name tables cover all enum values being printed. The U32 formatter uses bit masks based on field width and must avoid invalid full-width shifts; the code handles width 32 specially for keyfields, but actionfield U32 formatting should be considered carefully if width can be 32. KUnit covers admin metadata output, full decoded rule output, and raw keyset scanning.
