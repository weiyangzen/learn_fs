
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc.c

## Purpose
Provides shared QUICC Engine UCC mux and clock routing helper APIs used by UCC fast/slow drivers, TSA/QMC users, Ethernet, serial, and TDM clients. It programs QE mux registers for MII management, UCC speed type, grant/breakpoint/TSA selection, UCC Rx/Tx clocks, and TDM clock/sync sources.

## Important APIs, Types, and Functions
- Exported APIs: `ucc_set_qe_mux_mii_mng()`, `ucc_set_type()`, `ucc_mux_set_grant_tsa_bkpt()` via macros in headers, `ucc_set_qe_mux_rxtx()`, `ucc_set_tdm_rxtx_clk()`, and `ucc_set_tdm_rxtx_sync()`.
- Internal mapping helpers translate UCC number to CMXUCR register/shift and TDM number/direction/clock to mux bit values.

## Control Flow
Each exported setter validates UCC/TDM number and direction, translates enum clock values to hardware bit fields, and updates QE mux registers with `qe_clrsetbits_be32()` or bit set/clear helpers. MII management and GUEMR updates use `cmxgcr_lock` or direct 8-bit GUEMR access where appropriate.

## State and Persistence
State is hardware register state in global `qe_immr->qmx` and UCC GUEMR registers. No private heap state exists. Changes persist until another driver or firmware rewrites the mux.

## Dependencies and Integration Points
Depends on global QE IMMR mapping, QE register helpers, `cmxgcr_lock`, and UCC/QE clock enum definitions. Fast/slow UCC init and TSA connection code call these helpers.

## Risks
- Invalid clock/UCC combinations return `-ENOENT` or `-EINVAL`; callers must handle these as configuration errors.
- Most mux updates outside `cmxgcr_lock` are not locally serialized, so cross-driver concurrent configuration of the same mux fields could race.
- Hardware clock mapping tables are dense and easy to regress when adding SoC variants.

## Test Signals
Unit-style tests can exercise table mappings for all UCC/TDM/clock/direction combinations through mocked registers. Integration tests should boot QE devices using NMSI and TSA modes, reject invalid clock combinations, and verify mux register fields.
