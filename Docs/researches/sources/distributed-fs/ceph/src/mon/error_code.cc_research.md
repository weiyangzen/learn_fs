# sources/distributed-fs/ceph/src/mon/error_code.cc

## Purpose
`error_code.cc` implements the monitor-specific Boost error category. The monitor category mostly wraps POSIX-style negative errors while fitting Ceph's `ceph::converting_category` interface.

## Important APIs, Types, and Control Flow
`mon_error_category` overrides `name()`, both `message()` forms, `default_error_condition()`, `equivalent()`, and `from_code()`. `message()` returns `"No error"` for zero and delegates nonzero values to `cpp_strerror()`. `default_error_condition()` maps the monitor value to the generic category. `from_code()` converts Ceph's negative errno convention into a positive category value by returning `-ev`. `mon_category()` returns a function-local static singleton category.

## State and Persistence Behavior
There is no persistent state. The only state is the singleton static category object, initialized on first use. The file intentionally suppresses non-virtual-destructor diagnostics around Boost/category implementation details.

## Dependencies and Integration Points
It depends on `common/error_code.h`, `common/errno.h`, and `mon/error_code.h`. It integrates with any monitor code that returns `boost::system::error_code` or compares monitor errors to generic error conditions.

## Risks and Test Signals
Risks are mostly semantic: wrong sign conversion would break comparisons, and buffer-message truncation must stay NUL-terminated. Tests should cover `mon_category().name()`, zero/nonzero message strings, explicit `make_error_code()` behavior, equivalence with generic POSIX conditions, and conversion from negative errno values.
