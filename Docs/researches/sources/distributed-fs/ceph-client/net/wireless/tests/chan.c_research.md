# sources/distributed-fs/ceph-client/net/wireless/tests/chan.c

## Purpose
`chan.c` contains KUnit coverage for cfg80211 channel-definition compatibility, especially 6 GHz channel widths up to 320 MHz and puncturing behavior.

## Important APIs, Types, And Functions
The file defines static 6 GHz channel fixtures, parameter table `chandef_compat_cases`, `test_chandef_compat()`, suite `chandef_compat`, and imports the KUnit-only symbol namespace. The tested production APIs are `cfg80211_chandef_valid()` and `cfg80211_chandef_compatible()`.

## Control Flow
Each parameterized case builds two `cfg80211_chan_def` values, substitutes `c2` for `c1` for identical-channel cases, asserts both chandefs are valid, then checks compatibility in both argument orders. Expected return is either the wider/compatible chandef pointer or `NULL`; identical cases also verify that reversing arguments returns the other identical object.

## State And Persistence
The tests use only static channel fixtures and parameter data. No state persists outside the KUnit invocation.

## Dependencies And Integration Points
The suite depends on cfg80211 channel helpers, KUnit parameter generation via `KUNIT_ARRAY_PARAM_DESC`, and the KUnit-exported production symbols. It is built into `cfg80211-tests.o` by the local Makefile.

## Risks And Edge Cases
The cases target compatibility regressions around primary-channel mismatch, bandwidth containment, 160 MHz inside 320 MHz, and punctured secondary segments. Pointer identity is part of the expected contract, so helper changes that return equivalent copies instead of original inputs would break this suite.

## Test Signals
Passing cases demonstrate that identical 20/no-HT/40/80/160/320 MHz definitions are compatible, 20 MHz can be compatible within 320 MHz, mismatched primary 20 or 320 MHz definitions are rejected, and puncturing masks are interpreted correctly for compatible and incompatible 160-in-320 scenarios.
