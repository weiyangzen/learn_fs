# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/debug.h

Purpose: Defines logging levels, logging macros, hexdump tracing, and debugfs/memdump declarations or no-op stubs.

Important APIs/types/functions: Message bits cover TRACE, INFO, DATA, CTL, TIMER, HDRS, BYTES, INTR, GLOM, EVENT, BTA, FIL, USB, SCAN, CONN, BCDC, SDIO, MSGBUF, PCIE, and FWCON. Exposes `brcmf_err`, `bphy_err`, `bphy_info_once`, `brcmf_info`, `brcmf_dbg`, `BRCMF_*_ON()`, and `brcmf_dbg_hex_dump()`.

Control flow: All driver files use these macros for rate-limited errors and optional debug/tracing output. `common.c` implements the backing functions when needed.

State and persistence behavior: Logging is controlled by global `brcmf_msg_level` and build config. No persistent state.

Dependencies and integration points: Integrates with wiphy logging, net ratelimit, tracepoints, and Broadcom utility hexdump.

Risks: Non-DEBUG `brcmf_debug_create_memdump()` returns success without creating a dump. DEBUG/tracing maps `brcmf_info` to error logging. Macros assume valid wiphy where used.

Test signals: Build with DEBUG, BRCMDBG, tracing, and none; runtime `debug` module param should gate expected messages.
