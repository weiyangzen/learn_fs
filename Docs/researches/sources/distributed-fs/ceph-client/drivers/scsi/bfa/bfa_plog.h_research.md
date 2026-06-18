<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_plog.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_plog.h

## Purpose
`bfa_plog.h` defines the fixed-size per-port circular log used by the BFA driver to capture driver, HAL, FCS, login, FC exchange, unsolicited-frame, IOC, port, CT, RSCN, FIP, trunking, and debug events. It provides record formats, module/event IDs, string-length contracts, and logging function prototypes.

## Important APIs, Types, And Functions
Important constants are `BFA_PL_NLOG_ENTS` (256 records), `BFA_PL_STRING_LOG_SZ` (32 bytes), `BFA_PL_INT_LOG_SZ` (8 integers), `BFA_PL_SIG_LEN`, and `BFA_PL_SIG_STR`. `enum bfa_plog_log_type` distinguishes invalid, integer, and string log records. `struct bfa_plog_rec_s` is the fixed record layout with timestamp, source port, module ID, event ID, log type, integer count, misc field, and a union of string or integer payload. `enum bfa_plog_mid` and `enum bfa_plog_eid` define stable numeric IDs for log producers and events.

`struct bfa_plog_s` is the ring buffer: signature, enabled flag, ticks, head/tail indexes, and 256 records. Public APIs are `bfa_plog_init()`, `bfa_plog_str()`, `bfa_plog_intarr()`, `bfa_plog_fchdr()`, and `bfa_plog_fchdr_and_pl()`.

## Control Flow
The header establishes the expected logging flow. Initialization writes the signature and clears/sets ring state. Producers call the string, integer-array, FC-header, or FC-header-plus-payload helper with a module ID, event ID, misc value, and payload. The ring advances through `BFA_PL_LOG_REC_INCR()`, which wraps indexes modulo `BFA_PL_NLOG_ENTS`.

## State And Persistence
Port-log state is volatile in-memory state attached to `struct bfa_s` through `bfa->plog`. The buffer is fixed-size and circular, so old records are overwritten as head/tail advance. The signature and ID/string enum ordering form a compatibility contract with BFAL or other user/debug tooling that decodes numeric module and event values.

## Dependencies And Integration Points
The header includes `bfa_fc.h` for FC header structures and `bfa_defs.h` for shared driver definitions. Logging helpers integrate with FC frame paths, IOCTL/debug paths, FCS, LPS, and HAL modules that pass module/event IDs. The comments explicitly require appending new module/event IDs and defining corresponding strings in BFAL, indicating an external decoder dependency.

## Risks And Test Signals
Risks include enum reordering/removal breaking log decoders, string payload truncation to 32 bytes, integer payload truncation to eight words, ring overwrite hiding older failures, and concurrent producers needing implementation-side synchronization not visible in this header. FC header logging must respect byte ordering and structure layout when implemented.

Good test signals include plog initialization signature checks, wraparound at 256 records, logging while disabled/enabled, decoder compatibility for existing module/event IDs, string and integer record boundary tests, and FC header logging from TX/RX paths with expected misc length fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/bfa/bfa_plog.h -->
