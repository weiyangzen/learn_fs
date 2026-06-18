<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/Makefile -->
# sources/distributed-fs/ceph-client/drivers/macintosh/Makefile

Purpose: This Makefile maps Macintosh driver Kconfig options to object files and subdirectories.

Important mappings: It builds MacIO support for `PPC_PMAC`, media bay, Mac HID emulated mouse buttons, ADB HID, ANS LCD, PMU/CUDA/SMU and related LED/backlight/APM/event objects, ADB core and controller backends, thermal drivers, windfarm thermal modules, rack-meter, and the AMS subdirectory.

Control flow and dependencies: There is no runtime logic. Multi-object windfarm configurations list the shared control/sensor/PID objects needed by each machine family. `CONFIG_SENSORS_AMS` descends into `ams/`.

Risks and test signals: Object sharing across windfarm targets can cause duplicate symbol or missing dependency problems if Kconfig changes. Build-test key PPC/m68k configurations and module/built-in combinations where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/Makefile -->
