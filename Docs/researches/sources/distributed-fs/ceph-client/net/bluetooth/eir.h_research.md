# sources/distributed-fs/ceph-client/net/bluetooth/eir.h

## Purpose
This header declares EIR/advertising construction helpers and provides inline routines for common AD element encoding and lookup.

## Important APIs, Types, And Functions
It declares the public functions implemented in `eir.c`. Inline helpers are `eir_precalc_len()`, `eir_append_data()`, `eir_append_le16()`, `eir_skb_put_data()`, and `eir_get_data()`.

## Control Flow
Append helpers encode length, type, and payload into a caller-owned buffer or skb. `eir_get_data()` walks AD elements until it finds a requested type, a zero-length terminator, or malformed/truncated data.

## State, Persistence, And Dependencies
There is no persistent state. The header depends on unaligned little-endian helpers, skbuff APIs for `eir_skb_put_data()`, and visible HCI/Bluetooth types from includers.

## Integration Points
HCI, management, advertising, and EIR parsing code include this header to build payloads consistently. `eir.c` uses the same inline helpers for local-name, appearance, and service-data work.

## Risks
Append helpers do not check destination capacity; callers must perform size accounting. `eir_skb_put_data()` warns if the AD field length would exceed `u8` capacity but still writes based on inputs. `eir_get_data()` returns NULL for zero-length data fields, so callers must distinguish absent data from present empty data if that ever matters.

## Test Signals
Signals include correct AD length calculation, little-endian 16-bit fields, skb tailroom usage under normal callers, and parser behavior on empty, zero-terminated, exact-fit, and truncated advertising buffers.
