# sources/distributed-fs/ceph-client/fs/smb/client/smb2misc.c

## Purpose

This file provides miscellaneous SMB2/SMB3 protocol helpers: response header and length validation, data-area sizing, path conversion, lease-state construction, oplock/lease break dispatch, cleanup for cancelled creates/closes, and SMB3.1.1 preauthentication hash updates. It is a shared support layer for SMB2 transport and file/inode code.

## Important APIs, types, and functions

- `smb2_check_message()` validates a received SMB2 frame: protocol signature, server-to-client flag or allowed oplock-break request, header structure size, command range, response `StructureSize2`, maximum length, calculated length, negotiate context sizing, and known server padding quirks.
- `smb2_get_data_area_len()` extracts variable data offset/length for commands with payloads, with caps for suspicious offsets and lengths.
- `smb2_calc_size()` calculates expected SMB2 frame size from header, fixed parameter area, and optional data area.
- `cifs_convert_path_to_utf16()` strips disallowed leading separators for Windows/POSIX-extension paths and converts to UTF-16 using mount NLS/remapping.
- `smb2_get_lease_state()` maps CIFS cache flags and mount cache options to SMB2 lease-state bits.
- `smb2_is_valid_oplock_break()` and `smb2_is_valid_lease_break()` locate matching open files, pending opens, or cached directories and queue the appropriate break handling.
- `smb2_handle_cancelled_close()` and `smb2_handle_cancelled_mid()` schedule asynchronous closes for handles that might otherwise leak after interrupted commands.
- `smb311_update_preauth_hash()` updates the SMB3.1.1 preauth SHA-512 chain for negotiate and session setup traffic.

## Control flow

Receive validation begins with `smb2_check_message()`, which handles transform headers enough to find the session, checks the SMB2 header, validates fixed sizes from `smb2_rsp_struct_sizes`, calculates frame length, and tolerates documented server padding/excess cases. Size calculation delegates to `smb2_get_data_area_len()` based on command-specific offset/length fields.

Oplock-break handling distinguishes classic oplock responses from lease-break responses by structure size. It walks sessions and tree connections on the primary server, searches open file lists under `open_file_lock`, updates file/inode oplock state, sets pending-break flags, increments stats, and queues break work. Pending opens requiring acknowledgment are handled by copying the lease key and queuing `SMB2_lease_break()` work.

Cancelled handle cleanup allocates a `close_cancelled_open`, takes/owns a tcon reference when safe, and queues `SMB2_close()` on `cifsiod_wq`. Preauth hashing updates the session hash only for negotiate and relevant SMB3.1.1 session-setup messages.

## State and persistence behavior

Local state includes lease/oplock levels and epochs on `cifsFileInfo`, `CIFS_INODE_PENDING_OPLOCK_BREAK`, pending-open oplock values, tcon statistics, tcon references, queued work items, and `ses->preauth_sha_hash`. Remote state can be changed by queued lease-break acknowledgments and asynchronous closes. No local disk persistence is performed.

## Dependencies and integration points

The file depends on crypto SHA-512, CIFS core/session/tcon/open-file structures, cached directory lease handling, SMB2 status/PDU definitions, tracepoints, workqueues, and path conversion helpers. `transport.c` uses `smb311_update_preauth_hash()` during send/receive; SMB2 transport validation uses `smb2_check_message()`; cancellation paths use the handle cleanup helpers.

## Risks and edge cases

Length validation must balance strictness against real server padding quirks; accepting too much risks malformed-frame bugs, while rejecting tolerated padding can break interoperability. Lease-break scanning holds global session and per-tcon locks, so ordering and early unlock paths must stay correct. Cancelled close handling must not resurrect a closing tcon or leak a reference. Preauth hashing must skip the final successful session setup response and non-SMB3.1.1 traffic or authentication will fail.

## Test signals

Useful signals include packet-level validation tests for malformed SMB2 lengths and structure sizes, interoperability tests against servers with negotiate contexts and compound padding, oplock/lease-break integration tests, cancelled create/close interruption tests that watch server handle counts, and SMB3.1.1 authentication tests that verify preauth hash behavior. No direct KUnit file is included in this subset.
