# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/ptpchmaskfmt.sh

Purpose: helper to display PTP debugfs timestamp event queue filtering masks in hexadecimal form.

Important APIs and functions: reads integer tokens from a provided debugfs mask file and prints each with `printf '0x%08X '`.

Control flow: set `DEBUGFS_MASKFILE` to argument 1, iterate over all whitespace-separated integers in the file, print hex masks on one line.

State and persistence: read-only.

Dependencies and integration: expects bash, readable debugfs mask file, and numeric contents acceptable to printf.

Risks and test signals: unquoted command substitution intentionally splits whitespace but will also perform glob-like issues if file content is unusual. It is a formatting helper, not a validator.
