# sources/distributed-fs/ceph-client/drivers/gpib/include/gpib_cmd.h

## Purpose

`gpib_cmd.h` defines IEEE-488/GPIB command byte constants and small helpers for constructing and classifying command bytes and GPIB addresses.

## Important APIs and Constants

- `enum cmd_byte` names universal/addressed commands such as `GTL`, `SDC`, `GET`, `TCT`, `LLO`, `DCL`, `SPE`, `SPD`, `UNL`, `UNT`, listen/talk address bases `LAD`/`TAD`, and secondary/parallel-poll bases.
- `gpib_address_restrict()` clamps primary addresses to usable 0-30 range by mapping 31 back to 0.
- `MLA()`, `MTA()`, and `MSA()` construct listen, talk, and secondary address command bytes.
- `gpib_address_equal()` compares primary/secondary address pairs, treating two negative secondary addresses as equal/no-secondary.
- `is_PPE()`, `is_PPD()`, and `in_*_command_group()` classify command byte groups by high bits.

## Control Flow and Integration

The helpers are inline and pure. Driver and core code use them when composing command streams and validating command pass-through groups.

## State and Persistence Behavior

No state is stored. All behavior is deterministic by input byte/address.

## Dependencies

The header includes `linux/types.h` for fixed-size integer types. It is included by private gpib headers and drivers.

## Risks and Test Signals

The helpers intentionally mask command/address bits, so tests should include boundary addresses 0, 30, and 31, secondary address disabled cases, and command group classification for all high-bit groups. Misclassification affects bus command routing and pass-through handling.
