# sources/distributed-fs/ceph-client/tools/net/sunrpc/extract.sh

Purpose: Extracts embedded XDR protocol specification lines from RFC text.

Important APIs and functions: It is a stdin-to-stdout filter. It selects lines beginning with optional spaces followed by `///`, strips the marker and following space, and preserves empty marker lines.

Control flow: A single `grep '^ *///' | sed ... | sed ...` pipeline implements extraction.

State and persistence behavior: Stateless filter; no files are read except stdin or written except stdout.

Dependencies and integration points: Intended to produce `.x` XDR files for the SunRPC XDR generator from RFC documents using the convention described in RFC 8166.

Risks: Only lines using exactly the `///` convention are extracted. Leading spaces before markers are tolerated, but other comment styles are ignored.

Test signals: Feed RFC excerpts with `/// declaration`, `///` empty lines, indented markers, and non-marker text; verify only specification lines remain.
