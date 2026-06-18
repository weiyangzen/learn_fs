# sources/distributed-fs/ceph-client/drivers/net/ethernet/huawei/hinic/hinic_devlink.c

Implements HiNIC devlink firmware flashing and health reporter dumps. Public APIs allocate/free/register/unregister devlink and create/destroy `hw` and `fw` health reporters.

Firmware update validates raw image magic, section count, total length, required cold-update section set, and board type. `hinic_flash_fw()` skips boot sections, translates A/B section IDs, chunks payload into 1536-byte fragments after the 1024-byte header, sets first/last flags, and sends `HINIC_PORT_CMD_UPDATE_FW` management commands. Health dump callbacks format chip, ucode, memory/register timeout, PHY fault, and management watchdog payloads into devlink fmsg output.

State is `struct hinic_devlink_priv` plus firmware stored in device flash through management commands. Dependencies are devlink/netlink/firmware APIs, board-info and port management commands, `hinic_hw_dev.h`, and `hinic_devlink.h`. Risks are raw header casting, section-offset trust after aggregate validation, cold-only update policy, command failure mapping, and reporter context validity. Test valid/invalid firmware flash cases and reporter dumps for all fault types.
