# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/cmd.h

## Purpose
Declares WiLink 8-specific firmware command payloads and prototypes for command helpers implemented in `cmd.c`.

## Important APIs, types, and functions
- `struct wl18xx_cmd_channel_switch` carries role, target channel, switch timing, local supported rates, channel type, and band.
- Smart Config payloads include group bitmap and 16-byte group key command structures.
- DFS payloads include radar debug channel and DFS master restart role id.
- Prototypes expose channel switch, Smart Config start/stop/key, CAC, radar debug, and DFS master restart.

## Control flow
No executable flow. Callers allocate/fill/send these structures through `wl1271_cmd_send()`.

## State and persistence behavior
No local state. Structures describe transient command payloads that mutate firmware state when sent.

## Dependencies and integration points
Includes wlcore core and ACX headers for base command header and driver types. Used by `wl18xx/cmd.c`, `wl18xx/debugfs.c`, and `wl18xx/main.c` operation-table setup.

## Risks and test signals
Firmware ABI accuracy is the main risk. Build tests catch prototype drift; runtime signals include successful CSA, Smart Config operation, DFS CAC, radar debug, and master restart.
