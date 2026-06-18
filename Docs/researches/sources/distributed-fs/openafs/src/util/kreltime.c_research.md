# sources/distributed-fs/openafs/src/util/kreltime.c

Purpose: Implements relative date parsing, encoding, display, and addition for AFS time utilities.

Important APIs: `ktimeRelDate_ToInt32()` encodes year/month/day relative fields. `Int32To_ktimeRelDate()` decodes them. `ktimeDate_FromInt32()` converts absolute seconds to `struct ktime_date`. `ParseRelDate()` parses `<n>y<n>m<n>d` style strings. `RelDatetoString()` formats a relative date. `Add_RelDate_to_Time()` adds a relative date to an absolute time.

Control flow and state: Parsing walks fields in the fixed order year, month, day, accepts up to four digits per component, and enforces month/day maxima. Addition first converts the base time to a local calendar date, adds years and months at calendar granularity, converts back through `ktime_InterpretDate()`, then adds days/hours/min/sec in seconds.

Dependencies and integration: Includes `ktime.h` and `afsutil.h`; relies on `ktime_InterpretDate()` from `ktime.c`. Used by expiration/relative-date command parsing.

Risks and test signals: `RelDatetoString()` returns static storage and is not thread-safe. Month overflow handling treats month `12` specially via modulo and may produce subtle calendar behavior. Day additions use 24-hour seconds, so DST transitions can differ from calendar-day semantics. Test signals are date parsing and expiration behavior in commands.
