# sources/distributed-fs/ceph-client/drivers/firmware/arm_scmi/transports/Makefile

Purpose: This Makefile maps SCMI transport Kconfig symbols to transport module objects and applies a targeted compiler flag workaround for SMC on Thumb2 Clang builds.

Important APIs/types/functions: It builds `scmi_transport_smc.o` from `smc.o`, `scmi_transport_mailbox.o` from `mailbox.o`, `scmi_transport_optee.o` from `optee.o`, and `scmi_transport_virtio.o` from `virtio.o`. It removes `CC_FLAGS_FTRACE` from `smc.o` when `CONFIG_THUMB2_KERNEL=y` and `CONFIG_CC_IS_CLANG=y`.

Control flow: The SMC object is listed before mailbox to give its compatible matching precedence. Object inclusion follows `obj-$(CONFIG_...)`.

State and persistence: Build metadata only; no runtime state.

Dependencies and integration points: It consumes transport Kconfig symbols and produces kernel objects/modules named by the transport Kconfig help text. The ftrace flag removal integrates with ARM SMCCC register constraints.

Risks and edge cases: Matching precedence can affect devices compatible with multiple SCMI transport bindings. The Thumb2/Clang workaround prevents R7 conflicts with SMCCC but also disables ftrace instrumentation for `smc.o` in that configuration.

Test signals: Build all transport combinations, verify module names and object composition, and compile Thumb2 Clang profiling builds to ensure `smc.o` avoids the R7 frame-pointer conflict.
