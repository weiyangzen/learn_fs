# sources/distributed-fs/ceph-client/drivers/slimbus/Makefile

Purpose: Kbuild rules for the SLIMbus framework and controllers.

Important build rules: `CONFIG_SLIMBUS` builds aggregate module/object `slimbus.o` from `core.o`, `messaging.o`, `sched.o`, and `stream.o`. `CONFIG_SLIM_QCOM_NGD_CTRL` builds `slim-qcom-ngd-ctrl.o` from `qcom-ngd-ctrl.o`.

Control flow and integration: common framework objects provide bus registration, messaging, clock scheduling, and stream APIs. Controller objects call framework registration and transfer APIs.

State and dependencies: no runtime state. Dependencies are Kbuild and the selected Kconfig symbols. Risks include aggregate object composition mismatches if APIs move between framework files, and controller link failures when helper symbols are unavailable. Test signals are modular and built-in builds, symbol export resolution for SLIMbus client/controller drivers, and controller module loading on supported hardware.
