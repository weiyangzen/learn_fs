## sources/distributed-fs/ceph-client/tools/lib/ctype.c

Purpose: Provides the kernel `_ctype` lookup table for tools code using Linux ctype macros.

Important APIs/types: Defines global `const unsigned char _ctype[]` with classification flags such as control, space, punctuation, digit, uppercase/lowercase, and hex.

Control flow: No executable flow; consumers index the table through `<linux/ctype.h>` macros.

State/persistence: Read-only global data.

Dependencies/integration: Includes Linux ctype/compiler headers. Supports tools code that wants kernel-compatible character classification without libc ctype locale behavior.

Risks: Classification is fixed and ASCII-oriented. Values above 127 are classified according to this table, not locale. Table length/order must match kernel macro expectations.

Test signals: Unit tests should compare digits, hex letters, spaces, punctuation, control characters, and high-bit bytes against expected Linux macro behavior.
