# File Research: sources/block-storage/stratisd/src/bin/stratis-min/stratis-min.rs

Minimal Stratis client binary. It defines a `clap` command tree for `key`, `pool`, `filesystem`, and `report`, then dispatches each command to `stratisd::jsonrpc::client::{key,pool,filesystem,report}`.

Key behavior:
- Parses key operations: `set`, `list`, `unset`; `set` accepts either captured input or `--keyfile-path`, but dispatch passes only the optional file path.
- Parses pool lifecycle commands: `start`, `stop`, `create`, `init-cache`, `rename`, add data/cache devices, destroy, and status predicates.
- Converts pool IDs between name and UUID with `PoolIdentifier::{Name,Uuid}`.
- Handles encryption inputs for pool creation: `--key-descs` values as `key_desc[:token_slot]`; `--clevis-infos` as whitespace-separated key/value pairs with `pin=tang|tpm2`, token slots, Tang URL, thumbprint, or `trust_url`.
- Implements bind/unbind/rebind for keyring and Clevis/Tang/TPM2, including legacy token-slot handling through `OptionalTokenSlotInput`.
- Filesystem subcommands create, destroy, rename, list, and print origin.
- `report` prints formatted JSON from the daemon.

Important details:
- Errors are normalized by `main()` into `Result<(), String>`.
- `parse_args().debug_assert()` is covered by a unit test.
- The file is argument translation glue; filesystem/block-storage semantics are in the JSON-RPC client and engine calls.
