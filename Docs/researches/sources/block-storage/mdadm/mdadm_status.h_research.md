# File Research: sources/block-storage/mdadm/mdadm_status.h

## Role

`mdadm_status.h` defines the small common status enum used by newer mdadm helper functions.

## API

`mdadm_status_t` has five values:

- `MDADM_STATUS_SUCCESS`
- `MDADM_STATUS_ERROR`
- `MDADM_STATUS_UNDEF`
- `MDADM_STATUS_MEM_FAIL`
- `MDADM_STATUS_FORKED`

## Dependency Notes

The header is guarded and standalone. It is included by `mdadm.h`, which makes the status type available to sysfs, policy, platform, systemd, and metadata helper declarations.
