<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/sysfs.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/catpt/sysfs.c

## Purpose
Device sysfs attributes for exposing CATPT firmware version and firmware information string.

## APIs, Types, and Functions
Defines read-only attributes `fw_version` and `fw_info`, exported through `catpt_attr_groups`. `fw_version_show()` resumes the device, sends `GET_FW_VERSION`, autosuspends again, and prints `type.major.minor.build`. `fw_info_show()` prints the firmware-ready `ipc.config.fw_info` string cached during boot.

## Control Flow, State, and Persistence
`fw_version` is live firmware state and requires runtime PM plus IPC readiness. `fw_info` is cached state from the firmware-ready mailbox and does not resume the DSP. Attribute groups are attached to the platform driver so the files exist for the CATPT device after probe.

## Dependencies and Integration
Depends on runtime PM, `catpt_ipc_get_fw_version()`, `CATPT_IPC_RET()`, and the `catpt_dev` stored as driver data. The attribute group is referenced by `device.c` in the platform driver definition.

## Risks and Test Signals
Risks include `fw_info` being read before firmware-ready data is meaningful on partial probe failure, `fw_version` returning raw runtime PM errors, and IPC failures after autosuspend/resume. Test signals are sysfs reads before and after runtime suspend, correct version formatting, and non-empty firmware info after first boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/catpt/sysfs.c -->
