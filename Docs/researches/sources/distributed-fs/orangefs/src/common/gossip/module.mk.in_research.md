# sources/distributed-fs/orangefs/src/common/gossip/module.mk.in

Purpose: Build-fragment registration for the gossip logging implementation and optional backtrace support.

Important build variables: Substitutes `GOSSIP_ENABLE_BACKTRACE`, adds `gossip.c` to `LIBSRC`, `SERVERSRC`, and `LIBBMISRC`, and adds `-DGOSSIP_ENABLE_BACKTRACE` to `MODCFLAGS_$(DIR)/gossip.c` when enabled.

Control flow/state: Make configuration only.

Dependencies/integration: Ties configure-time backtrace detection/choice into the C preprocessor path in `gossip.c`.

Risks: Optional backtrace requires compatible execinfo support and correct link flags from elsewhere. The make variable name being set to `@GOSSIP_ENABLE_BACKTRACE@` must evaluate as intended.

Test signals: Configure both backtrace-on and backtrace-off builds; confirm `gossip_backtrace()` either emits stack frames or compiles to a no-op.
