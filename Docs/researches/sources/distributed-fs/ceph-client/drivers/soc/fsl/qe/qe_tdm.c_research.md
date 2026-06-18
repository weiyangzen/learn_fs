# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qe_tdm.c

## Purpose
Provides helper routines for QE UCC TDM configuration. It parses TDM-related device-tree properties, fills `ucc_tdm` and `ucc_tdm_info`, and initializes SI RAM entries plus SI mode registers for E1/T1 timeslot routing.

## Important APIs, types, and functions
Exports `ucc_of_parse_tdm` and `ucc_tdm_init`. Private helpers are `set_tdm_framer`, which maps `"e1"` and `"t1"` to enum values, and `set_si_param`, which adjusts SI mode fields for internal loopback.

## Control flow and state behavior
`ucc_of_parse_tdm` reads `fsl,rx-sync-clock`, `fsl,tx-sync-clock`, TX/RX timeslot masks, `fsl,tdm-id`, optional internal loopback, `fsl,tdm-framer-type`, and `fsl,siram-entry-id`. It converts clocks through `qe_clock_source`, rejects invalid or missing required properties, stores masks and mode into `utdm`, and mirrors TDM port into `ut_info->uf_info.tdm_num`.

`ucc_tdm_init` determines 24 T1 or 32 E1 timeslots, computes the UCC channel select, writes TX and RX SIRAM entries as valid or closed based on timeslot masks, marks the final TX and RX entries with `SIR_LAST`, builds the SIxMR value from SIRAM entry id, loopback/normal mode, and `si_info` flags, and writes the correct SIxMR register for TDM ports 0 through 3.

## Dependencies and integration points
Depends on public QE TDM headers, `qe_clock_source` from `qe.c`, big-endian MMIO, UCC fast info structures, and device-tree bindings used by UCC HDLC/TDM clients.

## Risks and test signals
The function logs and returns errors for missing properties, but one indentation block around invalid TX sync clock should be reviewed for readability. `ucc_tdm_init` only supports TDM ports 0-3 and only E1/T1 slot counts. Test signals include parsing valid E1 and T1 nodes, rejecting invalid clock/framer properties, correct SIRAM valid/closed entries for masks, and loopback SIxMR bits.
