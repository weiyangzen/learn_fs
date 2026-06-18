# sources/distributed-fs/ceph-client/drivers/scsi/sym53c8xx_2/sym_nvram.h

## Purpose

`sym_nvram.h` defines the persistent configuration formats and public NVRAM interface for the Symbios/LSI 53C8xx driver. It captures the on-card Symbios and Tekram EEPROM layouts, related flag definitions, and the `struct sym_nvram` union passed to setup code.

## Important APIs, Types, And Functions

The Symbios format is represented by `struct Symbios_nvram`, including controller flags, boot-order host records, 16 target records, SCAM records, spare target space, and trailer. Important flags include parity, verbose messages, high-to-low scan order, avoid bus reset, target disconnect, scan-at-boot, scan-LUNs, and tagged queueing.

The Tekram format is represented by `struct Tekram_nvram`, with 16 target records plus host ID, removable/media policy, boot delay index, max tags index, and flags for parity, sync negotiation, disconnect, start command, tagged commands, and wide negotiation.

`struct sym_nvram` stores a type discriminator (`SYM_SYMBIOS_NVRAM`, `SYM_TEKRAM_NVRAM`, `SYM_PARISC_PDC`) and, when NVRAM support is enabled, the corresponding union payload. Public functions are `sym_nvram_setup_host()`, `sym_nvram_setup_target()`, `sym_read_nvram()`, and `sym_nvram_type()`. Stub inline implementations are provided when `SYM_CONF_NVRAM_SUPPORT` is disabled.

## Control Flow And State

The header itself has no runtime control flow, but its structures define the persistent state decoded by `sym_nvram.c`. The data affects HBA initialization and per-target defaults before normal SCSI negotiation begins.

## Dependencies And Integration Points

It includes `sym53c8xx.h` for driver configuration and SCSI/HBA types. The structures are used by NVRAM readers, host attach code, and target setup code. On non-PA-RISC systems a dummy `struct pdc_initiator` is declared so the union remains compilable without firmware support.

## Risks And Test Signals

These structures map binary EEPROM layouts, so packing, field sizes, and flag meanings must remain stable. The fallback stubs have a signature mismatch risk: the disabled-support `sym_nvram_setup_target()` inline accepts fewer parameters than the enabled declaration in this file's visible code, which would matter if compiled in a configuration that calls the three-argument form while NVRAM support is off.

Test signals are successful compilation across NVRAM-enabled/disabled and PA-RISC/non-PA-RISC configurations, plus runtime confirmation that decoded fields match EEPROM dumps.
