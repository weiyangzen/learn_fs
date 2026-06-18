<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Kconfig

Purpose: Kconfig menu for the Hauppauge WinTV-PVR USB2 driver and its optional sysfs, DVB, and debug interfaces.

Important APIs/types/functions: `VIDEO_PVRUSB2` is the main tristate and depends on `VIDEO_DEV`, `I2C`, and `DVB_CORE`; it selects tuner, tveeprom, cx2341x encoder, decoder/audio subdevice drivers. `VIDEO_PVRUSB2_SYSFS` enables sysfs controls. `VIDEO_PVRUSB2_DVB` enables digital-TV integration and selects demod/tuner frontends under autoselect. `VIDEO_PVRUSB2_DEBUGIFC` enables the sysfs-hosted debug command interface.

Control flow: Kconfig controls which optional objects are appended by the Makefile. DVB is constrained so modular pvrusb2 is not built against modular-incompatible DVB core combinations.

State and persistence: no runtime state; it controls build inclusion.

Dependencies and integration: integrates pvrusb2 with V4L2, I2C subdevices, cx2341x firmware controls, DVB core/frontends/tuners, sysfs, and media subdriver autoselection.

Risks: the main driver depends on `DVB_CORE` even when DVB support is later disabled, which broadens required configuration. Default-y sysfs and DVB suboptions enlarge the module surface. `VIDEO_PVRUSB2_DEBUGIFC` depends on sysfs, so debug coverage can silently disappear without sysfs.

Test signals: build matrix for main/sysfs/DVB/debug options; ensure selected demod/tuner modules resolve; verify disabled optional features remove sysfs debug or DVB nodes as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/pvrusb2/Kconfig -->
