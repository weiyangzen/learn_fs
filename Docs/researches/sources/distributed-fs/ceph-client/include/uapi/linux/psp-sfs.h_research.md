<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-sfs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/psp-sfs.h

Purpose: defines the AMD Seamless Firmware Servicing userspace ioctl ABI for querying firmware versions and requesting PSP-managed firmware package updates.

Important APIs and types: `PAYLOAD_NAME_SIZE` and `TEE_EXT_CMD_BUFFER_SIZE` bound payload and version buffers. `struct sfs_user_get_fw_versions` returns a firmware-version blob plus SFS status fields. `struct sfs_user_update_package` carries a payload name and returns status/extended status. `SFSIOCFWVERS` and `SFSIOCUPDATEPKG` use ioctl type `'S'`.

Control flow: userspace asks for firmware versions or names an update package. The kernel driver loads firmware from the configured firmware search path, sends PSP/ASP commands, and returns SFS status codes.

State and persistence: firmware versions and update results are PSP/platform persistent state. Driver mailbox state is transient; an update may change durable firmware levels.

Dependencies and integration points: depends on Linux types and ioctl encoding. Integrates with AMD PSP, firmware_class search path, platform firmware packages under `/lib/firmware/amd`, and administrative update tooling.

Risks and test signals: risks include wrong firmware payload selection, path/config ambiguity, interrupted updates, oversized names/blobs, and poor status decoding. Test version query, valid and missing packages, firmware_class path overrides, PSP busy/timeout paths, and status/extended-status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/psp-sfs.h -->
