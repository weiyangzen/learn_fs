# sources/distributed-fs/ceph-client/drivers/soc/renesas/rz-sysc.h

## Purpose

`rz-sysc.h` is the private interface between the generic RZ SYSC driver and per-SoC data files. It defines identity metadata, register-access callbacks, and extern descriptors for enabled RZ/G3 and RZ/V2 system controllers.

## Important APIs, Types, and Functions

`struct rz_sysc_soc_id_init_data` contains family string, expected ID, device-ID offset, revision and specific-ID masks, and optional `print_id()` callback. `struct rz_sysc_init_data` contains the identity descriptor, readable/writeable callback pointers, and maximum register offset. Externs name the descriptors implemented by the per-SoC C files.

## Control Flow

No execution occurs in the header. `rz-sysc.c` consumes the structures at probe time through its OF match table and calls optional `print_id()`.

## State and Persistence Behavior

The header declares immutable descriptor shapes. Runtime state is owned by `rz-sysc.c`; hardware state is exposed through regmap.

## Dependencies and Integration Points

It depends on device, soc-bus, and basic type declarations. It creates a narrow integration boundary for adding new RZ system-controller variants without modifying generic probe logic heavily.

## Risks and Edge Cases

Callback contracts are informal: per-SoC files must ensure allowlist callbacks and `max_register` are consistent. Extern declarations must match Kconfig/Makefile object inclusion or link failures result.

## Test Signals

Compile every `SYSC_RZ` combination, including individual SoC symbols, and verify no missing externs. Review new descriptors for ID mask, offset, max register, and callback consistency.
