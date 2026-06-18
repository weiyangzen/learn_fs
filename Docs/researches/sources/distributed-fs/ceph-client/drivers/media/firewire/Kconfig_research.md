# sources/distributed-fs/ceph-client/drivers/media/firewire/Kconfig

Purpose: Kconfig fragment for Digital Everywhere FireDTV/FloppyDTV FireWire DVB adapters.

Important APIs/types/functions: The fragment is active only when `DVB_CORE && FIREWIRE`. `config DVB_FIREDTV` is a tristate that builds the `firedtv` module. Nested `config DVB_FIREDTV_INPUT` is a derived boolean enabling remote-control input support when `INPUT` availability matches the FireDTV build mode.

Control flow: Selecting `DVB_FIREDTV` enables the FireWire DVB driver objects from the Makefile. Selecting or deriving `DVB_FIREDTV_INPUT` adds remote-control input code. The visible comment groups these under FireWire adapters in media configuration.

State and persistence: Kconfig choices determine compile-time module composition and the presence of input support. No runtime state is defined here.

Dependencies/integration: Integrates with the kernel media Kconfig hierarchy, DVB core, FireWire core, and input subsystem. The Makefile consumes `CONFIG_DVB_FIREDTV` and `CONFIG_DVB_FIREDTV_INPUT`.

Risks and test signals: Build matrix should cover disabled, built-in, module, and input-enabled/disabled combinations. The derived input expression must avoid invalid built-in/module combinations where input support would be unavailable to the FireDTV object.
