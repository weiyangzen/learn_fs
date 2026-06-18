# sources/cloud-native/ostree/tests/test-rollsum-cli.c

## Purpose
This small C helper is a CLI for manually computing OSTree rollsum matches between two files. It is primarily a test/debug executable rather than a GLib TAP test.

## Important APIs, Types, And Functions
It uses `g_mapped_file_new`, `g_mapped_file_get_bytes`, `_ostree_compute_rollsum_matches()`, `OstreeRollsumMatches`, and prints `crcmatches`, `bufmatches`, `total`, and `match_size`.

## Control Flow
The program requires two path arguments, maps both files read-only into `GBytes`, computes rollsum matches, prints summary metrics to stderr, and returns nonzero on missing args or file mapping errors.

## State And Persistence
No persistent state is written. The program maps input files and allocates match structures in memory.

## Dependencies And Integration Points
This integrates the private rollsum implementation with simple file inputs. It sets `GIO_USE_VFS=local` to avoid non-local VFS behavior in tests.

## Risks
The helper does not free `matches` explicitly in the visible path, but process exit bounds leak impact. It assumes mapped files fit address space and only reports aggregate metrics, not detailed matches.

## Test Signals
Successful execution prints a line beginning `rollsum crcs=`. Errors print the GLib error message and exit with status 1.
