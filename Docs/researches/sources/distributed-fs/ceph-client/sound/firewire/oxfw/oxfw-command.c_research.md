# sources/distributed-fs/ceph-client/sound/firewire/oxfw/oxfw-command.c

## Purpose

This file implements AV/C/FCP command helpers used by OXFW devices for stream format configuration and signal-format probing.

## Important APIs, types, and functions

`avc_stream_set_format()` sends Extended Stream Format Information CONTROL/SINGLE commands. `avc_stream_get_format()` sends STATUS/SINGLE or STATUS/LIST commands and strips the AV/C header before returning stream format bytes. `avc_general_inquiry_sig_fmt()` uses SPECIFIC INQUIRY for input/output plug signal format at a candidate sample rate.

## Control flow

Set-format allocates a command buffer, writes AV/C operands, appends format bytes, uses `fcp_avc_transaction()`, validates response length/status, maps NOT IMPLEMENTED to `-ENXIO` and REJECTED to `-EINVAL`, and frees the buffer. Get-format chooses SINGLE for `eid == 0xff` and LIST otherwise, validates response identity, handles IN TRANSITION as `-EAGAIN`, verifies LIST entry IDs, then `memmove()`s payload bytes to the caller buffer.

## State and persistence behavior

No driver-local state persists here. Successful CONTROL commands modify device stream-format state; inquiries are read-only.

## Dependencies and integration points

It depends on `fcp_avc_transaction()`, AV/C plug direction enums, `amdtp_rate_table`, and constants from `oxfw.h`. `oxfw-stream.c` uses these helpers for discovery, reserve, and assumed-format probing.

## Risks and test signals

Risks include short responses, devices returning transitional statuses, header validation mismatches, and unsupported LIST handling. Tests should include real devices with LIST and SINGLE only behavior, unsupported Miglia-style devices, all rate inquiries, and malformed/short FCP responses.
