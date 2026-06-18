## sources/distributed-fs/ceph-client/tools/lib/bpf/strset.c

Purpose: Implements a compact string set backed by contiguous NUL-terminated string data and a hashmap from string offset to itself.

Important APIs/functions: `strset__new()` optionally imports existing string data and indexes unique strings. `strset__add_str()` appends if unique and returns the offset. `strset__find_str()` returns an existing offset without committing the temporary appended bytes. `strset__data()` and `strset__data_size()` expose the packed data.

Control flow: Hash/equality callbacks interpret keys as offsets into `strs_data`. Adds temporarily copy the candidate string to the current end so the hashmap can compare by offset, then either return an existing offset or commit by increasing `strs_data_len`.

State/persistence: Heap-owned buffer and hashmap persist until `strset__free()`. Returned offsets are stable as long as the set lives, even if the backing buffer reallocates.

Dependencies/integration: Uses libbpf `hashmap`, `str_hash()`, and `libbpf_add_mem()` growth limits. Used by libbpf code needing BTF/string-table style deduplication.

Risks: Initial data must be a valid sequence of NUL-terminated strings; malformed data can walk past the buffer during `strlen`. `strset__find_str()` may grow capacity even on misses. Offset 0 is documented as found only by `>0`, but valid string tables often use offset 0 for empty string, so callers must interpret return values carefully.

Test signals: Cover duplicate import, duplicate add, max-size exhaustion, malformed init data, empty strings, offset stability after realloc, and `find` miss behavior.
