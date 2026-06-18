# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/reclaim.h

## Role

Public interface and inline helpers for journal reclaim and pin tracking.

## Contents

- Defines `JOURNAL_PIN` default pin FIFO size.
- Provides `journal_reclaim_kick()`.
- Declares space accounting and watermark helpers.
- Defines `journal_pin_list_init()`, `journal_pin_active()`, and `journal_seq_pin()`.
- Declares last-seq updates, replay pin drops, pin set/copy/drop/flush helpers, discard work, reclaim start/stop, pin flushing, device-pin flushing, and diagnostics.

## Notable Details

`bch2_journal_pin_add()` only moves a pin to an older sequence, while `bch2_journal_pin_update()` only moves it to a newer sequence; both funnel through `bch2_journal_pin_set()`.
