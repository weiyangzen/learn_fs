# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/uncore-frequency/uncore-frequency-common.h

## Purpose

This header defines the common data model and callback contract for Intel uncore frequency control backends.

## Important APIs, Types, And Functions

It defines agent type bitmasks, `struct uncore_data`, `UNCORE_DOMAIN_ID_INVALID`, `enum uncore_index`, and prototypes for common init/exit and entry add/remove functions. `struct uncore_data` contains hardware metadata, cached initial frequencies, control CPU, sysfs attribute storage, and an attribute pointer array.

## Control Flow

Backends allocate/fill `struct uncore_data`, initialize common callbacks, add entries when control CPUs/devices are available, and remove entries during teardown or CPU/device removal.

## State And Persistence

The header defines fields used for runtime state but owns none itself. `stored_uncore_data` is reserved for backend resume restoration.

## Dependencies And Integration Points

It includes Linux device/sysfs types and is shared by the common module plus uncore frequency backends.

## Risks

`uncore_attrs[15]` must be large enough for all optional attributes; adding fields in common code requires increasing this bound. Backends must keep `control_cpu`, package/die/domain IDs, and agent masks consistent with hardware.

## Test Signals

Compile backends, sysfs attribute count coverage, domain and package mode entries, and backend read/write callback invocation for every `enum uncore_index` validate the contract.
