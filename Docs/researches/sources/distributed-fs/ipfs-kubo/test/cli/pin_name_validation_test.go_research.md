# sources/distributed-fs/ipfs-kubo/test/cli/pin_name_validation_test.go

Purpose: enforces the 255-byte pin-name limit for `ipfs pin add`, `ipfs pin ls --name`, and `ipfs add --pin-name`. It distinguishes byte length from rune count by including Unicode cases.

Important APIs and functions: `TestPinNameValidation` creates one offline daemon node and one test CID, then runs valid and invalid name cases. `TestAddPinNameValidation` creates a file and verifies `ipfs add --pin-name` accepts and persists valid names and rejects over-limit names. The tests use `strings.Repeat`, `fmt.Sprintf("--pin-name=%s", ...)`, `RunIPFS`, `pin rm`, and `pin ls --names --type=recursive`.

Control flow: valid cases accept empty names, short ASCII, exactly 255 bytes, and Unicode strings within the byte limit. Invalid cases submit 256-byte, 300-byte, and 300-byte Unicode names and expect non-zero exits plus an error mentioning `max 255 bytes`. Name-filter validation checks that a 255-byte filter succeeds while 256 bytes fails. Add-command validation confirms a successfully added file can be listed with the requested pin name, then unpins it.

State and persistence: successful names become pin metadata and are observable through `pin ls --names`. Failed validations must not mutate pin state. Cleanup unpins successfully added CIDs to keep sequential subtests isolated within the shared node.

Dependencies and integration points: covers CLI option parsing, config-independent pin validation, pinner metadata storage, `add` command integration with recursive pin creation, and byte-length validation with UTF-8 input.

Risks and test signals: the tests share nodes inside each top-level test, so state cleanup matters. Regressions show up as accepted over-limit names, rejected valid 255-byte names, missing `max 255 bytes` diagnostics, or `add --pin-name` storing content without the requested name.
