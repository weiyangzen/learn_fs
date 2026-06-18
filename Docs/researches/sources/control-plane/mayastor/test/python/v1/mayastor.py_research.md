# sources/control-plane/mayastor/test/python/v1/mayastor.py

Purpose: shared pytest fixtures for v1 Mayastor tests. It converts docker-compose containers into `MayastorHandle` dictionaries at function or module scope and provides temp-file and size-check helpers.

Important APIs and control flow: `check_size(prev, current, delta)` asserts pool used-space change in MiB. `containers` and `container_mod` collect compose containers by name. `mayastors` and `mayastor_mod` create `MayastorHandle` instances using each container’s `mayastor_net` IPv4 address. `create_temp_files` removes and recreates `/tmp/<container>.img` as 1 GiB files for all containers.

State, dependencies, and integration: fixture state is dictionaries of Docker container objects and gRPC handles. Temporary state is host `/tmp` images shared into containers. It depends on pytest-docker-compose, `v1.hdl.MayastorHandle`, and `common.command.run_cmd`.

Risks and test signals: handles are not explicitly closed after yield. `create_temp_files` has no cleanup after the test beyond recreating at setup. The fixture assumes all containers join `mayastor_net`. Signals are indirect: downstream tests fail early if handles cannot connect or temp files are missing.
