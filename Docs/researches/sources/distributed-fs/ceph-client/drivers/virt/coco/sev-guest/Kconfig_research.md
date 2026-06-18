# sources/distributed-fs/ceph-client/drivers/virt/coco/sev-guest/Kconfig

## Purpose
Declares the AMD SEV guest driver.

## APIs, Types, and Functions
`SEV_GUEST` is a tristate, defaults to module, depends on `AMD_MEM_ENCRYPT`, and selects `TSM_REPORTS`.

## Control Flow and State
Build-time only. Runtime exposes `/dev/sev-guest` and registers a TSM provider when running as an SEV-SNP guest.

## Dependencies and Integration
Depends on AMD memory encryption and PSP/SNP guest messaging support.

## Risks and Test Signals
Test module and built-in builds with and without SNP guest platform attributes. Verify TSM report symbols resolve when built as a module.
