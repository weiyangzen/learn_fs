
# sources/distributed-fs/openafs/src/util/base32.c

Purpose: `base32.c` converts signed `int` values to and from a compact base-32 string using digits and uppercase letters.

Important APIs: `int_to_base32(b32_string_t s, int a)` writes a NUL-terminated representation to the caller-supplied eight-byte buffer and returns it. `base32_to_int(char *s)` parses a base-32 string back to an integer.

Control flow: encoding special-cases zero, handles the top two bits separately, then emits five-bit groups from the highest nonzero group down. Decoding shifts the accumulated result left five bits and adds each digit value, mapping `0`-`9` to 0-9 and anything above `9` as uppercase letters starting at 10.

State and persistence: only static translation string `c_xlate` is used; no persistent effects.

Dependencies and integration: included via `afsutil.h`; buffer type is declared there. Used by utility consumers needing compact IDs.

Risks: decoder does not validate input range or lowercase; characters such as punctuation above `'9'` produce unintended values. Signed `int` bit operations depend on implementation details for negative values, though masking uses unsigned temporaries. Test signals should include zero, high-bit values, round trips, invalid characters, lowercase input, and maximum output length.
