# sources/distributed-fs/openafs/src/tools/dumpscan/xf_printf.c

## Purpose
Provides formatted output for `XFILE` streams without depending entirely on platform `printf` behavior. It implements `xfprintf`/`vxfprintf` over `xfwrite`, including integer/string/float formatting, `%n`, and a custom `%I` IPv4 address or hostname formatter.

## Important APIs, Types, And Functions
Public functions are `xfprintf` and `vxfprintf`. Static helpers are `mkint` for base conversion and `wsp` for batched space padding. The formatter supports standard integer specifiers, `%c`, `%s`, `%%`, `%n`, floating formats through `sprintf`, and `%I` for network-byte-order IPv4 addresses. Constants include `SPBUFLEN` and `MAXPREC`.

## Control Flow
`vxfprintf` scans literal text until `%`, writes pending literals, parses flags, width, precision, and `h`/`l` modifiers, then converts the next argument into a temporary string or points at an existing string. Width padding is emitted before or after the payload depending on left justification. `%I` optionally performs `gethostbyaddr`; on success it prints the host name with optional case conversion and precision truncation, otherwise it renders a dotted quad with optional zero/space padding.

## State And Persistence
The only module-level state is `spbuf`, lazily filled with spaces. The function writes to the caller's `XFILE` and advances that stream through `xfwrite`; it does not persist formatting state between calls. `%n` mutates caller-provided count pointers, and `%I` may mutate the hostname string returned by resolver storage when applying case conversion.

## Dependencies And Integration Points
The formatter is used by other dumpscan xfile backends, notably `xf_profile.c`, and by any dumpscan code wanting formatted output to an `XFILE`. It depends on libc formatting for floats, resolver APIs, `netinet/in.h`, and the generic xfile write path.

## Risks And Test Signals
Important risks include unsafe float formatting through `sprintf` into fixed buffers, precision/width arithmetic underflow because widths are unsigned but later assigned to signed padding, missing positional-argument support by design, no pointer `%p`, possible mutation of resolver-owned host strings, and limited handling of long long values. Tests should cover all integer flags, precision caps, literal flushing after errors, `%n`, null strings, custom `%I` with and without reverse DNS, and write-error propagation from a failing `XFILE`.
