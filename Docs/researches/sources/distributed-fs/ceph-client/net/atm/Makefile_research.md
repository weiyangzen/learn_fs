# sources/distributed-fs/ceph-client/net/atm/Makefile

Purpose: Kbuild manifest for ATM protocol families and optional ATM protocol adapters.

Important APIs, types, and functions: defines composite `atm-y` as `addr.o pvc.o signaling.o svc.o ioctl.o common.o atm_misc.o raw.o resources.o atm_sysfs.o`. `obj-$(CONFIG_ATM) += atm.o`; `obj-$(CONFIG_ATM_BR2684) += br2684.o`; optional `atm-$(CONFIG_PROC_FS) += proc.o`; and `obj-$(CONFIG_PPPOATM) += pppoatm.o`.

Control flow: enabling core ATM builds the composite `atm.o` from common socket code, address registry, signaling, resources, sysfs, and protocol adapters. Proc support is included only with procfs. BR2684 and PPP-over-ATM are separate objects/modules gated by their symbols.

State and persistence: no runtime state; build composition is derived from `.config`.

Dependencies and integration points: matches `net/atm/Kconfig` and the top-level net Makefile. The composition assumes `common.o` can call helpers from sibling ATM objects and that optional modules such as BR2684 register with ATM ioctl/notifier hooks exported by the core.

Risks: object membership and link order matter because `subsys_initcall(atm_init)` and protocol initialization call into the included objects. Optional proc/sysfs dependencies must stay aligned with C references.

Test signals: `ATM=y/m` builds `atm.o` with all base members, `PROC_FS=n` omits `proc.o`, `ATM_BR2684=m` builds `br2684.ko`, and link checks confirm exported hooks satisfy BR2684/PPPOATM users.
