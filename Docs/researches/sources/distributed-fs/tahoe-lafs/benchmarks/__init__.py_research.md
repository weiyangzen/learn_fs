## sources/distributed-fs/tahoe-lafs/benchmarks/__init__.py

Purpose: package marker and usage documentation for pytest-based Tahoe-LAFS end-to-end benchmarks.

Important content: module docstring explains running benchmarks under `systemd-run --user --scope pytest benchmark --number-of-nodes=3` and that `--number-of-nodes` can be repeated.

Control flow: no executable code.

State and dependencies: as a package marker, it enables imports under `benchmarks`. The documented workflow depends on systemd cgroups for accurate CPU accounting.

Risks and test signals: no direct tests. The docstring aligns with `benchmarks/conftest.py`, which reads cgroup v2 CPU stats; environments without systemd/cgroup v2 may not support the intended measurement mode.
