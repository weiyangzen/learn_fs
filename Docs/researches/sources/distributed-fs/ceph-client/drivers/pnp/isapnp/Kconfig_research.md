<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Kconfig

Purpose: Build configuration for ISA Plug and Play protocol support.

Important APIs/types/functions: `ISAPNP` bool depends on ISA or `HAS_IOPORT && COMPILE_TEST`.

Control flow/state: build-time only.

Dependencies/integration: includes legacy ISA I/O port enumeration backend under PnP when enabled.

Risks: legacy probing can touch sensitive ports; runtime code has disable parameters, but build enabling makes it available.

Test signals: ISA and compile-test build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pnp/isapnp/Kconfig -->
