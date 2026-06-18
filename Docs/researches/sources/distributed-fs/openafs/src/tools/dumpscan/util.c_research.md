# sources/distributed-fs/openafs/src/tools/dumpscan/util.c

## Purpose
Provides internal helper routines for dumpscan parsing and repair paths. It normalizes low-level parser return codes into user-visible diagnostics, prepares tag parser options from a `dump_parser`, and probes candidate offsets to decide whether a dump stream is positioned at a plausible vnode or dump terminator.

## Important APIs, Types, And Functions
The file exposes `handle_return`, `prep_pi`, and `match_next_vnode`, all marked as intended for internal use. The code works with `XFILE`, `dump_parser`, `tag_parse_info`, `dt_uint64`, AFS vnode type constants, `DUMPENDMAGIC`, dumpscan error codes such as `DSERR_TAG`, `DSERR_DONE`, `DSERR_FMT`, and xfile errors such as `ERROR_XFILE_EOF`. It depends on primitive dump readers like `ReadByte`, `ReadInt32`, and 64-bit formatting helpers `decimate_int64` and `hexify_int64`.

## Control Flow
`handle_return` is the common post-read dispatcher: a zero return is interpreted as an unexpected tag unless the caller already translated successful parser completion to `DSERR_DONE`; EOF and ENOMEM get location-aware callbacks; `DSERR_DONE` is converted to success; other positive codes are reported as system errors, while negative codes are assumed to have already been reported. `prep_pi` zeroes a `tag_parse_info`, copies parser error callback fields, and maps repair flags to tag parser skip flags. `match_next_vnode` seeks to a requested position, reads the next tag, then validates vnode/dump-end shape, vnode ordering, uniquifier bounds, and vnode type parity.

## State And Persistence
The file does not own persistent state. It observes and mutates stream position through `xfseek`, `xftell`, and primitive reads, and it uses parser flags, repair flags, and the parser's `vol_uniquifier` as validation inputs. Error reporting is pushed through callback state stored in `dump_parser`.

## Dependencies And Integration Points
This is shared parser glue for dumpscan modules such as tag, vnode, volume, repair, and primitive parsing. It integrates the xfile abstraction with the dumpscan callback/error model and with AFS dump format conventions from `dumpfmt.h`.

## Risks And Test Signals
Risks include the special meaning of return value `0` in `handle_return`, off-by-one reporting around unexpected tags, and heuristic false positives/negatives in `match_next_vnode` when repairing damaged dumps. Useful tests are malformed tag streams, unexpected EOF at different offsets, ENOMEM injection, `DSFIX_SKIP`/`DSFIX_RSKIP` flag propagation, valid vnode order transitions, dump-end matching, and corrupt vnode uniquifier/type combinations.
