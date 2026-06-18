## sources/cloud-native/moby/daemon/libnetwork/osl/netlinkutil_linux.go

Purpose: small Linux debug utility for formatting network device flags into readable names.

Important APIs/types/functions: `deviceFlags` type, `deviceFlagStrings` mapping from `unix.IFF_*` bits to names, and `deviceFlags.String`.

Control flow: `String` iterates over 32 bits, appends known flag names, accumulates unknown bits as a hex mask, and returns a `deviceFlags(...)` string joined by ` | `.

State and persistence behavior: stateless formatting.

Dependencies and integration points: used in `waitForIfUpped` logging to make netlink link update flags understandable. Depends on `golang.org/x/sys/unix`.

Risks: only checks 32 bits, which matches current flag width assumptions. Unknown flags are preserved as hex, preventing silent loss but not naming newer constants.

Test signals: no direct unit tests, but behavior is simple and used in debug logs during interface setup.
