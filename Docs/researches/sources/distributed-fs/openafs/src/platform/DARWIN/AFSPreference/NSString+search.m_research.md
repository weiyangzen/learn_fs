# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/NSString+search.m

Purpose: implements the delimiter-extraction category used for token parsing.

Important APIs and control flow: creates an `NSScanner` over `self`, optionally scans up to `startToken`, scans up to `endTk` into `result`, and strips the start token length from the front if a start token was supplied.

State and persistence: stateless string utility.

Dependencies and integration: used by `AFSCommanderPref` to derive a cell name from a token row before invoking `unlog -c`.

Risks: if `startToken` is absent, `result` may not contain the expected prefix and `substringFromIndex:` can raise. If `endTk` is absent, the method returns nil. The method does not advance past the start token explicitly, so scanner behavior is fragile.

Test signals: expected token row format, absent delimiters, short strings that trigger substring bounds issues, nil end token, and token rows with trailing punctuation.
