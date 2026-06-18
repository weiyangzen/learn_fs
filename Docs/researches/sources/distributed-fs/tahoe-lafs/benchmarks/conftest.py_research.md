## sources/distributed-fs/tahoe-lafs/benchmarks/conftest.py

Purpose: pytest infrastructure for Tahoe-LAFS benchmarks, parameterizing storage-node counts and creating an ephemeral grid.

Important APIs/fixtures: `pytest_addoption`, `pytest_generate_tests`, `port_allocator`, `grid`, `storage_nodes`, `client_node`, `get_cpu_time_for_cgroup`, `Benchmarker.record`, and `tahoe_benchmarker`.

Control flow: pytest receives repeated `--number-of-nodes` values, parametrizes tests, creates a temp grid with flog gatherer and introducer, starts requested storage nodes, creates a client with matching needed/happy shares, and records wall/CPU time around benchmark blocks.

State and dependencies: creates temp directories, Tahoe processes, flog gatherer, storage servers, clients, and reads `/proc/self/cgroup` plus `/sys/fs/cgroup/*/cpu.stat`. Depends on pytest-twisted, Twisted reactor, integration grid helpers, and Tahoe utilities.

Risks: assumes Linux cgroup v2 and systemd-run context; benchmark output is printed rather than persisted structurally. Session fixtures mean tests share grid state and must avoid name collisions.
