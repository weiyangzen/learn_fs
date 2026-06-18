# Research: sources/distributed-fs/openafs/src/platform/DARWIN/AFSPreference/NSString+search.h

Purpose: declares a small `NSString` category for extracting a substring delimited by start and end tokens.

Important API: `-estractTokenByDelimiter:endToken:` scans the receiver for an optional start token and required end token and returns the extracted substring.

Control flow and persistence: no persistence. The main known caller is `AFSCommanderPref unlog:`, which extracts a cell name from a token description line between `afs@` and a following space.

Dependencies and integration: imports Cocoa and extends all NSString instances in this bundle.

Risks: method name is misspelled. The contract does not specify behavior when delimiters are missing or repeated.

Test signals: token string with expected delimiters, missing start token, missing end token, multiple spaces, multiple `afs@` substrings, and empty receiver.
