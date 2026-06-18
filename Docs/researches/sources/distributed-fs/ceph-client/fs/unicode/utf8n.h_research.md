# sources/distributed-fs/ceph-client/fs/unicode/utf8n.h

`utf8n.h` is the internal header for Unicode normalization. It declares cursor APIs, table structures, and the generated data-table contract shared by `utf8-core.c`, `utf8-norm.c`, generated `utf8data.c`, and KUnit tests.

Declared APIs are `utf8version_is_supported()`, `utf8nlen()`, `utf8ncursor()`, and `utf8byte()`. `struct utf8cursor` stores the normalization map, normalization mode, active source pointer, decomposition pointer, saved scan positions, remaining lengths, current and next canonical combining class, and Hangul scratch bytes. `struct utf8data` maps a maximum Unicode age to a trie offset. `struct utf8data_table` references the age table, NFDICF and NFDI table arrays and sizes, and packed trie bytes. `utf8_data_table` is the exported generated table symbol.

The header is declarative; runtime flow is cursor initialization followed by repeated `utf8byte()` calls until NUL or error. Cursor state is transient and caller-owned, while `utf8data_table` is immutable module data. Dependencies include Linux types, export, string, module, and unicode headers. Risks are ABI drift between generator output and `struct utf8data_table`, cursor-field assumption changes, and normalization enum mismatches. Signals are compile-time compatibility, successful symbol resolution, KUnit tests, and filesystem normalization behavior.
