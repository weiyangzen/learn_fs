# File Research: sources/block-storage/util-linux/libmount/samples/statmount.c

Sample demonstrating direct and on-demand `statmount()` data retrieval for one filesystem.

Key responsibilities:
- Accepts a mountpoint or numeric mount ID.
- Creates an `Fs` and identifies it by target or unique ID.
- Fetches all statmount data directly.
- Resets the FS and demonstrates lazy/on-demand statmount reads through a shared `libmnt_statmnt`.

Important behavior:
- Numeric argv is treated as a mount ID; non-numeric argv as a mountpoint.
- Shows that reading fstype/root triggers targeted statmount reads.
- Final full fetch fills missing statmount data.

Dependencies:
- Depends on libmount statmount support, `mountutils.h` fallbacks, and `strutils.h`.

Notable risks:
- New-kernel functionality; older systems may warn on statmount fetch.
- Intended as a diagnostic sample rather than a robust command-line tool.
