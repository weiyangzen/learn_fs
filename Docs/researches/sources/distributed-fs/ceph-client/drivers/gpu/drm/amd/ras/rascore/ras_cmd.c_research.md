# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/rascore/ras_cmd.c

## Purpose

`ras_cmd.c` implements the generic rascore command dispatcher and handlers for ECC status, bad pages, counter reset, CPER and batch trace retrieval, PSP error injection, interface info, address translation, and device handle management.

## Important APIs, Types, And Functions

Public APIs are `ras_cmd_init/fini`, `rascore_handle_cmd`, `ras_cmd_query_interface_info`, `ras_cmd_translate_soc_pa_to_bank`, `ras_cmd_translate_bank_to_soc_pa`, and `ras_cmd_get_dev_handle`. Static handlers include block ECC status, grouped bad-page reads, clear bad-page info, reset all error counts, CPER snapshot/records, batch trace snapshot/records, and TA-backed error injection. `ras_cmd_maps` maps command IDs to handlers.

## Control Flow, State, And Persistence

Init creates a per-device command handle by XORing the rascore pointer with a magic value. Dispatch linearly searches the command map and returns unknown-command when absent. ECC status queries ACA totals. Bad pages are grouped in pages of 32 records from UMC/EEPROM caches. Clearing bad pages resets firmware or I2C EEPROM then UMC cached data. Counter reset clears ACA and logged UMC ECC. CPER and trace reads snapshot log-ring batches, gather trace records, generate CPER into temporary buffers, and copy to userspace pointers. Injection converts generic block/error IDs to TA IDs and calls PSP RAS TA. Address translation delegates to UMC translation.

## Dependencies And Integration Points

It depends on ACA, UMC, EEPROM/firmware EEPROM, log ring, CPER generation, PSP RAS TA, userspace copy helpers, and command ABI definitions in `ras_cmd.h`. Manager code may wrap or fall back to these handlers.

## Risks And Test Signals

Risks include user pointer copy failures, output buffer overrun if callers ignore `output_size`, command input-size mismatches, stale dev handles, bad-page grouping edge cases, CPER generation partial-buffer behavior, and TA enum drift. Test signals include each command ID, invalid input size/data cases, grouped bad-page pagination, CPER buffer-too-small paths, batch trace max-count limits, injection success/failure, and bank/SOC address round trips.
