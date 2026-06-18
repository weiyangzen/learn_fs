# sources/distributed-fs/ceph-client/fs/pstore/Kconfig

## Purpose
This Kconfig file defines the pstore feature matrix: generic persistent store support, compression, console/pmsg/ftrace frontends, RAM backend, zone manager, and block backend options.

## Important APIs, types, and functions
It introduces symbols `PSTORE`, `PSTORE_DEFAULT_KMSG_BYTES`, `PSTORE_COMPRESS`, `PSTORE_CONSOLE`, `PSTORE_PMSG`, `PSTORE_FTRACE`, `PSTORE_RAM`, `PSTORE_ZONE`, `PSTORE_BLK`, and block backend size/device parameters.

## Control flow
Selections wire dependencies at build time: pstore compression selects zlib inflate/deflate, pmsg selects RT mutexes, ftrace depends on function tracer/debugfs, RAM selects Reed-Solomon ECC support, and block selects `PSTORE_ZONE`.

## State and persistence
The file controls compiled-in capabilities and default module parameter values. Runtime persistence is implemented by the selected backends, not by Kconfig itself.

## Dependencies and integration points
It integrates with architecture I/O memory support, block support, ftrace/debugfs, zlib, Reed-Solomon libraries, and pstore admin documentation.

## Risks and test signals
Risks are invalid default sizing, feature combinations that expose frontends without backend capacity, and confusion between module parameters and Kconfig defaults. Test signals are build coverage for pstore disabled, each frontend alone, RAM, block, compression disabled, and combined frontend/backend configurations.
