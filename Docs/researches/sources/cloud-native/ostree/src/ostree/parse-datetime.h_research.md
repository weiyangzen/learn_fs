# sources/cloud-native/ostree/src/ostree/parse-datetime.h

Purpose: exposes a GNU-style natural language date/time parser used by OSTree timestamp-related CLI paths.

Important APIs/functions: declares `bool parse_datetime(struct timespec *result, char const *input, struct timespec const *now)`.

Control flow/state: no implementation. `now` may be `NULL`, in which case the implementation reads current realtime. The result is a `timespec` with nanosecond precision.

Dependencies/integration: includes `<stdbool.h>` and `<time.h>`. Consumers must compile/link the Bison-generated parser from `parse-datetime.y`.

Risks: the parser accepts broad human syntax, relative expressions, time zones, and `TZ="..."` prefixes, so callers need to decide whether ambiguous input is acceptable.

Test signals: timestamp CLI and RFC/date tests in the broader tree are the likely coverage points.
