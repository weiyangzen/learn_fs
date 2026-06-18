# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe_types.h

## Purpose
This header defines AS10x firmware/control-protocol constants and packed structures used by the AS102 frontend shim and parent transport code.

## Important APIs And Types
Constants encode bandwidths, hierarchy priority, modulation, hierarchy alpha, interleaving, FEC code rates, guard intervals, transmission modes, DVB-H flags, tune states, TS PID filter types, context IDs, and configuration modes. Packed structs include `as10x_tps`, `as10x_tune_args`, `as10x_tune_status`, `as10x_demod_stats`, `as10x_ts_filter`, `as10x_register_value`, and `as10x_register_addr`.

## Control Flow And Integration
`as102_fe.c` fills `as10x_tune_args` from DVB frontend properties, reads `as10x_tps` and `as10x_tune_status` through callbacks, and caches `as10x_demod_stats` for metric readers. Parent transport code serializes these packed structs to the hardware.

## State And Persistence
No runtime state exists in the header. The packed structs represent transient command and response payloads.

## Dependencies
The file relies on fixed-width integer types and `__packed` kernel annotation. Correct packing is essential for firmware protocol compatibility.

## Risks
Changing numeric constants or packing breaks device protocol. Several values use `0xff` as unknown/error sentinel, so conversion code must preserve those semantics. Endianness is implicit in field serialization by parent code and should be reviewed if moving across transports.

## Test Signals
Protocol tests should verify `sizeof()` and field offsets for each packed struct. Mock command tests should validate DVB property conversion against expected byte payloads.
