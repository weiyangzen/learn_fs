<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/can/cc770/Makefile

Purpose: this Makefile maps CC770 Kconfig symbols to the shared core and bus-specific object files.

Important APIs, types, and functions: `obj-$(CONFIG_CAN_CC770) += cc770.o` builds the shared controller core. `obj-$(CONFIG_CAN_CC770_ISA) += cc770_isa.o` and `obj-$(CONFIG_CAN_CC770_PLATFORM) += cc770_platform.o` build the ISA and platform wrappers.

Control flow: kbuild evaluates the three symbols and compiles the corresponding objects. The wrappers depend on exported or shared core functionality from `cc770.o`.

State and persistence: the file has no runtime state; it affects build output only.

Dependencies and integration points: it must stay aligned with `cc770/Kconfig` and the source files present in the directory. The directory is entered from the top-level CAN Makefile when `CONFIG_CAN_CC770` is enabled.

Risks: stale object names or symbol mismatches break module builds. Wrapper objects built without the core would fail linkage, so Kconfig nesting and Makefile gating must remain synchronized.

Test signals: compile built-in and modular CC770 configurations, confirm expected module/object names, and run dependency checks for ISA/platform wrapper selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/can/cc770/Makefile -->
