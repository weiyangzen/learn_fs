# sources/distributed-fs/ceph-client/scripts/ipe/polgen/polgen.c

## Purpose
Converts an optional plaintext IPE policy file into a generated C source file containing `const char *const ipe_boot_policy`.

## APIs, Control Flow, and State
`main()` requires an output path and optionally a policy input path. `policy_to_buffer()` opens the input, measures it with `fseek`/`ftell`, allocates an exact-size buffer, reads the file, and returns buffer plus length. `write_boot_policy()` writes a generated C file, includes `<linux/stddef.h>`, declares and defines `ipe_boot_policy`, emits `NULL` when no policy is supplied, or emits an escaped string literal. Escaping handles quotes, backslashes, tabs, question marks, and newlines by splitting the string across lines.

## Dependencies and Integration
It depends on libc file APIs and kernel headers for the generated C include. It integrates with IPE build logic that compiles the generated boot policy into the kernel.

## Risks and Test Signals
Risks include `ftell()` errors not being separately checked, text-mode I/O, partial-read failure returning `-1`, and generated C invalidity if unusual bytes are present. Test signals are successful generation for empty and non-empty policies, compilation of generated C, and byte-for-byte policy recovery from the escaped literal.
