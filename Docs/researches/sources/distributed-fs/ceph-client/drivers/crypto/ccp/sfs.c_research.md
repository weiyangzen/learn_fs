# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sfs.c

## Purpose

`sfs.c` implements AMD PSP Seamless Firmware Servicing support through `/dev/sfs`. It sends PSP extended mailbox commands to query firmware versions and load SFS update packages from the kernel firmware store.

## Important APIs, Types, And Functions

Lifecycle functions are `sfs_dev_init()` and `sfs_dev_destroy()`. User entry is `sfs_ioctl()`. Firmware command helpers are `send_sfs_cmd()`, `send_sfs_get_fw_versions()`, and `send_sfs_update_package()`. `sfs_misc_init()` registers a shared misc device with reference counting.

## Control Flow

Initialization allocates a 2 MiB command buffer through the SNP HV-fixed page allocator, marks it uncacheable, stores it in `psp->sfs_data`, and registers `/dev/sfs` mode `0600`. `SFSIOCFWVERS` initializes the first page to `0xc7`, sends `PSP_SFS_GET_FW_VERSIONS`, and copies the version blob plus status fields back to userspace. `SFSIOCUPDATEPKG` copies a bounded payload name from userspace, requests `amd/<payload>`, checks the aligned package size against the fixed 2 MiB buffer, copies firmware bytes into the SFS buffer, sends `PSP_SFS_UPDATE`, and returns firmware status.

## State And Persistence Behavior

The 2 MiB command buffer persists for the PSP device lifetime and may become HV-fixed during SNP init. It is mapped uncacheable until destroy restores write-back caching. The misc device is process-shared and protected by a global ioctl mutex.

## Dependencies And Integration Points

SFS depends on PSP extended mailbox commands, firmware loader paths under `amd/`, SEV SNP HV-fixed page allocation, memory attribute changes, and SFS UAPI structures. PSP init enables it when capability bit `sfs` is present.

## Risks And Test Signals

Risks include uncacheable mapping cleanup failure, HV-fixed page lifetime leaks, accepting malformed payload names, firmware package alignment mistakes, and concurrent ioctl buffer reuse. Test `/dev/sfs` permissions, firmware-version query, update with maximum and oversized payloads, missing firmware files, SNP-enabled initialization, and remove/unload memory attribute restoration.
