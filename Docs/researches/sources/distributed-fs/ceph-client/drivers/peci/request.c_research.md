# sources/distributed-fs/ceph-client/drivers/peci/request.c

Purpose: Builds, executes, retries, interprets, and frees PECI protocol requests. It contains command encodings for GetDIB, GetTemp, RdPkgConfig, RdPCIConfigLocal, RdEndpointConfig PCI, and RdEndpointConfig MMIO reads, plus typed response accessors.

Important APIs and functions: `peci_request_alloc()`/`peci_request_free()` manage fixed-buffer requests. `peci_request_status()` maps PECI completion codes to Linux errors. `peci_request_xfer()` serializes through `controller->bus_lock`; `peci_request_xfer_retry()` handles retryable completion codes with exponential sleep and retry-bit setting. Exported `peci_xfer_*` helpers construct and execute protocol-specific reads. Data accessors include `peci_request_data_readb/w/l/q()`, `peci_request_dib_read()`, and `peci_request_temp_read()`.

Control flow: A helper allocates a request with exact TX/RX lengths, writes command bytes and little-endian parameters, performs transfer directly or through retry logic, and returns either an ERR_PTR or a request containing RX data. Retryable completion codes `0x80` through `0x82` cause the retry bit in `tx.buf[1]` to be set, then the request sleeps with a backoff up to 128 ms until a 700 ms overall timeout.

State and persistence: Request state is heap allocated and caller-owned until `peci_request_free()`. `prev_count`-style persistence does not exist; only command buffers and response buffers persist per request. The retry path mutates the TX retry bit in place across attempts. Bus serialization is delegated to the controller mutex.

Dependencies and integration points: Depends on Linux PCI address helpers, unaligned little-endian accessors, PECI public structs, and the controller `.xfer` operation. CPU helper code in `cpu.c` and device detection in `device.c` consume these functions.

Risks: `peci_request_status()` must not be used for commands without completion-code byte, and the code documents that GetDIB/GetTemp/Ping are excluded. New request helpers must account for the first RX byte being completion code for most reads, so data accessors start at `rx.buf[1]`. Retry returns success when the transport succeeds and the final status is not retry, leaving callers to call `peci_request_status()` for non-retry protocol errors.

Test signals: Unit-like command encoding checks, completion-code mapping, retry on `NEED_RETRY`/resource codes, interruptible sleep interruption, bounds warnings for oversized buffers, endian correctness for PCI/MMIO addresses, and successful reads through the exported CPU APIs.
