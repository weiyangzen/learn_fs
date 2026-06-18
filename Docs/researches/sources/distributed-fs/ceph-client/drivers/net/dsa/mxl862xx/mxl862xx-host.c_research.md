# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/mxl862xx-host.c

## Purpose
Implements the MxL862xx MDIO/MMD host transport, including CRC-6 protected command registers, CRC-16 protected payload data, command batching, reset, and CRC-error shutdown handling.

## Important APIs, Types, and Functions
Exports `mxl862xx_api_wrap`, `mxl862xx_reset`, `mxl862xx_host_init`, and `mxl862xx_host_shutdown`. Internal functions include CRC error work, `mxl862xx_crc6`, encode/verify helpers, raw register read/write, busy wait, `mxl862xx_issue_cmd`, data pagination helpers, reset-data optimization, and firmware error translation.

## Control Flow and State
`mxl862xx_api_wrap` takes the MDIO lock, waits for idle, optionally resets the firmware data buffer when many zero words are present, writes payload words plus CRC16 through the data window, pages data with SET_DATA commands, issues the API command, optionally reads response words with GET_DATA commands, verifies CRC16, and returns the firmware result. `mxl862xx_issue_cmd` encodes CRC6 into control/length registers, waits for BUSY clear, verifies response CRC6, and extracts signed firmware return values. CRC failures set `MXL862XX_FLAG_CRC_ERR` and schedule work that closes CPU-port conduits.

## Dependencies and Integration Points
Depends on MDIO Clause 45 access, bus `mdio_lock`, CRC16, workqueues, RTNL, DSA CPU ports, `mxl862xx_priv`, firmware command IDs, and the main driver API wrapper calls.

## Risks and Test Signals
Risks include CRC bit packing mistakes, odd-size payload boundary bugs, paging off-by-one errors, lock nesting issues, over-broad port shutdown on transient CRC errors, and duplicated MMD constants drifting from `mxl862xx-cmd.h`. Test signals include CRC6 known vectors, odd/even payload round trips, multi-page payloads, firmware CRC error injection, reset command verification, and concurrent API callers.
