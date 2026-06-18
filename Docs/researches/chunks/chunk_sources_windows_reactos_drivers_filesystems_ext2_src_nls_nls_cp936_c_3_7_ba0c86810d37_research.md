# Chunk Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_cp936.c lines 7885-11031

## Scope

This chunk covers the tail of ReactOS ext2's imported Linux `nls_cp936.c` CP936/GB2312 NLS module. Most of the chunk is generated Unicode-to-charset table data; the final section wires those tables into the Linux-style `struct nls_table` conversion API and module registration path.

## APIs and Entry Points

- `uni2char(const wchar_t uni, unsigned char *out, int boundlen)` converts one Unicode code point to CP936 bytes using `page_uni2charset`; it returns byte count `1` or `2`, or `-ENAMETOOLONG` / `-EINVAL` on failure (`10945-10974`).
- `char2uni(const unsigned char *rawstring, int boundlen, wchar_t *uni)` converts one CP936 input character to a Unicode code point using `page_charset2uni`; it returns consumed byte count `1` or `2`, or a negative error (`10976-11005`).
- `table` exposes charset name `"cp936"`, alias `"gb2312"`, conversion callbacks, case tables, and `THIS_MODULE` owner through the kernel NLS interface (`11007-11015`).
- `init_nls_cp936()` registers the NLS table with `register_nls(&table)` (`11017-11020`).
- `exit_nls_cp936()` unregisters it with `unregister_nls(&table)` (`11022-11025`).
- `module_init`, `module_exit`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS(gb2312)` declare kernel module lifecycle and metadata (`11027-11031`).

## Data and State

- The chunk starts in the final rows of `u2c_76` from the previous chunk and then defines Unicode page tables `u2c_77` through `u2c_9F`, plus sparse/special tables `u2c_DC`, `u2c_F9`, `u2c_FA`, `u2c_FE`, and `u2c_FF` (`7885-10836`). Each `u2c_*` table stores 512 bytes, two output bytes per Unicode low byte, with `0x00,0x00` marking unmapped characters.
- `page_uni2charset[256]` maps a Unicode high byte to the corresponding `u2c_*` table pointer or `NULL` when that Unicode page is unsupported (`10838-10871`). This array is the main dispatch table for `uni2char`.
- `charset2lower[256]` and `charset2upper[256]` are bytewise case-fold tables. They only fold ASCII letters (`A-Z` / `a-z`); all bytes `0x80-0xff` map to themselves (`10873-10943`).
- Module state is effectively static and read-only after load. There is no mutable runtime state in this chunk beyond NLS core registration/unregistration of the static `table`.

## Control Flow

- Unicode-to-CP936:
  - Rejects empty output capacity with `-ENAMETOOLONG` (`10953-10954`).
  - Splits `wchar_t uni` into high byte `ch` and low byte `cl` (`10949-10950`).
  - Looks up `page_uni2charset[ch]` (`10957`).
  - If a table exists, requires two output bytes, copies `uni2charset[cl*2]` and `[cl*2+1]`, rejects the zero pair as unmapped, and returns `2` (`10958-10965`).
  - If there is no table and the Unicode character is non-NUL ASCII (`ch == 0 && cl`), writes one byte and returns `1` (`10966-10968`).
  - Otherwise returns `-EINVAL` (`10970-10971`).
- CP936-to-Unicode:
  - Rejects zero/negative input length with `-ENAMETOOLONG` (`10983-10984`).
  - If only one byte is available, treats it as a single-byte character and returns it directly as Unicode (`10986-10988`).
  - With at least two bytes, uses first byte `ch` as the page index and second byte `cl` as the table offset (`10991-10996`).
  - If `page_charset2uni[ch]` exists and `cl` is nonzero, reads the mapped Unicode value, rejects `0x0000`, and returns `2` (`10994-10999`).
  - Otherwise it falls back to treating `ch` as a single-byte Unicode value and returns `1` (`11000-11003`).

## Dependencies

- Includes and kernel/NLS types are outside this chunk: `<linux/module.h>`, `<linux/kernel.h>`, `<linux/string.h>`, `<linux/nls.h>`, and `<linux/errno.h>` appear at file top (`10-14`).
- `page_charset2uni`, used by `char2uni`, is defined before this chunk from the `c2u_81` through `c2u_FE` tables (`4400-4433`); this chunk depends on that earlier generated decoder table block.
- `register_nls`, `unregister_nls`, `struct nls_table`, `THIS_MODULE`, `module_init`, `module_exit`, `MODULE_LICENSE`, and `MODULE_ALIAS_NLS` are kernel/module/NLS framework APIs.
- Error codes `ENAMETOOLONG` and `EINVAL` come from kernel errno definitions and are returned as negative values.

## Risks and Edge Cases

- `char2uni` returns a lone byte as Unicode whenever `boundlen == 1`, even if that byte is a CP936 lead byte. This is consistent with common Linux NLS table behavior but means truncated DBCS input is not rejected as malformed in this code path (`10986-10988`).
- `char2uni` also falls back to a one-byte character when the first byte has no `page_charset2uni` table or the second byte is zero (`10994-11003`). Invalid lead-byte sequences may therefore be consumed as one byte rather than producing `-EINVAL`.
- `uni2char` rejects Unicode NUL because the ASCII fallback requires `cl` to be nonzero and no table entry represents U+0000 (`10966-10971`).
- The generated tables are dense and manual review is impractical; correctness depends on generation from the Microsoft CP936 mapping source described in the file header (`1-7`). Sparse tables such as `u2c_DC`, `u2c_FE`, and `u2c_FF` intentionally contain many `0x00,0x00` unmapped slots (`10659-10661`, `10746-10836`).
- The lookup math `cl * 2` assumes every `u2c_*` table has 512 bytes. The declarations in this chunk follow that convention, including sparse tables that are declared `[512]` and implicitly zero-filled beyond listed initializers.

## Cross-Chunk References

- Previous chunks define the file header/import provenance, all charset-to-Unicode `c2u_*` decode tables, `page_charset2uni`, and the earlier Unicode-to-charset tables `u2c_01` through most of `u2c_76`.
- This chunk completes the Unicode-to-charset table family and defines `page_uni2charset`, so `uni2char` here depends on data spanning earlier chunks and this chunk.
- The final per-file report should merge this chunk with earlier chunks by treating the file as a generated bidirectional CP936 mapping module with only a small amount of handwritten control code at the end.