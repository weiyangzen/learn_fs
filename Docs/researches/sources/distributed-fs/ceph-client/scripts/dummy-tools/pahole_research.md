# sources/distributed-fs/ceph-client/scripts/dummy-tools/pahole

Purpose: Dummy `pahole` version reporter for Kconfig/BTF capability probes.

Important APIs/functions: Prints `v99.99`.

Control flow: Always prints the version string and exits with shell success.

State/persistence: Stateless.

Dependencies/integration: Lets configuration probes believe a sufficiently new `pahole` exists.

Risks: It cannot generate BTF data. Real build use will not produce expected artifacts.

Test signals: Invoke with or without version-like arguments and verify Kconfig version parsing sees a high version.
