## sources/distributed-fs/openafs/src/libuafs/afsload/lib/AFS/Load/Config.pm

Purpose: Parses and validates afsload configuration files, including node ranges, node configuration directives, step boundaries, names, and actions.

Important APIs and functions: `check_conf($np, $conf_file)` validates a full configuration for a process count. `load_conf($rank, $conf_file, $stepsref, $nodeconfref)` parses config for one logical worker rank. Internal helpers `_range_check`, `_range_match`, and `_nextword` implement range semantics and token walking.

Control flow: `load_conf` reads the full file, tokenizes it with `Text::ParseWords::parse_line`, appends a sentinel `step`, then walks top-level directives. In `nodeconfig`, matching node ranges assign key/value settings. In `step`, optional `name` is captured and matching node action directives are converted into action objects. Skipped directives are scanned until the next `node` or `step`. After parsing, `$RANK` substitutions are applied to node config values. `check_conf` calls `load_conf` with a negative pseudo-rank to validate ranges and records nodes that have actions.

State and persistence: Module globals `@saw_nodes` and `$in_nodeconfig` track validation state. No persistent output.

Dependencies and integration: Depends on `Text::ParseWords` and `AFS::Load::Action`. Consumed by both config checker and MPI runner.

Risks: Global validation state is not reset between calls, so repeated checks in one interpreter can leak `@saw_nodes`. The whole file is tokenized at once and comments are not explicitly handled. Skipping unknown action arguments relies on `node` and `step` tokens not appearing as data. Negative-rank validation is clever but fragile.

Test signals: All range forms, invalid ranges, nodeconfig matching, `$RANK` substitution, named steps, skipped unmatched nodes, missing actions for nodes warnings, repeated `check_conf` calls, and quoted strings containing whitespace.
