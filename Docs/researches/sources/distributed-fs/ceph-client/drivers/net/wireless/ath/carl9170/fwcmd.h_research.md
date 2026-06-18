# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/fwcmd.h

## Purpose

`fwcmd.h` defines the packed host/firmware command and response ABI for carl9170. It assigns command opcodes, response/trap opcodes, maximum command sizes, payload structures, TX status encoding, PHY/RF command fields, PSM, RX filtering, beacon control, WoW, GPIO, TSF, and tally response formats.

## Important APIs, Types, and Functions

The primary ABI objects are `struct carl9170_cmd_head`, `struct carl9170_cmd`, and `struct carl9170_rsp`. Command-specific payloads include key set/disable, register read/write, byte write, RF init, PSM, RX filter, beacon control, and WoW structures. Response payloads include `_carl9170_tx_status`, GPIO, TSF, and tally structures. Constants define API range, async command flagging, RX filter semantics, WoW triggers, TX status bit masks, and firmware diagnostic text markers.

## Control Flow

The header has no control flow but constrains every `carl9170_exec_cmd()` exchange. Callers fill payloads and opcodes, the transport sends them to firmware, and responses are decoded through `struct carl9170_rsp`. Async opcodes are constructed by ORing the normal opcode with `CARL9170_CMD_ASYNC_FLAG`. TX completion response parsing uses compact two-byte `_carl9170_tx_status` entries to avoid C bitfield layout issues on the host side.

## State and Persistence Behavior

Commands described here mutate firmware and hardware state: register writes, software reset/reboot, beacon control, RX filters, WoW programming, key cache entries, RF/channel state, and power-save state. Responses feed persistent driver accounting such as TX completion, TSF, GPIO events, hardware tally counters, and firmware error/diagnostic text.

## Dependencies and Integration Points

The ABI is consumed by command transport, firmware parsing, MAC setup, main lifecycle code, PHY channel code, beacon code, RX/TX completion paths, and USB transport paths. It depends on Linux endian annotations, packed/aligned layout, and descriptor feature bits that declare which commands the loaded firmware supports.

## Risks and Edge Cases

All structures are packed ABI contracts; adding fields or changing alignment would break firmware compatibility. `CARL9170_MAX_CMD_PAYLOAD_LEN` is 60 bytes, so callers must enforce payload sizes. RX filter constants are inverted from an intuitive "accept" model: set bits mean matching frames are discarded. Host code avoids firmware-side TX status bitfields except under `__CARL9170FW__`.

## Test Signals

Compile-time checks should cover structure sizes and payload limits. Runtime tests should exercise register read/write, echo, key set/delete, RX filter, TSF read, RF init, PSM, beacon control, tally, WoW, async reboot, and TX completion decoding. Trace command headers to verify `len`, `cmd`, `seq`, and response opcodes.
