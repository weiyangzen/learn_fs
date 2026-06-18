# sources/distributed-fs/ceph-client/tools/net/ynl/tests/ethtool.py

Purpose: Python ethtool-like utility built on pyYNL. It exercises real user workflows through `YnlFamily` and serves as both a demo and a test target for `test_ynl_ethtool.sh`.

Important APIs/functions: `args_to_req()` validates CLI attr/value pairs against `operation_do_attributes()` and fills requests. `do_set()` and `do_get()` wrap YNL doit calls with ethtool `header.dev-name`. `bits_to_dict()` converts YNL bitset replies into name/value maps. `print_field()` and `print_speed()` provide human output. `main()` maps many ethtool flags to YAML operation names, including EEE, pause, coalesce, features, channels, rings, stats, timestamping, and default device info.

Control flow/state: argparse produces one mode flag plus a device and trailing attr/value args. The utility constructs `YnlFamily(spec_dir()/ethtool.yaml, schema_dir()/genetlink-legacy.yaml)`, optionally enables small receive debug mode, performs one or more YNL `do()` calls, and prints either Python pretty-printed dicts under `--json` or ethtool-like text.

Dependencies/integration: imports sibling `pyynl/cli.py` directory helpers and `YnlFamily`. It depends on kernel ethtool genetlink support and on operation/attribute names matching the YAML spec.

Risks/test signals: some set paths and bitmask parsing are TODOs. The `--show-ring` path appears to call `channels-get` while printing ring fields, a likely behavioral bug or stale operation name. Shell tests check representative show/set commands under netdevsim and veth namespaces.
