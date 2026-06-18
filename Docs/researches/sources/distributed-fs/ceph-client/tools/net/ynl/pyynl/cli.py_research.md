# sources/distributed-fs/ceph-client/tools/net/ynl/pyynl/cli.py

Purpose: Implements the `ynl` command-line utility for listing specs, validating YAML netlink specs, documenting operations, executing do/dump/multi netlink operations, querying kernel policy, and polling notifications.

Important APIs and state: `main()` owns argument parsing and execution. Helpers include `schema_dir()`, `spec_dir()`, `YnlEncoder`, `print_attr_list()`, `print_mode_attrs()`, and `do_doc()`. CLI groups cover family/spec selection, operations, JSON input/output, notification subscription, extra netlink flags, schema options, and debug controls.

Control flow: The CLI resolves either an installed family spec or explicit spec path, optionally validates through `SpecFamily`, constructs `YnlFamily`, optionally enables small receive debug mode, performs policy queries or listing commands, executes `do`, `dump`, or repeated `--multi` requests, and finally drains notifications when subscribed. Errors from kernel netlink operations are printed and returned as exit status 1.

Dependencies and integration: Imports `YnlFamily`, `Netlink`, `NlError`, `SpecFamily`, `SpecException`, and `YnlException` from `pyynl.lib`. It prefers in-tree schema/spec paths relative to the script and falls back to `/usr/share/ynl`.

State and persistence: No persistent state. Runtime state consists of parsed JSON attributes, an open YNL socket, optional notification subscription, and console output formatting.

Risks: `--policy` can clear `args.do`/`args.dump` after printing policy, so combined options rely on this ordering. Installed specs disable schema validation by default, changing behavior from in-tree specs. `print_attr_list()` recursively expands nests and can produce large output or repeat structures. `--process-unknown` defaults differ between installed family selection and explicit specs.

Test signals: `--list-families`, `--validate`, missing spec error, `--list-ops`, `--list-msgs`, `--list-attrs`, JSON do/dump execution, `--output-json`, repeated `--multi`, all extra netlink flags, policy query mode, notification subscription with finite duration, and `--dbg-small-recv`.
