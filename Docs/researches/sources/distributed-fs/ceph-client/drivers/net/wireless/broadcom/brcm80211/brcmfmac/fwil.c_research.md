# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/fwil.c

Purpose: Implements Firmware Interface Layer helpers that serialize host commands and iovar access to firmware through the active protocol.

Important APIs/types/functions: Command data set/get, iovar data set/get, bsscfg data set/get, and XTLV data set/get. Internal builders create iovar, bsscfg-prefixed iovar, and XTLV command buffers. Debug builds map firmware BCME errors to strings.

Control flow: Public calls lock `drvr->proto_block`, build/use `drvr->proto_buf`, call protocol set/query via `brcmf_fil_cmd_data()`, log hexdumps, copy returned data, and unlock. `brcmf_fil_cmd_data()` rejects bus-down state, clamps direct command length, calls protocol, and maps firmware errors to `-EBADE` unless raw firmware errors are requested.

State and persistence behavior: Shared `proto_buf` is transient and mutex-protected. Firmware state changes through set operations. `ifp->fwil_fwerr` changes error reporting semantics.

Dependencies and integration points: Used by common, core, cfg80211, feature, vendor, and bus support. Depends on proto, bus, xtlv, tracepoints, and `fwil.h` command IDs.

Risks: Lock ordering around `proto_block` matters. Iovar construction fails if buffers are too small. Get helpers copy requested length from `proto_buf`, relying on firmware to provide enough data. Raw firmware error mode is mutable per interface.

Test signals: Bus-down `-EIO`, unsupported firmware error mapping, buffer-too-short `-EPERM`, concurrent iovar serialization, and endian int wrapper round trips.
