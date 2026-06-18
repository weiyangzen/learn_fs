# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/accounting.rs

Wraps filesystem accounting ioctl support and re-exports bindgen accounting helpers.

Core behavior:
- Adds `BcachefsHandle::query_accounting(type_mask)`.
- Builds a flexible buffer with `QueryAccountingHeader` followed by u64 accounting data.
- Issues `BCH_IOCTL_QUERY_ACCOUNTING` as `_IOW(0xbc, 21, QueryAccountingHeader)`.
- Retries with doubled buffer size on `ERANGE`.
- Returns `ENOTTY` for old kernels without the ioctl.
- Parses accounting bkey records into `AccountingEntry { pos, counters }`.

Parsing details:
- Assumes bkey header is 5 u64s and `bpos` starts at byte offset 20.
- Uses kernel module version to decide whether `bpos` needs byte swapping for pre-big-endian-disk-accounting metadata.
- Stops on zero `key_u64s`, too-small entries, or entries extending past the buffer.

Potential concerns:
- Raw bkey layout parsing is tightly coupled to kernel struct layout and endianness assumptions.
- Counter u64s are read as native endian without additional swabbing, which may be correct for ioctl output but should remain aligned with kernel ABI.
