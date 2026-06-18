# sources/distributed-fs/ceph-client/tools/crypto/ccp/dbc_cli.py

Purpose: Command-line interface for Dynamic Boost Control operations through `dbc.py`.

Important APIs, types, and functions: `ERRORS` maps errno values to user-friendly messages. `messages` maps command message names to DBC tuples. `_pretty_buffer()` hex-formats bytes. `parse_args()` declares `get-nonce`, `get-param`, `set-param`, and `set-uid`. `pretty_error()` prints known errno text.

Control flow: Parses arguments, validates device existence, reads optional signature and UID files with exact length checks, parses decimal or hex data, opens the device, dispatches command, validates get/set message direction, calls wrapper functions, and prints nonce/parameter/signature or friendly errors.

State and persistence: Mutates DBC device state for set UID and set parameter. Reads signature/UID files. No local writes.

Dependencies and integration points: Depends on `dbc.py`, local shared library, `/dev/dbc`, and Python standard modules. Intended as a user tool for AMD PSP DBC.

Risks: Opening device with text mode `open(args.device)` is adequate for fd use but not explicit binary/read-write. Some required combinations, such as missing signature for set-param, are left for wrapper errors. `_pretty_buffer()` returns Python bytes repr text, not a bare hex string.

Test signals: CLI argument validation, invalid file lengths, get/set message mismatch, missing device, and expected errno translations on secured/unfused systems.
