# sources/distributed-fs/ceph-client/drivers/net/can/softing/Makefile

Purpose: Kbuild rules for Softing CAN drivers.

Important APIs/types/functions: `softing-y := softing_main.o softing_fw.o`; `obj-$(CONFIG_CAN_SOFTING) += softing.o`; `obj-$(CONFIG_CAN_SOFTING_CS) += softing_cs.o`.

Control flow: no runtime flow. The generic Softing module is composed from runtime/netdev logic and firmware-loading logic, while PCMCIA bridge is separate.

State and persistence: build-time only.

Dependencies/integration: requires symbol sharing between `softing_main.o` and `softing_fw.o` through `softing.h`; PCMCIA bridge exports platform data to the `softing` platform driver.

Risks: omitting `softing_fw.o` breaks boot and start/stop paths; omitting `softing_main.o` removes platform driver and netdev ops. Link order is simple but both objects are mandatory.

Test signals: all Softing configs should link; modpost should resolve firmware helper symbols and platform-driver symbols.
