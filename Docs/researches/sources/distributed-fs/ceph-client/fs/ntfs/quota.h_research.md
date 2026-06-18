# sources/distributed-fs/ceph-client/fs/ntfs/quota.h

## Purpose
`quota.h` declares the NTFS quota out-of-date marker.

## Important API
It includes `volume.h` and declares `bool ntfs_mark_quotas_out_of_date(struct ntfs_volume *vol)`.

## Control Flow and State
There is no internal state in the header. The return contract is boolean success/failure for updating quota metadata or recognizing it is already out of date.

## Dependencies and Integration
Callers need a mounted `ntfs_volume` with quota system inodes available. The implementation uses index and quota layout internals not exposed by this header.

## Risks
The API does not expose detailed error codes, so callers cannot distinguish missing quota inodes, corrupt quota entries, and unsupported versions without logs.

## Test Signals
Compile coverage plus caller tests should verify that false return paths are handled conservatively and do not assume quota metadata was updated.
