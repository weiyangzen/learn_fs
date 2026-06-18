# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/validate.h

This header exposes journal validation and text-rendering APIs.

Key elements:
- Declares `bch2_journal_entry_err_msg()`, entry validation/text helpers, full `jset` validation, and early `jset` validation.
- Defines `journal_entry_err()` and `journal_entry_err_on()` macros that integrate journal validation with fsck repair policy.
- Defines `JOURNAL_ENTRY_NONE` and `JOURNAL_ENTRY_BAD` sentinel return values used by journal scanning.

Important behavior:
- Read-time validation calls `mustfix_fsck_err()`.
- Write-time validation increments persistent fsck error counts and can make the filesystem inconsistent/read-only if corrupt metadata would be written.
- The macros rely on local variables such as `from` and `ret`, so callers must follow the expected validation-function structure.
