<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sis.h -->
# sources/distributed-fs/ceph-client/drivers/ata/sis.h

## Purpose

This header is the tiny cross-driver contract between SiS SATA and PATA support. It forward-declares `struct ata_port_info` and declares `sis_info133_for_sata`, which lets `sata_sis.c` use the PATA SiS port description for combined or PATA-mode controller channels.

## Important APIs, types, and functions

There are no functions. The only exported symbol declaration is `extern const struct ata_port_info sis_info133_for_sata;`.

## Control flow

The header has no runtime control flow. It is included by `sata_sis.c` so the compiler can type-check references to the PATA port-info object provided by `pata_sis.c`.

## State and persistence behavior

No state is stored here. It only declares a const data object owned elsewhere.

## Dependencies and integration points

It depends on libata's `struct ata_port_info` type by forward declaration and integrates the SATA and PATA SiS drivers at build/link time.

## Risks

The main risk is link/config mismatch: if `sata_sis.c` references `sis_info133_for_sata` without the provider object being built or exported under compatible configs, linking fails. Changes to the type or constness must match the provider.

## Test signals

Compile configurations with SiS SATA combined/PATA support enabled and disabled, ensuring no unresolved `sis_info133_for_sata` symbol and correct mode selection in `sata_sis.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sis.h -->
