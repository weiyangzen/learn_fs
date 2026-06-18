# sources/distributed-fs/orangefs/src/io/description/pint-dist-utils.c

## Purpose
Registers built-in distributions and manages a small parameter-offset table used by distribution `set_param` implementations.

## Important APIs, Types, And Functions
Exports `PINT_dist_initialize`, `PINT_dist_finalize`, `PINT_dist_default_get_num_dfiles`, `PINT_dist_default_set_param`, `PINT_dist_register_param_offset`, and `PINT_dist_unregister_param_offset`. Private type `PINT_dist_param_offset` records distribution name, parameter name, field offset, and field size.

## Control Flow
Initialization registers `basic`, `varstrip`, `simple_stripe`, and `twod_stripe` distributions. Finalization unregisters them and frees the parameter table. Registration grows the table in increments of ten, allocates name strings, stores offset/size metadata, and increments entry count. Default parameter setting looks up a `(dist,param)` row and `memcpy`s the provided value into the parameter blob. Unregistration frees matching strings and bubbles later entries down.

## State And Persistence
State is an in-memory global parameter table and distribution registry entries. No durable persistence exists, but encoded distributions depend on these registrations being active during decode/lookup.

## Dependencies And Integration Points
Depends on built-in distribution globals, `pint-distribution.h`, dist-specific headers, and server configuration type. Called during OrangeFS distribution subsystem startup/shutdown.

## Risks And Test Signals
Risks include not freeing individual dist/param strings in `PINT_dist_finalize` before freeing the table, leak if param-name allocation fails after dist-name allocation, no duplicate registration check, and default setter only supporting plain POD fields. Tests should cover init/finalize cycles, param set/unregister, duplicate params, allocation failures, and distribution lookup after registration.
