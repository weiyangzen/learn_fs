## sources/distributed-fs/ceph-client/fs/isofs/util.c

Purpose: provides ISO date/time conversion.

Important API: `iso_date(u8 *p, int flags)` converts short ISO directory timestamps or long-form Rock Ridge timestamps into `struct timespec64`. Flags select long form and High Sierra no-timezone behavior.

Control flow: long form parses ASCII year/month/day/hour/minute/second/hundredths and subtracts 1900 from the year. Short form reads binary year offset, month, day, time, and optional timezone byte. Negative years clamp to epoch zero. Otherwise it calls `mktime64`, sign-extends the timezone byte, and subtracts timezone offset only if within +/-52 fifteen-minute units.

State and persistence: pure conversion helper; no state is stored. Results populate inode atime/mtime/ctime elsewhere.

Dependencies and integration points: used by `inode.c` for ISO directory record dates and by `rock.c` for TF records.

Risks and test signals: risks include malformed date fields, timezone sign compatibility, High Sierra handling, and long-form nanosecond scaling. Test with boundary years 1900 and 2155, negative year inputs, timezone extremes, High Sierra records, and Rock Ridge long-form timestamps.
