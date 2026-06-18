# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_dap_fasi.h

## Purpose
`drx_dap_fasi.h` defines compile-time configuration and address flag macros for the DRX Data Access Protocol Fast Access Sequential Interface. FASI is an I2C-oriented protocol using short or long register-address formats and single-master or multi-master transaction behavior.

## Important APIs, Types, and Functions
The header sets defaults for `DRXDAPFASI_LONG_ADDR_ALLOWED`, `DRXDAPFASI_SHORT_ADDR_ALLOWED`, `DRXDAP_SINGLE_MASTER`, `DRXDAP_MAX_WCHUNKSIZE`, and `DRXDAP_MAX_RCHUNKSIZE`, then validates combinations with preprocessor errors. Public protocol flags include `DRXDAP_FASI_RMW`, `DRXDAP_FASI_BROADCAST`, `DRXDAP_FASI_CLEARCRC`, `DRXDAP_FASI_SINGLE_MASTER`, `DRXDAP_FASI_MULTI_MASTER`, `DRXDAP_FASI_SMM_SWITCH`, `DRXDAP_FASI_MODEFLAGS`, and `DRXDAP_FASI_FLAGS`. Address macros extract block, bank, and offset and classify short/long format eligibility.

## Control Flow
The header is included by DRX access-protocol code after `drx_driver.h`. Compile-time conditionals choose minimum write chunk size based on address format and master mode, reject impossible configurations, and enforce even read chunk sizes. Runtime code then uses the address and flag macros to encode FASI operations.

## State and Persistence
There is no runtime state. The only state is compile-time feature selection and constants that shape buffer sizing and transaction encoding.

## Dependencies and Integration Points
It depends on `drx_driver.h`, which supplies default DAP chunk sizes and master-mode policy. It integrates generic DRX register access code with FASI-capable demod firmware/hardware.

## Risks and Edge Cases
Misconfigured chunk sizes fail compilation, which is good for safety but can surprise downstream ports with smaller I2C limits. The default allows both short and long addressing; platforms requiring only one mode must override the macros before inclusion. Address classification relies on bit masks such as `0xFC30FF80`, so new address maps need careful validation.

## Test Signals
Compile coverage should include short-only, long-only, both-format, single-master, and multi-master builds. Runtime validation should exercise read, write, read-modify-write, broadcast, CRC-clear, short-format boundary, long-format address, and offset-too-large paths.
