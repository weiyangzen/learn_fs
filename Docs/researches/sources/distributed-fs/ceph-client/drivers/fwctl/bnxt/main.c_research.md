# sources/distributed-fs/ceph-client/drivers/fwctl/bnxt/main.c

## Purpose
`bnxt/main.c` is the Broadcom BNXT fwctl provider. It exposes selected HWRM firmware commands to userspace through the fwctl core, while validating each request against an allowlist and the requested fwctl RPC scope.

## Important APIs, Types, and Functions
`struct bnxtctl_dev` embeds `struct fwctl_device` and stores `struct bnxt_aux_priv *`. `struct bnxtctl_uctx` embeds `struct fwctl_uctx` and per-open capability bits. fwctl callbacks are `bnxtctl_open_uctx()`, `bnxtctl_close_uctx()`, `bnxtctl_info()`, and `bnxtctl_fw_rpc()`. The critical policy functions are `bnxtctl_validate_rpc()` and `bnxtctl_get_timeout()`.

## Control Flow
The auxiliary driver binds `bnxt_en.fwctl`. Probe allocates an fwctl device against the PCI parent, stores the BNXT aux private pointer, registers with fwctl, and stores driver data. Open sets capability bits for inline, query, and send commands. Info returns those caps in `struct fwctl_info_bnxt`.

RPC handling validates request and response sizes against HWRM structures, allocates a response buffer of the caller-requested size, chooses a timeout based on command type, and takes `edev->en_dev_lock`. Validation rejects stopped ULP state and allows only specific HWRM request types, with configuration, debug-read, and debug-write scope thresholds. `bnxt_send_msg()` sends the message. If firmware returns detailed status while the send function returns an error, the provider still returns the response buffer to userspace and fills `error_code` when needed.

## State and Persistence
Per-open state is only capability bits. Device state is the fwctl object and the BNXT auxiliary pointer. There is no persistent storage. The BNXT lock serializes firmware message submission against device state.

## Dependencies and Integration Points
The driver depends on `linux/bnxt/hsi.h`, `linux/bnxt/ulp.h`, auxiliary bus, PCI parent devices, fwctl core, and uapi `fwctl/bnxt.h`. It imports namespace `FWCTL`.

## Risks and Test Signals
The security boundary is the HWRM allowlist and scope mapping, so new firmware commands require careful classification. Default rejection is good, but command aliases or structure changes can invalidate assumptions. Response-size handling trusts userspace to provide at least `sizeof(struct output)` while still passing the full requested size to firmware. Tests should exercise each allowed scope, denied command IDs, ULP-stopped rejection, long-timeout NVM commands, firmware error responses, and remove while fds remain open.
