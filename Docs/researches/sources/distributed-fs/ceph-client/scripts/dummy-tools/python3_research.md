# sources/distributed-fs/ceph-client/scripts/dummy-tools/python3

Purpose: Dummy `python3` executable for probes that only need command success.

Important APIs/functions: Runs `true`.

Control flow: Ignores all arguments and exits success.

State/persistence: Stateless.

Dependencies/integration: Part of dummy tooling used by configuration generation.

Risks: Does not execute Python. Any script expecting output, file creation, or validation will silently get no behavior.

Test signals: Probe commands that check only for Python availability should pass; commands that require generated files should be excluded from dummy-tool workflows.
