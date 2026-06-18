# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/devlink_port_split.py

Purpose: Standalone Python test for devlink port split behavior based on the `lanes` and `splittable` port attributes.

Important APIs/functions: `run_command()`, `devlink_ports.get_if_names()`, `get_max_lanes()`, `get_split_ability()`, `split()`, `unsplit()`, `exists()`, `exists_and_lanes()`, `test()`, `create_split_group()`, `split_unsplittable_port()`, `split_splittable_port()`, `validate_devlink_output()`, `make_parser()`, and `main()`.

Control flow: It selects a devlink device from `--dev` or the first `devlink -j dev show` entry, enumerates physical ports, skips if no lanes info exists, verifies one-lane ports are unsplittable, and for wider ports iteratively splits to valid counts, waits for udev to settle, verifies split netdev names and lane counts, then unsplits.

State and persistence: Mutates physical devlink port split state and relies on unsplit cleanup after each split. No explicit trap exists, so interruption can leave ports split.

Dependencies and integration points: Requires devlink JSON output with `flavour`, `lanes`, `splittable`, `netdev`, udevadm, and hardware supporting port split.

Risks and test signals: Disruptive to physical port layout. Failures signal devlink lane reporting, split validation, netdev creation, or unsplit regressions.
