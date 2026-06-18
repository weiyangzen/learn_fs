<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/check-blacklist-hashes.awk -->
# sources/distributed-fs/ceph-client/certs/check-blacklist-hashes.awk

## Purpose

`check-blacklist-hashes.awk` validates the configured blacklist hash list before it is included into C source. It enforces the string, prefix, lowercase hex, maximum length, and even-length rules described by Kconfig.

## Important APIs, Types, And Functions

This is an AWK script. It sets `RS = ","` so each comma-separated initializer item is validated independently. It uses `match()` to extract the quoted string, split prefix and hash, and check hex constraints.

## Control Flow

For each comma-separated item, the script requires a quoted string. The string must match `tbs:<hash>` or `bin:<hash>`. The hash must be lowercase hexadecimal, no longer than 128 characters, and have an even number of characters. On any violation, it prints a specific error message with item number and exits with status `1`.

## State And Persistence Behavior

The script holds only AWK variables while validating build input. It does not write output; the Makefile handles copying after validation succeeds.

## Dependencies And Integration Points

It is invoked by `cmd_check_and_copy_blacklist_hash_list` in `certs/Makefile`. Its output goes to stderr so build failures explain which item is invalid.

## Risks And Edge Cases

Because the record separator is a comma, embedded commas inside strings are not supported and would fail validation. Uppercase hex is intentionally rejected to match runtime `blacklist_vet_description()`. An empty hash is rejected because the hex match requires at least one digit.

## Test Signals

Tests should feed valid `tbs` and `bin` strings, unknown prefixes, unquoted input, uppercase hex, odd-length hashes, overlong hashes, empty hashes, and multiple comma-separated entries. Expected invalid cases exit nonzero with a diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/certs/check-blacklist-hashes.awk -->
