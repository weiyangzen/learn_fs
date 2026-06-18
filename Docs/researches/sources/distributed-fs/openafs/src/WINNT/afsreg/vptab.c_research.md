# sources/distributed-fs/openafs/src/WINNT/afsreg/vptab.c

## Purpose
Implements the Windows vice partition table stored in the registry under the OpenAFS server service Afstab key. It validates partition/device names, enumerates entries, adds/updates entries, and removes entries.

## Important APIs, Types, And Functions
Exported functions are `vpt_PartitionNameValid`, `vpt_DeviceNameValid`, `vpt_Start`, `vpt_NextEntry`, `vpt_Finish`, `vpt_AddEntry`, and `vpt_RemoveEntry`. `PARTITION_NAME_PREFIX` is `/vicep`. Entries are `struct vptab` with `vp_name` and `vp_dev`; iteration uses `struct vpt_iter` over a registry multistring.

## Control Flow
Partition validation accepts `/vicep` plus one lowercase suffix letter or two lowercase letters whose encoded value is within 26..255. Device validation accepts only an uppercase drive letter followed by `:`. Iteration opens `AFSREG_SVR_SVC_AFSTAB_KEY`, enumerates child keys with `RegEnumKeyAlt`, and each `vpt_NextEntry` opens the partition key and reads `DeviceName`. Add opens/creates the Afstab key and partition subkey and writes `DeviceName`. Remove validates the partition name, opens Afstab, and deletes the partition key.

## State And Persistence
The persistent state is registry subkeys under `HKLM\System\CurrentControlSet\Services\TransarcAFSServer\Afstab`, one subkey per vice partition, with a `DeviceName` string value. Iteration state is a heap-allocated multistring owned by the caller until `vpt_Finish`.

## Dependencies And Integration Points
It depends on `afsreg.h` key constants and registry helper functions plus NT-to-Unix errno mapping. It is used by server configuration tools and the `regman` test utility.

## Risks And Test Signals
Risks include strict C-locale assumptions, fixed 32-byte name/device buffers, no recursive delete for partition subkeys, and limited device syntax that only accepts drive-letter devices. Test signals include validation edge cases (`/vicepa`, `/vicepz`, `/vicepaa`, upper/lower drive names), add/list/remove round trips, and errno behavior for missing or malformed registry entries.
