# sources/distributed-fs/coda/coda-src/vv/nettohost.cc

## Purpose

`nettohost.cc` converts Coda store ids and version vectors between network byte order and host byte order.

## Important APIs, Types, and Functions

`ntohsid()` and `htonsid()` convert `ViceStoreId::HostId` and `Uniquifier`. `ntohvv()` and `htonvv()` iterate `VSG_MEMBERS` version slots starting at `Versions.Site0`, convert the embedded store id, and convert `Flags`.

## Control Flow

Each function is a straight field-by-field conversion from input pointer to output pointer. Input and output may be distinct; in-place use relies on assignment order being safe for each converted field.

## State and Persistence Behavior

There is no persistent state. The output struct is overwritten with converted values.

## Dependencies and Integration Points

It depends on `<netinet/in.h>` byte-order functions, `vice.h`, `inconsist.h`, and `nettohost.h`. It assumes version slots are contiguous `RPC2_Integer` fields.

## Risks and Test Signals

The code assumes `Flags` is the same width expected by `htonl`/`ntohl`. Layout assumptions would break if `ViceVersionVector` changes away from contiguous site fields. Tests should cover round-trip conversion, non-palindromic values, all `VSG_MEMBERS` slots, flags, store ids, and in-place conversion behavior.
