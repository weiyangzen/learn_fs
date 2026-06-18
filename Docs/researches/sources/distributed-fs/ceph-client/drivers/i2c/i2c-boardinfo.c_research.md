# sources/distributed-fs/ceph-client/drivers/i2c/i2c-boardinfo.c

## Purpose

`i2c-boardinfo.c` stores statically declared I2C devices for board files and early platform code. These declarations are later consumed by the I2C core when matching adapters are registered.

## Important APIs, Types, and Functions

The file exports `__i2c_board_lock`, `__i2c_board_list`, and `__i2c_first_dynamic_bus_num` for internal I2C core use. Its only function is `i2c_register_board_info()`, which copies an array of `struct i2c_board_info` into allocated `struct i2c_devinfo` records.

## Control Flow

Callers pass a static bus number and descriptor array. The function takes the global write semaphore, advances `__i2c_first_dynamic_bus_num` past the highest reserved static bus, allocates one devinfo per descriptor, copies board info, deep-copies resource arrays when present, appends each entry to `__i2c_board_list`, releases the lock, and returns the first allocation error or zero.

## State and Persistence Behavior

Registered board info persists globally for the lifetime of the kernel. The function copies descriptor structures but does not deep-copy arbitrary embedded pointers beyond `resources`, so platform data and similar pointers must remain valid as documented.

## Dependencies and Integration Points

It depends on I2C core private structures from `i2c-core.h`, kernel lists, exported symbols, rwsem locking, and slab allocation. It is intended only for I2C core consumption, despite exported symbols.

## Risks

Partial failure leaves earlier entries registered and returns `-ENOMEM`; there is no rollback. Embedded pointers are shallow-copied, which is safe only for lifetime-stable data. Incorrect bus numbers can reserve dynamic bus numbers unexpectedly.

## Test Signals

Test zero-length reservation, multiple device registration, resource deep copy, allocation-failure partial behavior, dynamic bus number advancement, and later adapter registration consuming matching board entries.
