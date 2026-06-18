<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/sed-opal.c -->
# sources/distributed-fs/ceph-client/block/sed-opal.c

## Purpose

`sed-opal.c` implements the kernel block-layer support for TCG Opal self-encrypting drives. It builds and parses Opal protocol packets, manages sessions, performs discovery, exposes privileged ioctl operations for ownership, locking ranges, passwords, MBR shadowing, revert, secure erase, SUM status, generic table I/O, and stack reset, and stores an optional SED authentication key in a kernel keyring.

## Important APIs, Types, And Functions

The exported lifecycle/API functions are `init_opal_dev()`, `free_opal_dev()`, `sed_ioctl()`, and `opal_unlock_from_suspend()`. `struct opal_dev` owns the transport callback, command/response buffers, COMID/session identifiers, geometry, flags, parsed response tokens, saved suspend unlock data, and `dev_lock`.

Protocol construction uses `cmd_start()`, `cmd_finalize()`, `finalize_and_send()`, `add_token_u8()`, `add_token_u64()`, `add_token_bytestring()`, `add_bytestring_header()`, and UID builders such as `build_locking_range()` and `build_locking_user()`. Response parsing uses `response_parse()`, `response_get_token()`, `response_get_string()`, `response_get_u64()`, `response_status()`, and `parse_and_check_status()`.

High-level operations are expressed as arrays of `struct opal_step` executed by `execute_steps()`, which automatically runs discovery first and closes a session on mid-sequence failure. Operation wrappers include `opal_take_ownership()`, `opal_activate_lsp()`, `opal_reactivate_lsp()`, `opal_setup_locking_range()`, `opal_lock_unlock()`, `opal_reverttper()`, `opal_revertlsp()`, `opal_set_new_pw()`, `opal_set_new_sid_pw()`, `opal_activate_user()`, `opal_secure_erase_locking_range()`, `opal_generic_read_write_table()`, `opal_get_status()`, `opal_get_geometry()`, and `opal_stack_reset()`.

## Control Flow

`init_opal_dev()` allocates the device state and two 2048-byte DMA-safe buffers, initializes the mutex/list, stores the transport callback, and calls `check_opal_support()`. Discovery sets COMID to the discovery COMID, receives a discovery0 page, validates feature descriptors, records locking/MBR/SUM flags and geometry, and stores the real COMID for later commands.

Every ioctl enters through `sed_ioctl()`, which requires `CAP_SYS_ADMIN`, a supported `opal_dev`, and copies input payloads with `memdup_user()` for commands with `IOC_IN`. It dispatches to the matching wrapper and copies output for status, geometry, discovery, LR status, and SUM status paths.

Most wrappers resolve keys through `opal_get_key()`, lock `dev_lock`, reset session scratch state with `setup_opal_dev()`, and execute an ordered command sequence. Session start functions authenticate as Anybody, SID, PSID, Admin1, or a locking-range user, then `start_opal_session_cont()` extracts host and TPer session numbers. Individual command builders modify Opal tables or invoke methods, and `end_opal_session()` clears session ids after a successful end-session response.

Suspend support stores selected unlock requests in `dev->unlk_lst` via `IOC_OPAL_SAVE`. `opal_unlock_from_suspend()` replays saved unlocks and optionally sets MBR Done on resume.

## State And Persistence Behavior

Kernel state persists for the lifetime of `struct opal_dev`: support flags, COMID, geometry, command buffers, saved suspend unlock list, and the SED keyring pointer. Session ids, parsed responses, and `prev_data` are transient per command sequence. `sed_opal_init()` creates `.sed_opal`, seeds it from `sed_read_key(OPAL_AUTH_KEY)`, and updates it after password changes with `update_sed_opal_key()`; it also attempts to write new keys to the platform key store with `sed_write_key()`.

Persistent device state lives inside the Opal drive: ownership PINs, LockingSP lifecycle, locking-range start/length/enabled/locked bits, generated active keys, MBR table contents, SUM configuration, and revert state. The kernel issues authenticated protocol commands to change that persistent state.

## Dependencies And Integration Points

The file depends on block device headers, `uapi/linux/sed-opal.h`, `linux/sed-opal.h`, `linux/sed-opal-key.h`, kernel keyrings, user-copy APIs, and local `opal_proto.h`. Its transport is supplied by the block driver through a `sec_send_recv` callback using `TCG_SECP_01` and `TCG_SECP_02`. User space reaches it through block ioctls.

## Risks And Edge Cases

This file handles privileged secrets and device-bricking operations. Key handling must avoid accepting empty or oversized keys, leaking copied keys, or using saved unlock keys for the wrong locking range. All user pointers in table read/write and discovery paths must be range-checked and copied safely.

Packet construction is bounded by `IO_BUFFER_LENGTH`; `can_add()`, `remaining_size()`, and finalize padding prevent buffer overruns, but every command builder must propagate `err`. Response parsing is bounded by header lengths and `MAX_TOKS`; responses with more tokens than expected are a risk because the token array is fixed-size and parser changes must preserve that bound.

Protocol state is subtle. Some controller methods terminate sessions themselves, while normal sequences must call `end_opal_session()`. `execute_steps()` only attempts session cleanup after a session-start step has plausibly run. Discovery feature flags must be refreshed because device lock state can change across commands and suspend/resume.

## Test Signals

Useful tests include devices with no Opal support, discovery pages for Opal v1/v2, invalid discovery lengths, all ioctl permission failures, included-key and keyring-key paths, lock/unlock RO/RW/LK transitions, SUM and non-SUM locking, setup range start/length, MBR enable/done/write, table read/write chunking, PSID/SID/Admin1 session failures, revert cleanup of saved unlocks, stack reset pending/failure/success, and suspend replay. Expected signals are correct errno propagation, no command buffer overflow, proper user-copy behavior, and serialized operations under `dev_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/block/sed-opal.c -->
