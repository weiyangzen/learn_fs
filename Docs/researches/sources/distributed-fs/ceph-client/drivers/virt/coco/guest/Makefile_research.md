# sources/distributed-fs/ceph-client/drivers/virt/coco/guest/Makefile

## Purpose
Builds shared guest TSM objects.

## APIs, Types, and Functions
`CONFIG_TSM_REPORTS` builds `tsm_report.o` from `report.o`; `CONFIG_TSM_MEASUREMENTS` builds `tsm-mr.o`.

## Control Flow and State
No runtime behavior in this file.

## Dependencies and Integration
Used by vendor drivers through exported symbols from `report.c` and `tsm-mr.c`.

## Risks and Test Signals
Build tests should cover `TSM_REPORTS=m` with provider modules and built-in provider combinations to catch symbol visibility issues.
