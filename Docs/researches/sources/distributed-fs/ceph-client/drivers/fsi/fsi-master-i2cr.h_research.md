<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.h -->
# sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.h

## Purpose
`fsi-master-i2cr.h` defines the shared structure and helper prototypes for the IBM I2C Responder virtual FSI master.

## Important APIs, types, and functions
`struct fsi_master_i2cr` embeds `struct fsi_master`, stores a mutex protecting hardware access, and stores the backing `struct i2c_client`. It declares `fsi_master_i2cr_read()` and `fsi_master_i2cr_write()`, and provides `to_fsi_master_i2cr()` plus `is_fsi_master_i2cr()`.

## Control flow
The header has no executable control flow except the inline type check, which identifies I2CR-backed masters by testing whether the master parent device is an I2C client.

## State and persistence behavior
It describes runtime-only state shared by I2CR master and client code. There is no persistent data.

## Dependencies and integration points
It depends on I2C, mutexes, and `fsi-master.h`. It is the boundary between the I2CR master implementation and other drivers that can perform direct I2CR operations.

## Risks and edge cases
`is_fsi_master_i2cr()` is structural rather than type-tag based, so it assumes parent device type is sufficient. Callers must hold no assumptions about locking beyond using exported helpers, which serialize on `lock`.

## Test signals
Build coverage, direct helper calls from I2CR consumers, and correct identification of I2CR masters validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fsi/fsi-master-i2cr.h -->
