# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSVolumeInfo.cpp

## Purpose
`AFSVolumeInfo.cpp` handles filesystem volume-information queries. It validates the target FCB, formats Windows `FILE_FS_*` structures from cached `AFSVolumeInfoCB`, asks the service for live size/free-space information, and completes the IRP. Set-volume-information is a no-op success stub.

## Important APIs, Types, And Functions
Public dispatch routines are `AFSQueryVolumeInfo` and `AFSSetVolumeInfo`. Helper formatters are `AFSQueryFsVolumeInfo`, `AFSQueryFsSizeInfo`, `AFSQueryFsDeviceInfo`, `AFSQueryFsAttributeInfo`, and `AFSQueryFsFullSizeInfo`.

`AFSQueryVolumeInfo` decodes `FILE_OBJECT`, `AFSFcb`, `AFSObjectInfoCB`, and `AFSVolumeCB`, detects DOS-device style opens, takes the volume lock shared, rejects pioctl/special-share/invalid FCBs, and switches on `FileFsVolumeInformation`, `FileFsSizeInformation`, `FileFsDeviceInformation`, `FileFsAttributeInformation`, and `FileFsFullSizeInformation`.

## Control Flow
The dispatch path sets `ulLength` from the caller buffer size and passes it by reference to the helper. At exit it reports bytes copied as original length minus remaining length, releases the volume lock, and completes. Helpers zero the caller buffer, check fixed-structure size, fill fixed fields, and either copy full strings or return `STATUS_BUFFER_OVERFLOW` for partial string output.

## State And Persistence Behavior
Cached metadata comes from `pVolumeCB->VolumeInformation`, populated during volume initialization. Size and full-size classes call `AFSRetrieveVolumeSizeInformation` using a file id built from `CellID` and `VolumeID`, so free-space answers are live service data. The file does not persist changes; `AFSSetVolumeInfo` has no effect.

## Dependencies And Integration Points
Dependencies include Windows `FILE_FS_*` structures, `AFSFcb`, `AFSObjectInfoCB`, `AFSVolumeCB`, `AFSVolumeInfoCB`, volume locks, `AFSRetrieveVolumeSizeInformation`, tracing, and completion helpers. The file supports user-mode APIs such as volume-information and free-space queries and complements the quota stubs.

## Risks And Edge Cases
`pObjectInfo->VolumeCB` is assumed valid. `IoStatus.Information` on error depends on remaining-length arithmetic. Labels differ between DOS-device and normal opens: DOS returns the volume label; normal opens return `cell#volumeLabel`. `FILE_DEVICE_DISK` is returned intentionally for compatibility, not strict network-device identity. Set-volume-information silently succeeds.

## Test Signals
Test all supported information classes, unsupported classes, invalid FCB types, null file/Fcb/object info, DOS versus non-DOS labels, small and partial string buffers, live size service failures, `IoStatus.Information` for success/overflow/too-small, filesystem name `AFSRDRFsd`, device type behavior, and no-op set-volume handling.
